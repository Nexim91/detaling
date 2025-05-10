from django.db import models

class Service(models.Model):
    name = models.CharField("Название", max_length=100)
    category = models.CharField("Категория", max_length=50)
    price = models.CharField("Цена", max_length=50)
    duration = models.CharField("Срок", max_length=50)
    description = models.TextField("Описание", blank=True)

    def __str__(self):
        return self.name