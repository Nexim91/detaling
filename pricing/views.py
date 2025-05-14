from django.shortcuts import render
from .models import Service
from collections import defaultdict

def price_uslugi_view(request):
    services = Service.objects.all()
    services_by_category = defaultdict(list)
    for service in services:
        services_by_category[service.category.name].append(service)
    categories = [{'name': cat, 'services': servs} for cat, servs in services_by_category.items()]
    return render(request, 'pricing/price_uslugi.html', {'categories': categories})

def test_page(request):
    return render(request, 'pricing/test_page.html')
