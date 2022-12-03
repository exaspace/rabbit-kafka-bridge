#!/usr/bin/env python3
"""
Component to forward messages from RabbitMQ to Kafka.
"""
import logging
import logging.config
import argparse
import pika
import time
import pprint
from confluent_kafka import Producer

logger = logging.getLogger()


class Rabbit2Kafka(object):
    def __init__(self, rabbit_reader, kafka_writer):
        self.rabbit_reader = rabbit_reader
        self.kafka_writer = kafka_writer

    def run(self):
        rabbit_reader.run(self._callback)

    def _callback(self, pika_channel, method, properties, body):
        logger.debug("Received rabbit message={}".format(body))
        self.kafka_writer.write(body)


class RabbitReader(object):
    def __init__(self, host, queue_name):
        self.host = host
        self.queue_name = queue_name

    def run(self, callback):
        while True:
            try:
                self._start()
                self.channel.basic_consume(
                    on_message_callback=callback, queue=self.queue_name, auto_ack=True
                )
                logger.info("Starting Rabbit consumption")
                self.channel.start_consuming()
            except pika.exceptions.AMQPConnectionError:
                logger.error("Can't connect to Rabbit Server")
            time.sleep(1)

    def _start(self):
        logger.info("Opening connection to Rabbit")
        params = pika.ConnectionParameters(self.host)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()


class KafkaWriter(object):
    def __init__(self, hosts, topic_name):
        self.hosts = hosts
        self.topic_name = topic_name
        self.producer = None
        self._connect()

    def _connect(self):
        try:
            logger.info("Connecting to Kafka hosts={}".format(self.hosts))
            self.producer = Producer({"bootstrap.servers": self.hosts})
        except:
            logger.exception("Could not connect to Kafka hosts={}".format(self.hosts))

    def write(self, message):
        while self.producer is None:
            self._connect()
            time.sleep(3)
        try:
            logger.debug("Sending message to Kafka")
            self.producer.produce(self.topic_name, message)
            logger.debug("...done")
        except Exception as e:
            logger.exception("Error sending message to Kafka. Will re-create producer")
            self.producer = None


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--rabbit_host", type=str, default="localhost")
    parser.add_argument("--rabbit_queue", type=str)
    parser.add_argument("--kafka_host", type=str, default="localhost")
    parser.add_argument("--kafka_port", type=int, default=9092)
    parser.add_argument("--kafka_topic", type=str)

    args = parser.parse_args()
    if not args.rabbit_queue or not args.kafka_topic:
        parser.print_help()
    else:
        logging.config.fileConfig("logging.conf")
        rabbit_reader = RabbitReader(
            host=args.rabbit_host, queue_name=args.rabbit_queue
        )
        kafka_writer = KafkaWriter(
            "{}:{}".format(args.kafka_host, args.kafka_port), args.kafka_topic
        )
        Rabbit2Kafka(rabbit_reader, kafka_writer).run()
