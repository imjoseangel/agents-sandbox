# agents-sandbox
Sandbox to play with agents in a distributed fashion

We need to have a RabbitMQ docker image running for this to work:
```
docker run --rm -p 5672:5672 -p 15672:15672 --hostname localhost --name some-rabbit-mg -e RABBITMQ_DEFAULT_USER=user -e RABBITMQ_DEFAULT_PASS=password rabbitmq:3-management
```
We can see the management console going to `http://localhost:15672/`

Then we can just launch the two agents(in 2 different consoles):
```
python agents/rabbit/distributed-specialiced-agent-A.py
```

```
python agents/rabbit/distributed-specialiced-agent-R.py
```

We can ask another agent to be the orchestrator. An example is in `agents/rabbit/launcher-agent.py` an agent that bradcasts a question to all the agents and gets their response.

We can now send new questions to the agents using the `rabbit/send_rabbit.py` script in `tools`.
We can log the queues with `rabbit/receive_rabbit.py` script in `tools`.

## ToDo:
- Follow the cloud events specification for the messages sent through the system
- Add a transaction id to the messages (So that the questioning agent can identify which messages are answers to it or not)
- Decouple the logic to send/receive messages from the Agent (So that any other technologie can be used)
- Create an `AgentBaseModel` with the generic logic to be extended by any agent that wants to join the network