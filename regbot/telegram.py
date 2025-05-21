import requests
from django.conf import settings
from django.contrib.auth.models import User
from accounts.models import UserProfile, Car
from accounts.forms_new import UserRegistrationForm
from pricing.models import Service, Category

REGBOT_TELEGRAM_BOT_TOKEN = settings.REGBOT_TELEGRAM_BOT_TOKEN
REGBOT_TELEGRAM_API_URL = f"https://api.telegram.org/bot{REGBOT_TELEGRAM_BOT_TOKEN}"

user_states = {}
user_carts = {}

def send_message(chat_id, text, reply_markup=None):
    url = f"{REGBOT_TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(url, json=payload)

import logging
logger = logging.getLogger(__name__)

def build_categories_keyboard(categories):
    keyboard = []
    row = []
    for idx, category in enumerate(categories, 1):
        row.append({"text": category.name, "callback_data": f"category_{category.id}"})
        if idx % 3 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return {"inline_keyboard": keyboard}

def build_services_keyboard(services):
    keyboard = []
    for service in services:
        keyboard.append([{"text": f"{service.name} - {service.price} руб.", "callback_data": f"add_{service.id}"}])
    keyboard.append([{"text": "Просмотреть корзину", "callback_data": "view_cart"}])
    keyboard.append([{"text": "Назад к категориям", "callback_data": "back_to_categories"}])
    keyboard.append([{"text": "В меню", "callback_data": "menu"}])
    return {"inline_keyboard": keyboard}

def build_cart_keyboard(cart_items):
    keyboard = []
    for idx, item in enumerate(cart_items):
        keyboard.append([{"text": f"Удалить {item['name']}", "callback_data": f"remove_{idx}"}])
    keyboard.append([{"text": "Оформить заказ", "callback_data": "checkout"}])
    keyboard.append([{"text": "Вернуться в меню", "callback_data": "menu"}])
    return {"inline_keyboard": keyboard}

def handle_update(update):
    logger.info(f"Received update: {update}")
    message = update.get("message")
    callback_query = update.get("callback_query")

    if callback_query:
        chat_id = callback_query["message"]["chat"]["id"]
        data = callback_query["data"]

        if data.startswith("category_"):
            category_id = int(data[len("category_"):])
            try:
                category = Category.objects.get(id=category_id)
                services = category.services.all()
                keyboard = build_services_keyboard(services)
                send_message(chat_id, f"Услуги категории {category.name}:", reply_markup=keyboard)
            except Category.DoesNotExist:
                send_message(chat_id, "Категория не найдена.")
            return

        if data.startswith("add_"):
            service_id = int(data.split("_")[1])
            try:
                service = Service.objects.get(id=service_id)
                cart = user_carts.setdefault(chat_id, [])
                cart.append({"id": service.id, "name": service.name, "price": service.price})
                send_message(chat_id, f"Услуга '{service.name}' добавлена в корзину.")
            except Service.DoesNotExist:
                send_message(chat_id, "Услуга с таким номером не найдена.")
            return

        if data == "view_cart":
            cart = user_carts.get(chat_id, [])
            if not cart:
                send_message(chat_id, "Ваша корзина пуста.")
            else:
                text = "Ваша корзина:\n"
                total = 0
                for item in cart:
                    text += f"{item['name']} - {item['price']} руб.\n"
                    total += item['price']
                text += f"Итого: {total} руб."
                keyboard = build_cart_keyboard(cart)
                send_message(chat_id, text, reply_markup=keyboard)
            return

        if data.startswith("remove_"):
            idx = int(data.split("_")[1])
            cart = user_carts.get(chat_id, [])
            if 0 <= idx < len(cart):
                removed_item = cart.pop(idx)
                send_message(chat_id, f"Удалена услуга '{removed_item['name']}' из корзины.")
            else:
                send_message(chat_id, "Неверный индекс для удаления.")
            return

        if data == "checkout":
            cart = user_carts.get(chat_id, [])
            if not cart:
                send_message(chat_id, "Ваша корзина пуста.")
            else:
                from bot.telegram import send_telegram_message
                from django.conf import settings
                from cart.models import Order, OrderItem
                from django.contrib.auth.models import User

                # Получаем пользователя Django по chat_id (нужно связать chat_id с user)
                try:
                    profile = UserProfile.objects.get(chat_id=chat_id)
                    user = profile.user
                except UserProfile.DoesNotExist:
                    user = None

                if user is None:
                    send_message(chat_id, "Пользователь не найден. Пожалуйста, зарегистрируйтесь.")
                    return

                # Создаем заказ
                order = Order.objects.create(user=user)

                # Добавляем позиции заказа
                for item in cart:
                    service_id = item['id']
                    quantity = 1  # Можно расширить для учета количества
                    service = Service.objects.get(id=service_id)
                    OrderItem.objects.create(order=order, service=service, quantity=quantity)

                # Получаем профиль пользователя
                try:
                    profile = UserProfile.objects.get(user=user)
                except UserProfile.DoesNotExist:
                    profile = None

                # Получаем машины пользователя
                cars = Car.objects.filter(user_profile=profile) if profile else []

                # Формируем текст уведомления
                order_details = f"Новый заказ #{order.id} от пользователя {user.get_full_name()} ({user.email}):\n"
                order_details += f"Телефон: {profile.phone if profile else 'Нет данных'}\n"
                order_details += "Машины пользователя:\n"
                if cars:
                    for car in cars:
                        order_details += f"- {car.make} {car.model} {car.year} (цвет: {car.color})\n"
                else:
                    order_details += "Нет данных о машинах\n"
                for item in cart:
                    order_details += f"- {item['name']} x {1}\n"
                order_details += f"Итого: {sum(item['price'] for item in cart)} руб."

                # Отправляем уведомление
                NOTIFY_BOT_TOKEN = settings.TELEGRAM_NOTIFY_BOT_TOKEN
                NOTIFY_CHAT_ID = settings.TELEGRAM_NOTIFY_CHAT_ID
                send_telegram_message(NOTIFY_BOT_TOKEN, NOTIFY_CHAT_ID, order_details)

                # Отправка уведомления через bot (основной бот, не regbot)
                from bot.telegram import send_telegram_message as send_mainbot_message
                MAIN_BOT_TOKEN = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
                MAIN_CHAT_ID = getattr(settings, 'TELEGRAM_CHAT_ID', None)
                if MAIN_BOT_TOKEN and MAIN_CHAT_ID:
                    mainbot_msg = f"[ЗАКАЗ ИЗ ТЕЛЕГРАМ-БОТА]\n"
                    mainbot_msg += f"Новый заказ #{order.id}\n"
                    mainbot_msg += f"Пользователь: {user.get_full_name()} ({user.email})\n"
                    mainbot_msg += f"Телефон: {profile.phone if profile else 'Нет данных'}\n"
                    mainbot_msg += f"Chat ID: {profile.chat_id if profile else 'Нет данных'}\n"
                    mainbot_msg += f"ID пользователя: {user.id}\n"
                    # Информация, которую пользователь заполнил при регистрации (Telegram)
                    reg_info = []
                    reg_info.append(f"Имя: {profile.first_name if profile else '-'}")
                    reg_info.append(f"Фамилия: {profile.last_name if profile else '-'}")
                    reg_info.append(f"Email: {profile.email if profile else '-'}")
                    reg_info.append(f"Телефон: {profile.phone if profile else '-'}")
                    reg_info.append(f"Chat ID: {profile.chat_id if profile else '-'}")
                    # Информация о машине, которую пользователь указал при регистрации (Telegram)
                    last_car = None
                    cars_list = list(cars)
                    if cars_list:
                        last_car = cars_list[-1]
                    if last_car:
                        reg_info.append("--- Данные автомобиля, указанные при регистрации в Telegram ---")
                        reg_info.append(f"Марка: {last_car.make}")
                        reg_info.append(f"Модель: {last_car.model}")
                        reg_info.append(f"Год: {last_car.year}")
                        reg_info.append(f"Цвет: {last_car.color}")
                    else:
                        reg_info.append("Данные автомобиля не указаны")
                    mainbot_msg += "\n".join(reg_info) + "\n"
                    # Услуги
                    mainbot_msg += "Услуги:\n"
                    for item in cart:
                        mainbot_msg += f"- {item['name']} x 1 ({item['price']} руб.)\n"
                    mainbot_msg += f"Итого: {sum(item['price'] for item in cart)} руб.\n"
                    send_mainbot_message(MAIN_BOT_TOKEN, MAIN_CHAT_ID, mainbot_msg)

                send_message(chat_id, "Спасибо за заказ! Мы свяжемся с вами в ближайшее время.")
                user_carts[chat_id] = []
            return

        if data == "back_to_categories":
            categories = Category.objects.all()
            keyboard = build_categories_keyboard(categories)
            send_message(chat_id, "Выберите категорию услуг:", reply_markup=keyboard)
            return

        if data == "menu_register":
            send_message(chat_id, "Пожалуйста, введите ваше имя и фамилию через пробел:")
            user_states[chat_id] = {"step": "get_name", "data": {}}
            return
        if data == "menu_services":
            categories = Category.objects.all()
            if categories:
                keyboard = build_categories_keyboard(categories)
                send_message(chat_id, "Выберите категорию услуг:", reply_markup=keyboard)
            else:
                send_message(chat_id, "Категории услуг не найдены.")
            return
        if data == "menu_cancel":
            if chat_id in user_states:
                user_states.pop(chat_id)
                send_message(chat_id, "Текущее действие отменено.")
            else:
                send_message(chat_id, "Нет активных действий для отмены.")
            return
        if data == "menu_help":
            help_text = (
                "Это телеграм-бот для регистрации и заказа услуг.\n"
                "Используйте кнопки ниже для управления ботом."
            )
            keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "Регистрация", "callback_data": "menu_register"},
                        {"text": "Просмотр услуг", "callback_data": "menu_services"}
                    ],
                    [
                        {"text": "Отмена", "callback_data": "menu_cancel"},
                        {"text": "В меню", "callback_data": "menu"}
                    ]
                ]
            }
            send_message(chat_id, help_text, reply_markup=keyboard)
            return
        if data == "menu_logout":
            user_states.pop(chat_id, None)
            user_carts.pop(chat_id, None)
            # Открепляем chat_id от UserProfile, чтобы Telegram-аккаунт не был связан с пользователем
            try:
                profile = UserProfile.objects.get(chat_id=chat_id)
                profile.chat_id = None
                profile.save()
            except UserProfile.DoesNotExist:
                pass
            send_message(chat_id, "Вы вышли из профиля. Для повторного входа используйте регистрацию или войдите на сайте.")
            return
        if data == "menu":
            keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "Регистрация", "callback_data": "menu_register"},
                        {"text": "Просмотр услуг", "callback_data": "menu_services"}
                    ],
                    [
                        {"text": "Отмена", "callback_data": "menu_cancel"}
                    ],
                    [
                        {"text": "Помощь", "callback_data": "menu_help"}
                    ]
                ]
            }
            send_message(chat_id, "Доступные команды:", reply_markup=keyboard)
            return

    if not message:
        logger.warning("No message in update")
        return
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()

    state = user_states.get(chat_id, {"step": None, "data": {}})

    if text == "/start":
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "Регистрация", "callback_data": "menu_register"},
                    {"text": "Просмотр услуг", "callback_data": "menu_services"}
                ],
                [
                    {"text": "Отмена", "callback_data": "menu_cancel"}
                ],
                [
                    {"text": "Помощь", "callback_data": "menu_help"}
                ]
            ]
        }
        send_message(chat_id, "🚀 Добро пожаловать в CosmoDetailing – Детейлинг будущего! 🌌", reply_markup=keyboard)
        user_states.pop(chat_id, None)
        return

    if text == "/menu":
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "Регистрация", "callback_data": "menu_register"},
                    {"text": "Просмотр услуг", "callback_data": "menu_services"}
                ],
                [
                    {"text": "Отмена", "callback_data": "menu_cancel"}
                ],
                [
                    {"text": "Помощь", "callback_data": "menu_help"}
                ]
            ]
        }
        send_message(chat_id, "Доступные команды:", reply_markup=keyboard)
        return

    if text == "/help":
        help_text = (
            "Это телеграм-бот для регистрации и заказа услуг.\n"
            "Используйте кнопки ниже для управления ботом."
        )
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "Регистрация", "callback_data": "menu_register"},
                    {"text": "Просмотр услуг", "callback_data": "menu_services"}
                ],
                [
                    {"text": "Отмена", "callback_data": "menu_cancel"},
                    {"text": "В меню", "callback_data": "menu"}
                ]
            ]
        }
        send_message(chat_id, help_text, reply_markup=keyboard)
        return

    if text == "/cancel":
        if chat_id in user_states:
            user_states.pop(chat_id)
            send_message(chat_id, "Текущее действие отменено.")
        else:
            send_message(chat_id, "Нет активных действий для отмены.")
        return

    if text == "/register":
        send_message(chat_id, "Пожалуйста, введите ваше имя и фамилию через пробел:")
        user_states[chat_id] = {"step": "get_name", "data": {}}
        return

    if state["step"] == "get_name":
        parts = text.split()
        if len(parts) < 2:
            send_message(chat_id, "Пожалуйста, введите имя и фамилию через пробел.")
            return
        state["data"]["first_name"] = parts[0]
        state["data"]["last_name"] = " ".join(parts[1:])
        send_message(chat_id, "Введите ваш email:")
        state["step"] = "get_email"
        user_states[chat_id] = state
        return

    if state["step"] == "get_email":
        state["data"]["email"] = text
        send_message(chat_id, "Введите пароль:")
        state["step"] = "get_password"
        user_states[chat_id] = state
        return

    if state["step"] == "get_password":
        state["data"]["password"] = text
        send_message(chat_id, "Введите номер телефона:")
        state["step"] = "get_phone"
        user_states[chat_id] = state
        return

    if state["step"] == "get_phone":
        state["data"]["phone"] = text
        send_message(chat_id, "Введите марку автомобиля:")
        state["step"] = "get_car_make"
        user_states[chat_id] = state
        return

    if state["step"] == "get_car_make":
        state["data"]["car_make"] = text
        send_message(chat_id, "Введите модель автомобиля:")
        state["step"] = "get_car_model"
        user_states[chat_id] = state
        return

    if state["step"] == "get_car_model":
        state["data"]["car_model"] = text
        send_message(chat_id, "Введите год выпуска автомобиля:")
        state["step"] = "get_car_year"
        user_states[chat_id] = state
        return

    if state["step"] == "get_car_year":
        if not text.isdigit():
            send_message(chat_id, "Пожалуйста, введите корректный год выпуска (число).")
            return
        state["data"]["car_year"] = int(text)
        send_message(chat_id, "Введите цвет автомобиля:")
        state["step"] = "get_car_color"
        user_states[chat_id] = state
        return

    if state["step"] == "get_car_color":
        state["data"]["car_color"] = text

        data = state["data"]
        form_data = {
            "username": data["email"],
            "email": data["email"],
            "password1": data["password"],
            "password2": data["password"],
            "first_name": data["first_name"],
            "last_name": data["last_name"],
        }
        form = UserRegistrationForm(form_data)
        logger.info(f"Registration form data: {form_data}")
        logger.info(f"Form valid: {form.is_valid()}")
        if not form.is_valid():
            logger.info(f"Form errors: {form.errors}")
        if form.is_valid():
            try:
                user = form.save()
                profile, created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        "first_name": data["first_name"],
                        "last_name": data["last_name"],
                        "phone": data["phone"],
                        "email": data["email"],
                        "chat_id": chat_id
                    }
                )
                # Гарантируем, что chat_id всегда актуален
                if profile.chat_id != chat_id:
                    profile.chat_id = chat_id
                    profile.save()
                # Универсальная проверка наличия машин у профиля
                cars_qs = getattr(profile, 'cars', getattr(profile, 'car_set', None))
                if cars_qs is not None and not cars_qs.exists():
                    Car.objects.create(
                        user_profile=profile,
                        make=data["car_make"],
                        model=data["car_model"],
                        year=data["car_year"],
                        color=data.get("car_color", "")
                    )
                if created:
                    send_message(chat_id, f"Регистрация успешна, {data['first_name']}! Вы можете просмотреть услуги командой /services")
                else:
                    send_message(chat_id, f"Ваш профиль обновлён, {data['first_name']}! Вы можете просмотреть услуги командой /services")
            except Exception as e:
                logger.error(f"Ошибка при создании пользователя или профиля: {e}")
                send_message(chat_id, "Произошла ошибка при регистрации. Пожалуйста, попробуйте позже.")
        else:
            if 'username' in form.errors and 'A user with that username already exists.' in form.errors['username']:
                send_message(chat_id, "Пользователь с таким email уже зарегистрирован. Пожалуйста, используйте другой email или войдите в систему.")
            else:
                errors = "; ".join([f"{field}: {error[0]}" for field, error in form.errors.items()])
                send_message(chat_id, f"Ошибка регистрации: {errors}")

        user_states.pop(chat_id, None)
        return

    if text == "/services":
        categories = Category.objects.all()
        if categories:
            keyboard = build_categories_keyboard(categories)
            send_message(chat_id, "Выберите категорию услуг:", reply_markup=keyboard)
        else:
            send_message(chat_id, "Категории услуг не найдены.")
        return

    if text.startswith("/add"):
        parts = text.split()
        if len(parts) == 2 and parts[1].isdigit():
            service_id = int(parts[1])
            try:
                service = Service.objects.get(id=service_id)
                cart = user_carts.setdefault(chat_id, [])
                cart.append({"id": service.id, "name": service.name, "price": service.price})
                send_message(chat_id, f"Услуга '{service.name}' добавлена в корзину.")
            except Service.DoesNotExist:
                send_message(chat_id, "Услуга с таким номером не найдена.")
        else:
            send_message(chat_id, "Неверная команда. Используйте /add <номер_услуги>")
        return

    send_message(chat_id, "Неизвестная команда. Используйте /start для начала.")
