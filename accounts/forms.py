from django import forms
from .models import UserProfile, Car, CarStay

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'phone', 'email']

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['make', 'model', 'year', 'color', 'notes']

class CarStayForm(forms.ModelForm):
    class Meta:
        model = CarStay
        fields = ['check_in_date', 'check_out_date', 'status']
        widgets = {
            'check_in_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'check_out_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
