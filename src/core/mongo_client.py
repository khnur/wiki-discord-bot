from typing import Any

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

mongoClient: MongoClient = MongoClient(
    'mongodb://abc:pass@mongo:27017?retryWrites=true&w=majority&authSource=admin'
)
database: Database = mongoClient['wiki']

Data = dict[str, Any]

default_language_collection: Collection | None = None
daily_stats_collection: Collection | None = None
recent_events_collection: Collection | None = None


def get_default_language_collection() -> Collection:
    global default_language_collection
    if default_language_collection is None:
        default_language_collection = database['default_languages']
        default_language_collection.create_index('key', unique=True)
    return default_language_collection


def get_daily_stats_collection() -> Collection:
    global daily_stats_collection
    if daily_stats_collection is None:
        daily_stats_collection = database['daily_stats']
        daily_stats_collection.create_index([("language", 1), ("date", 1)], unique=True)
    return daily_stats_collection


def get_recent_events_collection() -> Collection:
    global recent_events_collection
    if recent_events_collection is None:
        recent_events_collection = database['recent_events']
    return recent_events_collection
