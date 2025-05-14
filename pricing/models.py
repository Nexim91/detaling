from django.db import models

class Service(models.Model):
    SERVICE_CATEGORIES = [
        ('detailing', 'Детейлинг'),
        ('polishing', 'Полировка'),
    ]

    name = models.CharField("Название услуги", max_length=100)
    category = models.CharField("Категория", max_length=50, choices=SERVICE_CATEGORIES)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    duration = models.DurationField("Длительность услуги")
    description = models.TextField("Описание", blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_category_display()}) - {self.price} руб."

# Пример готовых услуг и цен для наполнения базы данных
def create_sample_services():
    from datetime import timedelta
    services = [
        Service(name="Полировка кузова", category="polishing", price=15000.00, duration=timedelta(hours=3), description="Профессиональная полировка кузова автомобиля для восстановления блеска и защиты."),
        Service(name="Детейлинг салона", category="detailing", price=8000.00, duration=timedelta(hours=2), description="Глубокая чистка и уход за интерьером автомобиля."),
        Service(name="Комплексный детейлинг", category="detailing", price=20000.00, duration=timedelta(hours=5), description="Полный комплекс услуг по детейлингу кузова и салона."),
        Service(name="Химчистка салона", category="detailing", price=10000.00, duration=timedelta(hours=3), description="Глубокая химчистка всех поверхностей салона."),
        Service(name="Нанокерамика кузова", category="detailing", price=25000.00, duration=timedelta(hours=6), description="Защита кузова нанокерамическим покрытием."),
        Service(name="Полировка фар", category="polishing", price=5000.00, duration=timedelta(hours=1), description="Восстановление прозрачности фар."),
        Service(name="Защита кузова пленкой", category="detailing", price=30000.00, duration=timedelta(hours=8), description="Нанесение защитной пленки на кузов."),
        Service(name="Мойка двигателя", category="detailing", price=4000.00, duration=timedelta(hours=1), description="Профессиональная мойка двигателя."),
        Service(name="Полировка дисков", category="polishing", price=7000.00, duration=timedelta(hours=2), description="Восстановление блеска дисков."),
        Service(name="Уход за кожаным салоном", category="detailing", price=6000.00, duration=timedelta(hours=2), description="Чистка и кондиционирование кожаных поверхностей."),
        Service(name="Удаление запахов", category="detailing", price=3500.00, duration=timedelta(hours=1), description="Удаление неприятных запахов из салона."),
        Service(name="Полировка кузова с воском", category="polishing", price=18000.00, duration=timedelta(hours=4), description="Полировка кузова с нанесением воска."),
        Service(name="Обработка стекол", category="detailing", price=4500.00, duration=timedelta(hours=1), description="Нанесение водоотталкивающего покрытия на стекла."),
        Service(name="Чистка ковров", category="detailing", price=3000.00, duration=timedelta(hours=1), description="Глубокая чистка ковровых покрытий."),
        Service(name="Полировка кузова с защитой", category="polishing", price=22000.00, duration=timedelta(hours=5), description="Полировка кузова с нанесением защитного покрытия."),
    ]
    for service in services:
        service.save()
