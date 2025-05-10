from django.db import models
from services.models import Service

class Booking(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    client_name = models.CharField("Имя", max_length=100)
    phone = models.CharField("Телефон", max_length=20)
    car_model = models.CharField("Модель авто", max_length=50)
    date = models.DateField("Дата")
    time = models.TimeField("Время")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client_name} — {self.service.name}"