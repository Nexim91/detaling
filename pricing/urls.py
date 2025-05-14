from django.urls import path
from . import views

app_name = 'pricing'

urlpatterns = [
    path('price_uslugi/', views.price_uslugi_view, name='price_uslugi'),
    path('test/', views.test_page, name='test_page'),
]
