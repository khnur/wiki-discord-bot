import os

WIKIPEDIA_STREAM_URL: str = "https://stream.wikimedia.org/v2/stream/recentchange"

MONGO_CLIENT: str = os.environ.get(
    "MONGO_CLIENT"
) or 'mongodb://abc:pass@mongo:27017?retryWrites=true&w=majority&authSource=admin'

KAFKA_BROKER: str = os.environ.get("KAFKA_BROKER", "localhost:9092")
TOPIC: str = "wikipedia"

ALERT_TELEGRAM_BOT_TOKEN: str = os.environ.get("ALERT_TELEGRAM_BOT_TOKEN", "")

INTERVAL_SECONDS: int = 5
MAX_DOCUMENT_NUMBER: int = 3
