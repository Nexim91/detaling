import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from .telegram import handle_update, REGBOT_TELEGRAM_BOT_TOKEN, REGBOT_TELEGRAM_API_URL
import requests

@csrf_exempt
def telegram_webhook(request):
    if request.method == "POST":
        try:
            update = json.loads(request.body)
            handle_update(update)
        except Exception as e:
            print(f"Error handling update: {e}")
        return JsonResponse({"status": "ok"})
    else:
        return JsonResponse({"status": "method not allowed"}, status=405)

def set_webhook():
    webhook_url = f"https://yourdomain.com/regbot/webhook/"  # Replace with your actual webhook URL
    url = f"{REGBOT_TELEGRAM_API_URL}/setWebhook"
    params = {"url": webhook_url}
    response = requests.get(url, params=params)
    return response.json()
