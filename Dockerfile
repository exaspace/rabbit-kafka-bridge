FROM exaspace/python3-rdkafka:1.1.0

WORKDIR /app

COPY . /app/

RUN pip install -r requirements.txt

ENTRYPOINT ["./rabbit-kafka-bridge.py"]
