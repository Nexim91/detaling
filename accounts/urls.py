from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('cars/', views.car_list, name='car_list'),
    path('cars/add/', views.add_car, name='add_car'),
    path('cars/<int:car_id>/edit/', views.edit_car, name='edit_car'),
    path('cars/<int:car_id>/stays/', views.car_stay_history, name='car_stay_history'),
    path('cars/<int:car_id>/stays/add/', views.add_car_stay, name='add_car_stay'),
    path('register/', views.register, name='register'),
]
