from django.shortcuts import render
from .models import Service

def price_uslugi_view(request):
    services = Service.objects.all()
    return render(request, 'pricing/price_uslugi.html', {'services': services})

def test_page(request):
    return render(request, 'pricing/test_page.html')
