import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'detailing_project.settings')
django.setup()

from regbot.telegram import handle_update, user_carts, user_states

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def simulate_message(chat_id, text):
    update = {
        "message": {
            "chat": {"id": chat_id},
            "text": text
        }
    }
    handle_update(update)

def simulate_callback(chat_id, data):
    update = {
        "callback_query": {
            "message": {"chat": {"id": chat_id}},
            "data": data
        }
    }
    handle_update(update)

def test_registration_flow(chat_id):
    logger.info("Тестирование процесса регистрации")
    simulate_message(chat_id, "/register")
    simulate_message(chat_id, "Иван Иванов")
    simulate_message(chat_id, "ivan@example.com")
    simulate_message(chat_id, "пароль123")
    simulate_message(chat_id, "+71234567890")
    simulate_message(chat_id, "Toyota")
    simulate_message(chat_id, "Camry")
    simulate_message(chat_id, "2015")
    simulate_message(chat_id, "А123ВС")

def test_duplicate_registration(chat_id):
    logger.info("Тестирование повторной регистрации")
    test_registration_flow(chat_id)
    # Попытка зарегистрироваться повторно с тем же email
    simulate_message(chat_id, "/register")
    simulate_message(chat_id, "Иван Иванов")
    simulate_message(chat_id, "ivan@example.com")
    simulate_message(chat_id, "пароль123")
    simulate_message(chat_id, "+71234567890")
    simulate_message(chat_id, "Toyota")
    simulate_message(chat_id, "Camry")
    simulate_message(chat_id, "2015")
    simulate_message(chat_id, "А123ВС")

def test_add_services_and_cart(chat_id):
    logger.info("Тестирование добавления услуг и корзины")
    simulate_message(chat_id, "/services")
    # Предполагается, что категория с id=1 существует
    simulate_callback(chat_id, "category_1")
    # Добавление услуги с id=1
    simulate_callback(chat_id, "add_1")
    simulate_callback(chat_id, "view_cart")
    simulate_callback(chat_id, "remove_0")
    simulate_callback(chat_id, "view_cart")

def test_checkout(chat_id):
    logger.info("Тестирование оформления заказа")
    # Добавление услуги снова
    simulate_callback(chat_id, "add_1")
    simulate_callback(chat_id, "checkout")

def test_navigation_commands(chat_id):
    logger.info("Тестирование навигационных команд")
    simulate_message(chat_id, "/start")
    simulate_message(chat_id, "/menu")
    simulate_message(chat_id, "/help")
    simulate_message(chat_id, "/cancel")

def run_all_tests():
    test_chat_id = 123456789
    test_registration_flow(test_chat_id)
    test_duplicate_registration(test_chat_id)
    test_add_services_and_cart(test_chat_id)
    test_checkout(test_chat_id)
    test_navigation_commands(test_chat_id)
    logger.info("Все тесты завершены")

if __name__ == "__main__":
    run_all_tests()
