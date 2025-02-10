import json
import time

import requests
from confluent_kafka import Producer

from core.config import *


def delivery_report(err, msg):
    if err:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def produce():
    producer: Producer = Producer({'bootstrap.servers': KAFKA_BROKER})
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
        time.sleep(INTERVAL_SECONDS)
