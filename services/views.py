from django.shortcuts import render
from .models import Service

def home(request):
    services = Service.objects.all()
    return render(request, 'index.html', {'services': services})

def services(request):
    services = Service.objects.all()
    return render(request, 'service.html', {'services': services})
def about_view(request):
    return render(request, 'about.html')
def price_view(request):
    return render(request, 'price.html')

def about_view(request):
    return render(request, 'about.html')

def location_view(request):
    return render(request, 'location.html')
