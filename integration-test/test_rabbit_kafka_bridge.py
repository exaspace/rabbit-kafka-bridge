import os
import time
import logging
import logging.config
from typing import List
import uuid

import pika
from confluent_kafka import Consumer, TopicPartition
from confluent_kafka.admin import AdminClient, NewTopic


RABBIT_HOST = os.getenv("RABBIT_HOST", "localhost")
EXCHANGE = "testexchange"
ROUTING_KEY = ""

KAFKA_HOST = f"{os.getenv('KAFKA_HOST', 'localhost')}:9092"
KAFKA_TOPIC = "testtopic"

logging.config.fileConfig("../logging.conf")
logger = logging.getLogger()


def kafka_create_topic(
    host: str, topic: str, num_partitions: int = 1, replication_factor: int = 1
):
    a = AdminClient({"bootstrap.servers": host})
    all = a.list_topics().topics
    topics = list(all.keys())
    if topic not in topics:
        new_topics = [
            NewTopic(
                topic,
                num_partitions=num_partitions,
                replication_factor=replication_factor,
            )
        ]
        fs = a.create_topics(new_topics)
        fs[topic].result()
        logger.info("Kafka topic %s created", topic)
    else:
        logger.info("Kafka topic %s exists", topic)


def kafka_consume_last_message(host: str, topic: str, partition: int):
    c = Consumer(
        {
            "bootstrap.servers": host,
            "group.id": "testgroup",
            "auto.offset.reset": "latest",
        }
    )
    tp = TopicPartition(topic, partition=partition, offset=0)
    _low, high = c.get_watermark_offsets(tp)
    tp.offset = high - 1
    c.assign([tp])
    msgs = c.consume(1)
    msg = msgs[0]
    if msg.error():
        raise Exception("Consumer error: {}".format(msg.error()))
    c.close()
    value = msg.value().decode("utf-8")
    logger.debug("Read message from Kafka: '%s'", value[:40])
    return value


def rabbit_send(host: str, exchange: str, messages: List[str]):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host))
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange, passive=True)
    for msg in messages:
        logger.debug("Publishing to RabbitMQ: '%s'", msg[:40])
        channel.basic_publish(
            exchange=EXCHANGE,
            routing_key=ROUTING_KEY,
            body=msg,
            properties=pika.BasicProperties(delivery_mode=2),
        )  # persistent
    connection.close()


def test_send_receive():
    kafka_create_topic(KAFKA_HOST, KAFKA_TOPIC, num_partitions=1, replication_factor=1)

    rabbit_message = f"Hello {uuid.uuid4().hex}"
    rabbit_send(RABBIT_HOST, EXCHANGE, [rabbit_message])
    time.sleep(2)  # should be more than enough time for message to be forwarded
    kafka_msg = kafka_consume_last_message(KAFKA_HOST, KAFKA_TOPIC, partition=0)

    assert kafka_msg == rabbit_message
