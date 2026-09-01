import logging
import threading
import requests
from django.conf import settings

logger = logging.getLogger('sentinelad.app')

def send_telegram_alert(message: str):
    """
    Gửi tin nhắn Telegram thông qua Bot ngầm (không làm chậm ứng dụng)
    """
    def _send():
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)
        
        if not token or not chat_id:
            logger.warning("Telegram token or chat_id is missing.")
            return

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        try:
            response = requests.post(url, json=payload, timeout=5)
            if not response.ok:
                logger.error(f"Failed to send Telegram alert: {response.text}")
        except Exception as e:
            logger.error(f"Exception sending Telegram alert: {e}")

    thread = threading.Thread(target=_send)
    thread.start()
