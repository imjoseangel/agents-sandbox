import pika
from llama_index.llms.ollama import Ollama
from llama_index.core.llms import ChatMessage
import uuid, json, time, threading

# Configuración de RabbitMQ con credenciales
RABBITMQ_HOST = 'localhost'  # Reemplaza con tu host de RabbitMQ
RABBITMQ_USER = 'user'  # Reemplaza con tu usuario de RabbitMQ
RABBITMQ_PASSWORD = 'password'  # Reemplaza con tu contraseña de RabbitMQ
IDENTIFIER = 'Agent_orchestrator'
QUESTION_EXCHANGE = 'preguntas'
QUESTION_QUEUE = f'{QUESTION_EXCHANGE}.{IDENTIFIER}'

ANSWER_EXCHANGE = 'respuetas'
ANSWER_QUEUE = f'{ANSWER_EXCHANGE}.{IDENTIFIER}'
# Configuración de Ollama
OLLAMA_BASE_URL = "http://localhost:11434"  # Reemplaza con la URL de tu instancia de Ollama
MODEL = "gemma2"  # Reemplaza con el modelo que quieres usar

def consume_messages_after_delay(channel, queue_name, delay=10):
    
    """Consumes messages from a queue after a delay, returning them in a list."""
    time.sleep(delay)  # Wait for the delay

    messages = []
    while True:
        method, properties, body = channel.basic_get(queue=queue_name, auto_ack=True) # auto_ack=True
        if method is None:  # No more messages
            break
        messages.append(json.loads(body.decode()))

    return messages


def main():
    try:
    # Inicialización de LlamaIndex y Ollama
        llm = Ollama(model=MODEL, request_timeout=60.0, temperature=0)

        # Credenciales de RabbitMQ
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)

        # Conexión a RabbitMQ con credenciales
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
        channel = connection.channel()

        # Declaración de colas (si no existen)
        channel.exchange_declare(exchange=QUESTION_EXCHANGE,exchange_type="fanout")
        channel.queue_declare(queue=QUESTION_QUEUE)
        channel.queue_bind(queue=QUESTION_QUEUE,exchange=QUESTION_EXCHANGE)
        # Declaración de colas (si no existen)
        channel.exchange_declare(exchange=ANSWER_EXCHANGE,exchange_type="fanout")
        channel.queue_declare(queue=ANSWER_QUEUE)
        channel.queue_bind(queue=ANSWER_QUEUE,exchange=ANSWER_EXCHANGE)
        
        
        # Create the LLM connection
        messages = [
                    ChatMessage(
                        role="system", content=""" You are the host of a spelling TV show. 
                        You will ask the guests to spell a word in capital letters.
                        Always ask in the same format: Can you help me spell PERRO?
                        Do not add anything else to the question."""
                    ),
                    ChatMessage(role="user", content="Lets start the show. Host, first word?"),
        ]
        response = llm.chat(messages)
        response
        print(response)
        
        # Create JSON payload with message and UUID
        transaction_id = str(uuid.uuid4())
        payload = {
            "message": str(response.message),
            "transaction_id": transaction_id
        }
        json_payload = json.dumps(payload)

        channel.basic_publish(exchange=QUESTION_EXCHANGE, routing_key="", body=json_payload)
        channel.queue_declare(transaction_id,auto_delete=True)
        
        all_messages_received = consume_messages_after_delay(channel,transaction_id,5)
        
        channel.queue_delete(transaction_id)
        
        converted_to_chat = [ChatMessage(role="user", content=f"Answer: {response["response"]} . Description: {response["description"]}") for response in all_messages_received]
        
        system_message = [
                    ChatMessage(
                        role="system", content="""You will be receiving several answers from different agents.
                        They will also send a description of their task.
                        Based on the Answer field of each answer, tell me if they helped you in the spelling or not.
                        If you don't receive any answer. Simply say: "NO ANSWERS RECEIVED"."""
                    ),
                    ChatMessage(role="user",content="Here are the anwers:")
        ]
        
        responses_messages=system_message+converted_to_chat
        response = llm.chat(responses_messages)
        response
        print(f"RESPONSE: {response}")
        
        
    finally:
        channel.cancel()
        connection.close()
    
    



    # Prompt it to spell a word
    # Wait for X seconds for answers
    # Evaluate the answers
    # Do somehthing with the answers


if __name__ == "__main__":
    main()