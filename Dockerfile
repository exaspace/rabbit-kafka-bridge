FROM exaspace/python3-rdkafka:1.0.0-0

WORKDIR /app

ADD . /app/

RUN pip3 install -r requirements.txt

ENTRYPOINT ["./rabbit-kafka-bridge.py3"]
