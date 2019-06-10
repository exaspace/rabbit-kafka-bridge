# Rabbit Kafka Bridge

Application to forward messages from RabbitMQ to Kafka.

* Written in Python3
* Uses `librdkafka` under the hood (via `confluent_kafka`) so is extremely fast for Kafka operations.
* The application will recover if there are network outages connecting to Rabbit or Kafka
* Available as a docker image in the public docker hub (`exaspace/rabbit-kafka-bridge`)

Run via docker:

```
docker run --rm -it --net host exaspace/rabbit-kafka-bridge:1.0.0 \
    --rabbit_host localhost \
	--rabbit_queue somequeue \
    --kafka_host localhost \
    --kafka_port 9092 \
	--kafka_topic sometopic
```

Or run natively:

```
pip3 install -r requirements.txt
./rabbit-kafka-bridge.py3
```

To see all options use `--help`


### Quick demo using docker-compose

In the `integration-test` directory there is a docker compose file which will start RabbitMQ, Kafka and the bridge application (configured to read from `testqueue` in Rabbit and send to topic `testtopic` in Kafka).

```
docker-compose up -d
```

Send a message to RabbitMQ:

```
docker-compose exec rabbit-kafka-bridge util/rabbit-send.py --host rabbitmq --exchange testexchange --message "Hello" --count 1
```

You should see the messages arriving in Kafka:

```
docker-compose exec kafka kafka-console-consumer.sh  --bootstrap-server localhost:9092 --from-beginning --topic testtopic
```
