from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from pricing.models import Service
from .models import Cart, CartItem, Order, OrderItem
from bot.telegram import send_telegram_message
from django.conf import settings

@login_required
def add_to_cart(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, service=service)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f'Услуга "{service.name}" добавлена в корзину.')
    return redirect('cart:view_cart')

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    return render(request, 'cart/view_cart.html', {'cart': cart, 'items': items})

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    items = cart.items.all()
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
            message_lines = [
                f"Новый заказ #{order.id} от пользователя {request.user.username} ({request.user.email}):"
            ]
            for item in items:
                message_lines.append(f"- {item.service.name} x {item.quantity}")
            message = "\n".join(message_lines)
            send_telegram_message(telegram_token, telegram_chat_id, message)

        return redirect('cart:order_success', order_id=order.id)
    return render(request, 'cart/checkout.html', {'cart': cart, 'items': items})

@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'cart/order_success.html', {'order': order})
