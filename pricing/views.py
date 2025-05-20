from django.shortcuts import render
from .models import Category, Service
def price_uslugi_view(request):
    categories = Category.objects.prefetch_related('services').all()
    no_category_services = Service.objects.filter(category__isnull=True)
    cart_count = 0
    if request.user.is_authenticated:
        from cart.models import Cart
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_count = cart.items.count()
    return render(request, 'pricing/price_uslugi.html', {
        'categories': categories,
        'no_category_services': no_category_services,
        'cart_count': cart_count,
    })

def test_page(request):
    return render(request, 'pricing/test_page.html')
