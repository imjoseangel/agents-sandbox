import pika
from llama_index.llms.ollama import Ollama
from llama_index.core.llms import ChatMessage
import json

# Configuración de RabbitMQ con credenciales
RABBITMQ_HOST = 'localhost'  # Reemplaza con tu host de RabbitMQ
RABBITMQ_USER = 'user'  # Reemplaza con tu usuario de RabbitMQ
RABBITMQ_PASSWORD = 'password'  # Reemplaza con tu contraseña de RabbitMQ
IDENTIFIER = 'Agent_R'
INPUT_EXCHANGE = 'preguntas'
INPUT_QUEUE = f'{INPUT_EXCHANGE}.{IDENTIFIER}'
OUTPUT_QUEUE = 'respuestas'

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
    channel.exchange_declare(exchange=INPUT_EXCHANGE, exchange_type="fanout")
    channel.queue_declare(queue=INPUT_QUEUE)
    channel.queue_bind(queue=INPUT_QUEUE, exchange=INPUT_EXCHANGE)

    def callback(ch, method, properties, body):
        message_json = json.loads(body.decode('utf-8'))
        transaction_id = message_json.get("transaction_id")
        message = message_json.get("message")

        print(f"Received message: {message_json}")

        try:
            messages = [
                ChatMessage(
                    role="system", content=""" You are in charge of providing the letter R for a spelling request.
                                  Only answer "R" if you are asked to spell a word with the letter R in it. Any other case answer "Pass".
                                  Do not give any extra information."""
                ),
                ChatMessage(role="user", content=f"{message}"),
            ]
            response = llm.chat(messages)  # Usar LLMPredictor
            string_response = str(response).strip()  # Eliminar espacios en blanco alrededor de la respuesta.
            print(f"Respuesta de Ollama: {string_response}")

            if "Pass" not in string_response:
                output_message = {
                    "transaction_id": transaction_id,
                    "response": string_response,
                    "description": f"Agent {IDENTIFIER} is in charge of providing the letter R for a spelling request",  # Include agent description
                }

                channel.basic_publish(
                    exchange="",
                    routing_key=transaction_id,
                    body=json.dumps(output_message)  # Send JSON response
                )
                print(f"Response sent to queue {OUTPUT_QUEUE}: {output_message}")

            ch.basic_ack(delivery_tag=method.delivery_tag)

        except json.JSONDecodeError:
            print(f"Error: Invalid JSON received: {body.decode('utf-8')}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False) #Nack the message to avoid infinite loop
        except Exception as e:
            print(f"Error processing event: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
    # Consumir mensajes de la cola de entrada
    channel.basic_consume(queue=INPUT_QUEUE, on_message_callback=callback)

    print(' [*] Esperando mensajes. Para salir, presiona CTRL+C')
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        connection.close()
        print("Programa interrumpido por el usuario.")


if __name__ == "__main__":
    main()