from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField("Имя", max_length=30)
    last_name = models.CharField("Фамилия", max_length=30)
    phone = models.CharField("Телефон", max_length=20, blank=True, null=True)
    email = models.EmailField("Email", blank=True, null=True)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

class Car(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='cars')
    make = models.CharField("Марка", max_length=50)
    model = models.CharField("Модель", max_length=50)
    year = models.PositiveIntegerField("Год выпуска")
    license_plate = models.CharField("Госномер", max_length=20)
    notes = models.TextField("Примечания", blank=True, null=True)

    def __str__(self):
        return f"{self.make} {self.model} ({self.license_plate})"

class CarStay(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='stays')
    check_in_date = models.DateTimeField("Дата заезда")
    check_out_date = models.DateTimeField("Дата выезда", blank=True, null=True)
    status = models.CharField("Статус", max_length=50)

    def __str__(self):
        return f"{self.car} - {self.status} с {self.check_in_date} по {self.check_out_date if self.check_out_date else '...'}"
