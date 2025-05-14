from django.core.management.base import BaseCommand
from pricing.models import Category, Service

class Command(BaseCommand):
    help = 'Populate the database with sample categories and services with prices adjusted for Kaluga and Kaluga region'

    def handle(self, *args, **kwargs):
        categories = {
            "Детейлинг": [
                {"name": "Детейлинг салона", "price": 8500.00, "duration": "2 часа", "description": "Глубокая чистка и уход за интерьером автомобиля."},
                {"name": "Комплексный детейлинг", "price": 21000.00, "duration": "5 часов", "description": "Полный комплекс услуг по детейлингу кузова и салона."},
                {"name": "Химчистка салона", "price": 10500.00, "duration": "3 часа", "description": "Глубокая химчистка всех поверхностей салона."},
                {"name": "Нанокерамика кузова", "price": 26000.00, "duration": "6 часов", "description": "Защита кузова нанокерамическим покрытием."},
                {"name": "Защита кузова пленкой", "price": 31000.00, "duration": "8 часов", "description": "Нанесение защитной пленки на кузов."},
                {"name": "Мойка двигателя", "price": 4200.00, "duration": "1 час", "description": "Профессиональная мойка двигателя."},
                {"name": "Уход за кожаным салоном", "price": 6300.00, "duration": "2 часа", "description": "Чистка и кондиционирование кожаных поверхностей."},
                {"name": "Удаление запахов", "price": 3700.00, "duration": "1 час", "description": "Удаление неприятных запахов из салона."},
                {"name": "Обработка стекол", "price": 4700.00, "duration": "1 час", "description": "Нанесение водоотталкивающего покрытия на стекла."},
                {"name": "Чистка ковров", "price": 3200.00, "duration": "1 час", "description": "Глубокая чистка ковровых покрытий."},
                {"name": "Полировка сидений", "price": 3700.00, "duration": "1 час", "description": "Полировка и уход за сиденьями автомобиля."},
                {"name": "Очистка стекол", "price": 2100.00, "duration": "30 минут", "description": "Очистка и полировка стекол автомобиля."},
                {"name": "Чистка колесных арок", "price": 2700.00, "duration": "45 минут", "description": "Удаление грязи и пыли из колесных арок."},
            ],
            "Полировка": [
                {"name": "Полировка кузова", "price": 16000.00, "duration": "3 часа", "description": "Профессиональная полировка кузова автомобиля для восстановления блеска и защиты."},
                {"name": "Полировка фар", "price": 5300.00, "duration": "1 час", "description": "Восстановление прозрачности фар."},
                {"name": "Полировка дисков", "price": 7400.00, "duration": "2 часа", "description": "Восстановление блеска дисков."},
                {"name": "Полировка кузова с воском", "price": 19000.00, "duration": "4 часа", "description": "Полировка кузова с нанесением воска."},
                {"name": "Полировка кузова с защитой", "price": 23000.00, "duration": "5 часов", "description": "Полировка кузова с нанесением защитного покрытия."},
                {"name": "Полировка зеркал", "price": 3200.00, "duration": "1 час", "description": "Полировка боковых зеркал автомобиля."},
                {"name": "Полировка хромированных деталей", "price": 4300.00, "duration": "1.5 часа", "description": "Полировка и защита хромированных элементов."},
            ],
            "Покраска": [
                {"name": "Покраска кузова", "price": 32000.00, "duration": "8 часов", "description": "Профессиональная покраска кузова автомобиля."},
                {"name": "Локальная покраска", "price": 16000.00, "duration": "4 часа", "description": "Покраска отдельных участков кузова."},
                {"name": "Покраска бампера", "price": 8500.00, "duration": "2 часа", "description": "Покраска переднего или заднего бампера."},
                {"name": "Покраска дисков", "price": 7400.00, "duration": "3 часа", "description": "Покраска автомобильных дисков."},
                {"name": "Покраска дверей", "price": 13000.00, "duration": "5 часов", "description": "Покраска дверей автомобиля."},
                {"name": "Покраска капота", "price": 11000.00, "duration": "4 часа", "description": "Покраска капота автомобиля."},
                {"name": "Покраска крыши", "price": 11500.00, "duration": "4.5 часа", "description": "Покраска крыши автомобиля."},
            ],
            "Тонировка": [
                {"name": "Тонировка стекол", "price": 7500.00, "duration": "2 часа", "description": "Нанесение тонировочной пленки на стекла автомобиля."},
                {"name": "Снятие тонировки", "price": 3200.00, "duration": "1 час", "description": "Удаление старой тонировочной пленки."},
                {"name": "Тонировка фар", "price": 5300.00, "duration": "1.5 часа", "description": "Тонировка автомобильных фар."},
                {"name": "Тонировка задних стекол", "price": 7000.00, "duration": "2 часа", "description": "Нанесение тонировочной пленки на задние стекла автомобиля."},
                {"name": "Тонировка лобового стекла", "price": 8500.00, "duration": "2.5 часа", "description": "Нанесение тонировочной пленки на лобовое стекло автомобиля."},
                {"name": "Тонировка боковых стекол", "price": 8000.00, "duration": "2 часа", "description": "Нанесение тонировочной пленки на боковые стекла автомобиля."},
                {"name": "Тонировка фар с защитой", "price": 5800.00, "duration": "1.5 часа", "description": "Тонировка фар с дополнительным защитным покрытием."},
                {"name": "Удаление тонировки с фар", "price": 3700.00, "duration": "1 час", "description": "Удаление старой тонировочной пленки с фар."},
            ],
            "Восстановление пластика": [
                {"name": "Восстановление пластиковых деталей", "price": 8500.00, "duration": "3 часа", "description": "Ремонт и восстановление пластиковых элементов салона и кузова."},
                {"name": "Покраска пластиковых деталей", "price": 6300.00, "duration": "2 часа", "description": "Покраска и обновление пластиковых поверхностей."},
                {"name": "Полировка пластиковых деталей", "price": 4200.00, "duration": "1.5 часа", "description": "Полировка и восстановление блеска пластиковых элементов."},
                {"name": "Ремонт пластиковых бамперов", "price": 9500.00, "duration": "3.5 часа", "description": "Ремонт и восстановление пластиковых бамперов автомобиля."},
                {"name": "Восстановление пластиковых накладок", "price": 7300.00, "duration": "2.5 часа", "description": "Ремонт и восстановление пластиковых накладок на кузове."},
                {"name": "Обновление пластиковых панелей", "price": 6800.00, "duration": "2 часа", "description": "Обновление и восстановление пластиковых панелей салона."},
                {"name": "Удаление царапин с пластика", "price": 3700.00, "duration": "1 час", "description": "Удаление мелких царапин и повреждений с пластиковых поверхностей."},
            ],
        }

        for category_name, services in categories.items():
            category, created = Category.objects.get_or_create(name=category_name)
            for service_data in services:
                service, created = Service.objects.get_or_create(
                    name=service_data["name"],
                    category=category,
                    defaults={
                        "price": service_data["price"],
                        "duration": service_data["duration"],
                        "description": service_data["description"],
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Service "{service.name}" created in category "{category.name}".'))
                else:
                    self.stdout.write(self.style.WARNING(f'Service "{service.name}" already exists in category "{category.name}".'))
