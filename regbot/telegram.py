import requests
from django.conf import settings
from django.contrib.auth.models import User
from accounts.models import UserProfile, Car
from accounts.forms_new import UserRegistrationForm
from pricing.models import Service

# Removed import of telegram package to avoid ModuleNotFoundError
# from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Instead, use raw JSON for inline keyboard markup in send_message function

# Separate token and API URL for this bot to allow independent connection
REGBOT_TELEGRAM_BOT_TOKEN = settings.REGBOT_TELEGRAM_BOT_TOKEN
REGBOT_TELEGRAM_API_URL = f"https://api.telegram.org/bot{REGBOT_TELEGRAM_BOT_TOKEN}"

# In-memory user states for dialog (in production use persistent storage)
user_states = {}

# In-memory cart storage per user chat_id
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
    for category in categories:
        keyboard.append([{"text": category, "callback_data": f"category_{category}"}])
    return {"inline_keyboard": keyboard}

def build_services_keyboard(services):
    keyboard = []
    for service in services:
        keyboard.append([{"text": f"{service.name} - {service.price} руб.", "callback_data": f"add_{service.id}"}])
    keyboard.append([{"text": "Просмотреть корзину", "callback_data": "view_cart"}])
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
            category = data[len("category_"):]
            services = Service.objects.filter(category=category)
            keyboard = build_services_keyboard(services)
            send_message(chat_id, f"Услуги категории {category}:", reply_markup=keyboard)
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
                # Здесь можно добавить логику оформления заказа
                send_message(chat_id, "Спасибо за заказ! Мы свяжемся с вами в ближайшее время.")
                user_carts[chat_id] = []
            return

        if data == "menu":
            menu_text = (
                "Доступные команды:\n"
                "/register - Регистрация\n"
                "/services - Просмотр услуг\n"
                "/cancel - Отмена текущего действия\n"
                "/help - Помощь\n"
            )
            send_message(chat_id, menu_text)
            return

    if not message:
        logger.warning("No message in update")
        return
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()

    state = user_states.get(chat_id, {"step": None, "data": {}})

    if text == "/start":
        send_message(chat_id, "Добро пожаловать! Чтобы зарегистрироваться, отправьте команду /register\nДля просмотра меню используйте /menu")
        user_states.pop(chat_id, None)
        return

    if text == "/menu":
        menu_text = (
            "Доступные команды:\n"
            "/register - Регистрация\n"
            "/services - Просмотр услуг\n"
            "/cancel - Отмена текущего действия\n"
            "/help - Помощь\n"
        )
        send_message(chat_id, menu_text)
        return

    if text == "/help":
        help_text = (
            "Это телеграм-бот для регистрации и заказа услуг.\n"
            "Используйте /register для регистрации.\n"
            "Используйте /services для просмотра услуг.\n"
            "Используйте /add <номер_услуги> для добавления услуги в корзину.\n"
            "Используйте /cancel для отмены текущего действия."
        )
        send_message(chat_id, help_text)
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
        send_message(chat_id, "Введите госномер автомобиля:")
        state["step"] = "get_car_license"
        user_states[chat_id] = state
        return

    if state["step"] == "get_car_license":
        state["data"]["car_license"] = text

        # Попытка создать пользователя и профиль
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
        if form.is_valid():
            user = form.save()
            # Проверяем, существует ли профиль для пользователя
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "phone": data["phone"],
                    "email": data["email"]
                }
            )
            if created:
                Car.objects.create(
                    user_profile=profile,
                    make=data["car_make"],
                    model=data["car_model"],
                    year=data["car_year"],
                    license_plate=data["car_license"]
                )
                send_message(chat_id, f"Регистрация успешна, {data['first_name']}! Вы можете просмотреть услуги командой /services")
            else:
                send_message(chat_id, "Профиль пользователя уже существует. Пожалуйста, войдите в систему.")
        else:
            if 'username' in form.errors and 'A user with that username already exists.' in form.errors['username']:
                send_message(chat_id, "Пользователь с таким email уже зарегистрирован. Пожалуйста, используйте другой email или войдите в систему.")
            else:
                errors = "; ".join([f"{field}: {error[0]}" for field, error in form.errors.items()])
                send_message(chat_id, f"Ошибка регистрации: {errors}")

        user_states.pop(chat_id, None)
        return

    if text == "/services":
        services = Service.objects.all()
        if services:
            keyboard = build_services_keyboard(services)
            send_message(chat_id, "Доступные услуги:", reply_markup=keyboard)
        else:
            send_message(chat_id, "Услуги не найдены.")
        return

    if text.startswith("/add"):
        parts = text.split()
        if len(parts) == 2 and parts[1].isdigit():
            service_id = int(parts[1])
            try:
                service = Service.objects.get(id=service_id)
                # TODO: связать с пользователем Telegram, для упрощения пропущено
                send_message(chat_id, f"Услуга '{service.name}' добавлена в корзину.")
            except Service.DoesNotExist:
                send_message(chat_id, "Услуга с таким номером не найдена.")
        else:
            send_message(chat_id, "Неверная команда. Используйте /add <номер_услуги>")
        return

    send_message(chat_id, "Неизвестная команда. Используйте /start для начала.")
