from datetime import datetime, timedelta

import pytz
import requests

from core.config import ALERT_TELEGRAM_BOT_TOKEN


def get_date(timestamp: float | int) -> str:
    result = datetime.fromtimestamp(timestamp, tz=pytz.UTC) + timedelta(hours=5)
    return result.strftime('%Y-%m-%d')


def get_date_time(timestamp: float | int) -> str:
    result = datetime.fromtimestamp(timestamp, tz=pytz.UTC) + timedelta(hours=5)
    return result.strftime('%Y-%m-%d %H:%M:%S')


def get_current_date_time() -> str:
    result = datetime.now(tz=pytz.UTC) + timedelta(hours=5)
    return result.strftime('%Y-%m-%d %H:%M:%S')


def send_message_to_telebot(text: str):
    if ALERT_TELEGRAM_BOT_TOKEN and len(ALERT_TELEGRAM_BOT_TOKEN) > 40:
        requests.post(
            f"https://api.telegram.org/bot{ALERT_TELEGRAM_BOT_TOKEN}/sendMessage",
            data={
                "chat_id": 686700338,
                "text": text
            }
        )
