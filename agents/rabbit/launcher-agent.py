import pika
from llama_index.llms.ollama import Ollama
from llama_index.core.llms import ChatMessage

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


def main():
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
                    You will ask the guests to spell a random word in capital letters.
                    Always ask in the same format: Can you help me spell "random word"?
                    Do not add anything else to the question."""
                ),
                ChatMessage(role="user", content="Lets start the show. Host, first word?"),
    ]
    response = llm.chat(messages)
    response
    print(response)
    
    channel.basic_publish(exchange=QUESTION_EXCHANGE, routing_key="", body=str(response.message))
    # Prompt it to spell a word
    # Wait for X seconds for answers
    # Evaluate the answers
    # Do somehthing with the answers


if __name__ == "__main__":
    main()