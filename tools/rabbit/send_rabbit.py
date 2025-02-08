import argparse
import pika

# Configuración de RabbitMQ con credenciales
RABBITMQ_HOST = 'localhost'  # Reemplaza con tu host de RabbitMQ
RABBITMQ_USER = 'user'  # Reemplaza con tu usuario de RabbitMQ
RABBITMQ_PASSWORD = 'password'  # Reemplaza con tu contraseña de RabbitMQ
EXCHANGE_NAME = 'preguntas'  # Reemplaza con el nombre de tu cola

def enviar_mensaje(mensaje):
    """Envía un mensaje a una cola de RabbitMQ con credenciales."""

    # Credenciales de RabbitMQ
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)

    # Conexión a RabbitMQ con credenciales
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
    channel = connection.channel()

    # Declaración de la cola (se asegura de que la cola exista)
    channel.exchange_declare(exchange=EXCHANGE_NAME,exchange_type="fanout")

    try:
        # Envía el mensaje a la cola
        channel.basic_publish(exchange=EXCHANGE_NAME, routing_key="", body=mensaje)
        print(f"Mensaje enviado: {mensaje}")

    except Exception as e:
        print(f"Error al enviar el mensaje: {e}")

    finally:
        connection.close()  # Cierra la conexión después de enviar el mensaje

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Envía un mensaje a una cola de RabbitMQ con credenciales.")
    parser.add_argument("mensaje", help="El mensaje a enviar.")
    args = parser.parse_args()

    mensaje_texto = args.mensaje
    enviar_mensaje(mensaje_texto)