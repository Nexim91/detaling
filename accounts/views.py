from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Car, CarStay
from .forms import UserProfileForm, CarForm, CarStayForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from accounts.forms_new import UserRegistrationForm
from django.utils.timezone import now
from collections import Counter
from datetime import timedelta

@login_required
def profile_view(request):
    user = request.user
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=user)
        profile.save()
    cars = profile.cars.all()

    # Пример данных для дашборда
    # История услуг по датам (например, количество услуг в каждый месяц)
    stays = CarStay.objects.filter(car__user_profile=profile).order_by('check_in_date')
    service_dates = [stay.check_in_date.strftime('%Y-%m') for stay in stays]
    service_counts = Counter(service_dates)
    sorted_dates = sorted(service_counts.keys())
    service_history_dates = sorted_dates
    service_history_counts = [service_counts[date] for date in sorted_dates]

    # Пример напоминаний (можно расширить логику)
    reminders = []
    for stay in stays:
        if stay.check_in_date + timedelta(days=180) < now().date():
            reminders.append(f"Рекомендуется повторная химчистка для автомобиля {stay.car.make} {stay.car.model} ({stay.car.license_plate})")

    # Пример текущих заказов (статус "в работе")
    current_orders = []
    for stay in stays.filter(status='in_progress'):
        current_orders.append({
            'status': 'В работе',
            'service_name': stay.service_name,
            'date': stay.check_in_date.strftime('%d.%m.%Y')
        })

    context = {
        'profile': profile,
        'cars': cars,
        'reminders': reminders,
        'current_orders': current_orders,
        'service_history_dates': service_history_dates,
        'service_history_counts': service_history_counts,
    }
    return render(request, 'accounts/profile.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('accounts:profile')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def edit_profile(request):
    user = request.user
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'accounts/edit_profile.html', {'form': form})

@login_required
def car_list(request):
    profile = request.user.profile
    cars = profile.cars.all()
    return render(request, 'accounts/car_list.html', {'cars': cars})

@login_required
def add_car(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = CarForm(request.POST)
        if form.is_valid():
            car = form.save(commit=False)
            car.user_profile = profile
            car.save()
            return redirect('accounts:car_list')
    else:
        form = CarForm()
    return render(request, 'accounts/add_car.html', {'form': form})

@login_required
def edit_car(request, car_id):
    profile = request.user.profile
    car = get_object_or_404(Car, id=car_id, user_profile=profile)
    if request.method == 'POST':
        form = CarForm(request.POST, instance=car)
        if form.is_valid():
            form.save()
            return redirect('accounts:car_list')
    else:
        form = CarForm(instance=car)
    return render(request, 'accounts/edit_car.html', {'form': form})

@login_required
def car_stay_history(request, car_id):
    profile = request.user.profile
    car = get_object_or_404(Car, id=car_id, user_profile=profile)
    stays = car.stays.all().order_by('-check_in_date')
    return render(request, 'accounts/car_stay_history.html', {'car': car, 'stays': stays})

@login_required
def add_car_stay(request, car_id):
    profile = request.user.profile
    car = get_object_or_404(Car, id=car_id, user_profile=profile)
    if request.method == 'POST':
        form = CarStayForm(request.POST)
        if form.is_valid():
            stay = form.save(commit=False)
            stay.car = car
            stay.save()
            return redirect('accounts:car_stay_history', car_id=car.id)
    else:
        form = CarStayForm()
    return render(request, 'accounts/add_car_stay.html', {'form': form, 'car': car})
