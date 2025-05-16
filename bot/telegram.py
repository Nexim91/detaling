import requests

def send_telegram_message(token: str, chat_id: str, message: str) -> bool:
    """
    Send a message to a Telegram chat using a bot token.

    Args:
        token (str): Telegram bot token.
        chat_id (str): Chat ID to send the message to.
        message (str): Message text.

    Returns:
        bool: True if message sent successfully, False otherwise.
    """
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")
        return False
