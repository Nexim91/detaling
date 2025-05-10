from django.urls import path
from . import views

urlpatterns = [
    path('', views.booking_view, name='booking'),
    path('contacts/', views.contacts_view, name='contacts'),
]
