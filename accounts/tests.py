from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import UserProfile, Car, CarStay
from accounts.forms import UserProfileForm, CarForm, CarStayForm
from datetime import date

class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.profile = UserProfile.objects.create(
            user=self.user,
            first_name='Иван',
            last_name='Иванов',
            phone='1234567890',
            email='ivan@example.com'
        )

    def test_profile_str(self):
        self.assertEqual(str(self.profile), 'Иванов Иван')

class CarModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.profile = UserProfile.objects.create(user=self.user)
        self.car = Car.objects.create(
            user_profile=self.profile,
            make='Toyota',
            model='Camry',
            year=2020,
            license_plate='A123BC'
        )

    def test_car_str(self):
        self.assertEqual(str(self.car), 'Toyota Camry (A123BC)')

class CarStayModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.profile = UserProfile.objects.create(user=self.user)
        self.car = Car.objects.create(user_profile=self.profile, make='Toyota', model='Camry', year=2020, license_plate='A123BC')
        self.stay = CarStay.objects.create(
            car=self.car,
            check_in_date=date.today(),
            status='active'
        )

    def test_stay_str(self):
        self.assertIn(str(self.stay.check_in_date), str(self.stay))

class UserProfileFormTest(TestCase):
    def test_valid_form(self):
        data = {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'phone': '1234567890',
            'email': 'ivan@example.com'
        }
        form = UserProfileForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        data = {
            'first_name': '',
            'last_name': 'Иванов',
            'phone': '1234567890',
            'email': 'ivan@example.com'
        }
        form = UserProfileForm(data=data)
        self.assertFalse(form.is_valid())

class CarFormTest(TestCase):
    def test_valid_form(self):
        data = {
            'make': 'Toyota',
            'model': 'Camry',
            'year': 2020,
            'license_plate': 'A123BC'
        }
        form = CarForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        data = {
            'make': '',
            'model': 'Camry',
            'year': 2020,
            'license_plate': 'A123BC'
        }
        form = CarForm(data=data)
        self.assertFalse(form.is_valid())

class CarStayFormTest(TestCase):
    def test_valid_form(self):
        data = {
            'check_in_date': '2025-01-01',
            'check_out_date': '2025-01-10',
            'status': 'active'
        }
        form = CarStayForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        data = {
            'check_in_date': '',
            'check_out_date': '2025-01-10',
            'status': 'active'
        }
        form = CarStayForm(data=data)
        self.assertFalse(form.is_valid())

class AccountsViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.profile = UserProfile.objects.create(user=self.user)

    def test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_profile_view_requires_login(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertRedirects(response, '/accounts/login/?next=/accounts/profile/')

        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)

    def test_edit_profile_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('accounts:edit_profile'))
        self.assertEqual(response.status_code, 200)

    def test_car_list_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('accounts:car_list'))
        self.assertEqual(response.status_code, 200)

    def test_add_car_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('accounts:add_car'))
        self.assertEqual(response.status_code, 200)

    def test_edit_car_view(self):
        self.client.login(username='testuser', password='12345')
        car = Car.objects.create(user_profile=self.profile, make='Toyota', model='Camry', year=2020, license_plate='A123BC')
        response = self.client.get(reverse('accounts:edit_car', args=[car.id]))
        self.assertEqual(response.status_code, 200)

    def test_car_stay_history_view(self):
        self.client.login(username='testuser', password='12345')
        car = Car.objects.create(user_profile=self.profile, make='Toyota', model='Camry', year=2020, license_plate='A123BC')
        response = self.client.get(reverse('accounts:car_stay_history', args=[car.id]))
        self.assertEqual(response.status_code, 200)

    def test_add_car_stay_view(self):
        self.client.login(username='testuser', password='12345')
        car = Car.objects.create(user_profile=self.profile, make='Toyota', model='Camry', year=2020, license_plate='A123BC')
        response = self.client.get(reverse('accounts:add_car_stay', args=[car.id]))
        self.assertEqual(response.status_code, 200)
