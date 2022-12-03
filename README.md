# Rabbit Kafka Bridge

[![Test](https://github.com/exaspace/rabbit-kafka-bridge/actions/workflows/main.yml/badge.svg)](https://github.com/exaspace/rabbit-kafka-bridge/actions/workflows/main.yml)

Simple application to forward messages from a RabbitMQ queue to a Kafka topic.

* Written in Python3
* Uses `librdkafka` under the hood (via `confluent_kafka`) so is very fast for Kafka operations.
* The application will recover if there are network outages connecting to Rabbit or Kafka
* Available as a docker image in the public docker hub (`exaspace/rabbit-kafka-bridge`)
* The docker image is rebuilt on a weekly basis to ensure latest security updates are applied from the base image

Run via docker:

```
docker run --rm -it --net host exaspace/rabbit-kafka-bridge \
    --rabbit_host localhost \
    --rabbit_queue somequeue \
    --kafka_host localhost \
    --kafka_port 9092 \
    --kafka_topic sometopic
```

Or run natively:

```
pip3 install -r requirements.txt
./rabbit-kafka-bridge.py
```

To see all options use `--help`


### Quick demo using docker compose

The docker compose file will build the application docker image locally and start RabbitMQ and Kafka (RabbitMQ is configured to start with a queue called 'testqueue' which is bound to an exchange called 'testexchange').

```
docker compose up -d
```

Send a message to RabbitMQ (to exchange 'testexchange'):

```
docker compose exec rabbit-kafka-bridge util/rabbit-send.py \
    --host rabbitmq --exchange testexchange --message "Hello" --count 1
```

You should see the messages arriving in Kafka on topic 'testtopic' (NB this command is quite slow):

```
docker compose exec kafka kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 --from-beginning --topic testtopic
```
