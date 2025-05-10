from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('index.html', views.home, name='home_index'),
    path('service/', views.services, name='service'),
    path('service.html', views.services, name='service_html'),
    path('price.html', views.price_view, name='price'),
    path('about.html', views.about_view, name='about'),
    path('location.html', views.location_view, name='location'),

]
