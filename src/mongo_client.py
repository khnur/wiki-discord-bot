from typing import Any

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

mongoClient: MongoClient = MongoClient(
    'mongodb://abc:pass@mongo:27017?retryWrites=true&w=majority&authSource=admin'
)
database: Database = mongoClient['wiki']

Data = dict[str, Any]


def get_default_language_collection() -> Collection:
    collection: Collection = database['default_languages']
    collection.create_index('key', unique=True)
    return collection


def get_daily_stats_collection() -> Collection:
    collection: Collection = database['daily_stats']
    collection.create_index([("language", 1), ("date", 1)], unique=True)
    return collection


def get_recent_events_collection() -> Collection:
    return database['recent_events']
