from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Car, CarStay

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=False, max_length=20, label="Телефон")

    class Meta:
        model = User
        fields = ("username", "email", "phone", "password1", "password2")

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            # Сохраняем телефон в связанную модель UserProfile
            phone = self.cleaned_data.get("phone")
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.phone = phone
            profile.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'phone', 'email']

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['make', 'model', 'year', 'license_plate', 'notes']

class CarStayForm(forms.ModelForm):
    class Meta:
        model = CarStay
        fields = ['check_in_date', 'check_out_date', 'status']
        widgets = {
            'check_in_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'check_out_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
