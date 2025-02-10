import pika

# Configuración de RabbitMQ con credenciales
RABBITMQ_HOST = 'localhost'  # Reemplaza con tu host de RabbitMQ
RABBITMQ_USER = 'user'  # Reemplaza con tu usuario de RabbitMQ
RABBITMQ_PASSWORD = 'password'  # Reemplaza con tu contraseña de RabbitMQ
EXCHANGES = ["preguntas", "respuestas"]  # Reemplaza con las colas que quieres escuchar
IDENTIFIER = "monitor"

def consumir_eventos():
    """Consume mensajes de colas y los imprime por pantalla."""

    # Credenciales de RabbitMQ
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)

    # Conexión a RabbitMQ con credenciales
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
    channel = connection.channel()
    

    # Declaración de colas (se asegura de que las colas existan)
    for exchange in EXCHANGES:
        channel.exchange_declare(exchange=exchange,exchange_type="fanout")
        queue_name = f"{exchange}.{IDENTIFIER}"
        channel.queue_declare(queue=queue_name)
        channel.queue_bind(queue=queue_name,exchange=exchange)

    def callback(ch, method, properties, body):
        evento = body.decode('utf-8')  # Decodificar el mensaje de bytes a string
        queue = method.routing_key
        print(f"Evento recibido en cola {queue}: {evento}")
        ch.basic_ack(delivery_tag=method.delivery_tag)  # Confirmar el mensaje

    try:
        # Consumir mensajes de las colas
        for exchange in EXCHANGES:
            queue_name = f"{exchange}.{IDENTIFIER}"
            channel.basic_consume(queue=queue_name, on_message_callback=callback)

        print(' [*] Esperando mensajes. Para salir, presiona CTRL+C')
        channel.start_consuming()

    except KeyboardInterrupt:
        print("Programa interrumpido por el usuario.")

    finally:
        connection.close()  # Cierra la conexión

if __name__ == "__main__":
    consumir_eventos()