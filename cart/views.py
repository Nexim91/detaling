from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from pricing.models import Service
from .models import Cart, CartItem, Order, OrderItem
from bot.telegram import send_telegram_message
from django.conf import settings
from django.http import JsonResponse

@login_required
def add_to_cart(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, service=service)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f'Услуга "{service.name}" добавлена в корзину.')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('cart:view_cart')

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    if request.method == 'POST':
        # Удаление позиции
        if 'remove' in request.POST:
            item_id = request.POST.get('remove')
            CartItem.objects.filter(id=item_id, cart=cart).delete()
        # Обновление количества
        elif 'update' in request.POST:
            for item in items:
                qty = request.POST.get(f'quantity_{item.id}')
                if qty is not None:
                    try:
                        qty = int(qty)
                        if qty > 0:
                            item.quantity = qty
                            item.save()
                    except ValueError:
                        pass
        # После изменений обновляем список items
        items = cart.items.all()
    # Добавляем line_total для каждого item и общий cart_total
    cart_total = 0
    for item in items:
        item.line_total = item.service.price * item.quantity
        cart_total += item.line_total
    return render(request, 'cart/view_cart.html', {'cart': cart, 'items': items, 'cart_total': cart_total})

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    items = cart.items.all()
    # Добавляем line_total для каждого item и общий cart_total
    cart_total = 0
    for item in items:
        item.line_total = item.service.price * item.quantity
        cart_total += item.line_total
    if request.method == 'POST':
        order = Order.objects.create(user=request.user)
        # Save order before creating order items
        order.save()
        for item in items:
            OrderItem.objects.create(order=order, service=item.service, quantity=item.quantity)
        cart.items.all().delete()

        # Send Telegram notification to owner
        telegram_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        telegram_chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)
        if telegram_token and telegram_chat_id:
            # Получаем профиль пользователя и машины
            user_profile = getattr(request.user, 'profile', None)
            phone = user_profile.phone if user_profile else 'Не указан'
            cars = user_profile.cars.all() if user_profile else []

            message_lines = [
                f"Новый заказ #{order.id} от пользователя {request.user.username} ({request.user.email}):",
                f"Телефон: {phone}",
                "Машины пользователя:"
            ]
            if cars:
                for car in cars:
                    message_lines.append(f"- {car.make} {car.model} ({car.license_plate})")
            else:
                message_lines.append("Нет данных о машинах")

            for item in items:
                message_lines.append(f"- {item.service.name} x {item.quantity}")
            message = "\n".join(message_lines)
            send_telegram_message(telegram_token, telegram_chat_id, message)

        return redirect('cart:order_success', order_id=order.id)
    return render(request, 'cart/checkout.html', {'cart': cart, 'items': items, 'cart_total': cart_total})

@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'cart/order_success.html', {'order': order})
