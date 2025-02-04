from datetime import datetime, timedelta

import pytz


def get_date(timestamp: float | int) -> str:
    result = datetime.fromtimestamp(timestamp, tz=pytz.UTC) + timedelta(hours=5)
    return result.strftime('%Y-%m-%d')


def get_date_time(timestamp: float | int) -> str:
    result = datetime.fromtimestamp(timestamp, tz=pytz.UTC) + timedelta(hours=5)
    return result.strftime('%Y-%m-%d %H:%M:%S')


def get_current_date_time() -> str:
    result = datetime.now(tz=pytz.UTC) + timedelta(hours=5)
    return result.strftime('%Y-%m-%d %H:%M:%S')
