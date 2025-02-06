# agents-sandbox
sandbox to play with agents in a distributed fashion

We need to have a kafka docker image running for this to work:
```
docker run -d -p 9092:9092 --name broker apache/kafka:latest
```
After having it running, we need to create 2 topics, 1 for "preguntas" and another for "respuestas:
- Connect to the image: 
```
docker exec --workdir /opt/kafka/bin/ -it broker sh
```
- Create first topic:
```
./kafka-topics.sh --bootstrap-server localhost:9092 --create --topic preguntas
```
- Create second topic:
```
./kafka-topics.sh --bootstrap-server localhost:9092 --create --topic respuestas
```

Then we can just launch the two agents(in 2 different consoles):
```
python distributed-specialiced-agent-A.py
```

```
python distributed-specialiced-agent-R.py
```

We can now send new questions to the agents using the `send_kafka.py` script in `tools`
We can log the topics with `receive_kafka.py` script in `tools`.