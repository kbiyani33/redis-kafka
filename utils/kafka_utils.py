from kafka import KafkaProducer, KafkaConsumer
import json

TOPIC_NAME = "crud_operations"

def get_kafka_producer():
    return KafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

def get_kafka_consumer():
    return KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers="localhost:9092",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )
