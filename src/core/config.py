import os

WIKIPEDIA_STREAM_URL: str = "https://stream.wikimedia.org/v2/stream/recentchange"

KAFKA_BROKER: str = os.environ.get("KAFKA_BROKER", "localhost:9092")
TOPIC: str = "wikipedia"

INTERVAL_SECONDS: int = 5
MAX_DOCUMENT_NUMBER: int = 3
