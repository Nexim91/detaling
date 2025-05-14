from django.shortcuts import render, redirect
from .models import Service

def home(request):
    services = Service.objects.all()
    return render(request, 'index.html', {'services': services})

def services(request):
    services = Service.objects.all()
    return render(request, 'service.html')

def about_view(request):
    return render(request, 'about.html')

def price_view(request):
    return render(request, 'price.html')

def location_view(request):
    return render(request, 'location.html')

def single_view(request):
    return render(request, 'single.html')

def team_view(request):
    return render(request, 'team.html')

def booking_page_view(request):
    return render(request, 'booking.html')

def blog_view(request):
    return render(request, 'blog.html')

def contact_view(request):
    return render(request, 'contact.html')

def redirect_to_pricing(request):
    return redirect('pricing:price_uslugi')



