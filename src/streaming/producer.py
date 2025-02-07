import json
import time

import requests
from confluent_kafka import Producer

KAFKA_BROKER: str = "localhost:9092"
TOPIC: str = "wikipedia"
WIKIPEDIA_STREAM_URL: str = "https://stream.wikimedia.org/v2/stream/recentchange"

producer: Producer = Producer({'bootstrap.servers': KAFKA_BROKER})


def delivery_report(err, msg):
    if err:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def produce():
    response = requests.get(WIKIPEDIA_STREAM_URL, stream=True)
    print("Connected to Wikipedia stream...")
    for line in response.iter_lines():
        if not line:
            continue
        try:
            the_line: str = line.decode("utf-8").strip()
            if not the_line.startswith("data:"):
                continue
            data_str: str = the_line[len("data:"):].strip()
            if not data_str:
                continue
            data = json.loads(data_str)
            producer.produce(TOPIC, json.dumps(data), callback=delivery_report)
            producer.flush()
        except json.JSONDecodeError as e:
            print(f'Error: {e}')
        time.sleep(5)
