import pika
from llama_index.llms.ollama import Ollama
from llama_index.core.llms import ChatMessage

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
        event = body.decode('utf-8')  # Decodificar el mensaje de bytes a string
        print(f"Evento recibido: {event}")

        try:
            messages = [
                ChatMessage(
                    role="system", content=""" You are in charge of providing the letter R for a spelling request.
                                  Only answer "R" if you are asked to spell a word with the letter R in it. Any other case answer "Pass".
                                  Do not give any extra information."""
                ),
                ChatMessage(role="user", content=f"{event}"),
]
            response = llm.chat(messages)  # Usar LLMPredictor
            string_response = str(response).strip()  # Eliminar espacios en blanco alrededor de la respuesta.
            print(f"Respuesta de Ollama: {string_response}")

            if "Pass" not in string_response:
                # Envío de la respuesta a la cola de salida
                channel.basic_publish(exchange=OUTPUT_QUEUE, routing_key="", body=string_response)
                print(f"Respuesta enviada a la cola {OUTPUT_QUEUE}")

            ch.basic_ack(delivery_tag=method.delivery_tag)  # Confirmar el mensaje

        except Exception as e:
            print(f"Error al procesar el evento: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)  # Rechazar el mensaje y no volver a enviarlo.

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