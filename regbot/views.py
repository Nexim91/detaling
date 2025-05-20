import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from .telegram import handle_update, REGBOT_TELEGRAM_BOT_TOKEN, REGBOT_TELEGRAM_API_URL
import requests

import logging
logger = logging.getLogger(__name__)

@csrf_exempt
def telegram_webhook(request):
    logger.info(f"Incoming request: method={request.method}, path={request.path}, body={request.body.decode('utf-8', errors='ignore')}")
    if request.method == "POST":
        try:
            update = json.loads(request.body)
            # Проверяем наличие message или callback_query
            if "message" in update or "callback_query" in update:
                handle_update(update)
            else:
                logger.warning("No message or callback_query in update")
        except Exception as e:
            logger.error(f"Error handling update: {e}")
        return JsonResponse({"status": "ok"})
    else:
        return JsonResponse({"status": "method not allowed"}, status=405)

def set_webhook():
    webhook_url = f"https://yourdomain.com/regbot/webhook/"  # Replace with your actual webhook URL
    url = f"{REGBOT_TELEGRAM_API_URL}/setWebhook"
    params = {"url": webhook_url}
    response = requests.get(url, params=params)
    return response.json()
