import threading
from typing import Callable

from confluent_kafka import Consumer
import json

KAFKA_BROKER = "localhost:9092"
TOPIC = "wikipedia"


def consume(func: Callable[[dict[str, str | int | float]], None], lock: threading.Lock):
    consumer = Consumer({
        'bootstrap.servers': KAFKA_BROKER,
        'group.id': 'wikipedia-consumer',
        'auto.offset.reset': 'earliest'
    })

    consumer.subscribe([TOPIC])

    while True:
        try:
            print(lock.locked())
            if lock.locked():
                continue
            with lock:
                msg = consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    print(f"Consumer error: {msg.error()}")
                    continue

                data: dict = json.loads(msg.value().decode('utf-8'))
                func(data)
        except Exception as e:
            print(f"Exception in Consumer: {e}")

    consumer.close()
