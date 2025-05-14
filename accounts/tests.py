import os
import django
from django.test import TestCase
from django.contrib.auth.models import User

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'detailing_project.settings')
django.setup()

class AccountsTests(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(username='testuser', password='12345')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('12345'))
