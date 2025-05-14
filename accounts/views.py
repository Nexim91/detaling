from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Car, CarStay
from .forms import UserProfileForm, CarForm, CarStayForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from accounts.forms_new import UserRegistrationForm

@login_required
def profile_view(request):
    user = request.user
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=user)
        profile.save()
    cars = profile.cars.all()
    return render(request, 'accounts/profile.html', {'profile': profile, 'cars': cars})

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
