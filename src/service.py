from pymongo.results import UpdateResult

import mongo_client
import util
from mongo_client import Data


def update_language(key: int, language: str) -> int:
    default_language_collection = mongo_client.get_default_language_collection()
    result: UpdateResult = default_language_collection.update_one(
        {"key": key},
        {"$set": {
            "language": language,
            "updated_at": util.get_current_date_time()
        }},
        upsert=True
    )
    return result.matched_count


def get_language_by_key(key: int) -> str:
    default_language_collection = mongo_client.get_default_language_collection()
    data: Data = default_language_collection.find_one({'key': key})
    return data['language'] if data else 'en'


def increment_daily_stats(language: str, date: str) -> int:
    daily_stats_collection = mongo_client.get_daily_stats_collection()
    data: Data = daily_stats_collection.find_one({
        "language": language,
        "date": date
    })
    if data:
        result: UpdateResult = daily_stats_collection.update_one(
            {"_id": data['_id']},
            {"$set": {
                "amount": data['amount'] + 1,
                "updated_at": util.get_current_date_time()
            }}
        )
        return result.matched_count
    else:
        daily_stats_collection.insert_one({
            "language": language,
            "date": date,
            "amount": 0
        })
        return 1


def get_daily_stats(language: str, date: str) -> int:
    daily_stats_collection = mongo_client.get_daily_stats_collection()
    data: Data = daily_stats_collection.find_one({
        "language": language,
        "date": date
    })
    return data['amount'] if data else 0


def append_event(language: str, event: dict):
    recent_events_collection = mongo_client.get_recent_events_collection()
    event['language'] = language
    recent_events_collection.insert_one({
        'language': language,
        'title': event['title'],
        'user': event['user'],
        'timestamp': event['timestamp'],
        'server_url': event['server_url']
    })
    documents: list = list(recent_events_collection.find({"language": language}).sort("timestamp", 1))
    if len(documents) <= 5:
        return
    oldest = documents[:len(documents) - 5]
    for doc in oldest:
        recent_events_collection.delete_one({"_id": doc["_id"]})


def get_events(language: str) -> list:
    recent_events_collection = mongo_client.get_recent_events_collection()
    data_list = recent_events_collection.find({"language": language})
    return list(data_list) if data_list else []
