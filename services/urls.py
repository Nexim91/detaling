from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('index.html', views.home, name='home_index'),
    path('service.html', views.services, name='service_html'),
    path('price.html', views.price_view, name='price'),
    path('about.html', views.about_view, name='about'),
    path('location.html', views.location_view, name='location'),
    path('single.html', views.single_view, name='single'),
    path('team.html', views.team_view, name='team'),
    path('booking.html', views.booking_page_view, name='booking_page'),
    path('blog.html', views.blog_view, name='blog'),
    path('contact.html', views.contact_view, name='contact_html'),

    
]
