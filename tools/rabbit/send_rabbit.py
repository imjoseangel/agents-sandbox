import argparse
import pika
import json
from cloudevents.http import CloudEvent, to_json
import uuid

# Configuración de RabbitMQ con credenciales
RABBITMQ_HOST = 'localhost'  # Reemplaza con tu host de RabbitMQ
RABBITMQ_USER = 'user'  # Reemplaza con tu usuario de RabbitMQ
RABBITMQ_PASSWORD = 'password'  # Reemplaza con tu contraseña de RabbitMQ
EXCHANGE_NAME = 'preguntas'  # Reemplaza con el nombre de tu cola

def enviar_mensaje(mensaje): # Recibe el ID del programa como argumento
    """Envía un mensaje a una cola de RabbitMQ con credenciales, formateado como CloudEvent, con UUID y subject."""

    # Credenciales de RabbitMQ
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)

    # Conexión a RabbitMQ con credenciales
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
    channel = connection.channel()

    # Declaración de la cola (se asegura de que la cola exista)
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="fanout")

    try:
        # Genera un UUID para el ID del evento
        event_id = str(uuid.uuid4())

        # Crea el CloudEvent con el UUID y el subject
        attributes = {
            "type": "com.example.mensaje.enviado",  # Reemplaza con tu tipo de evento
            "source": "/mi/aplicacion",  # Reemplaza con la fuente del evento
            "id": event_id, # Incluye el UUID como ID del evento
            "subject": event_id # Usa el ID del programa como subject
        }
        data = {"message": mensaje}
        event = CloudEvent(attributes, data)

        # Serializa el CloudEvent a JSON
        message_json = to_json(event)

        # Envía el mensaje a la cola
        channel.basic_publish(exchange=EXCHANGE_NAME, routing_key="", body=message_json)
        print(f"Mensaje enviado: {message_json}")

    except Exception as e:
        print(f"Error al enviar el mensaje: {e}")

    finally:
        connection.close()  # Cierra la conexión después de enviar el mensaje

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Envía un mensaje a una cola de RabbitMQ con credenciales, formateado como CloudEvent con UUID y subject.")
    parser.add_argument("mensaje", help="El mensaje a enviar.")
    args = parser.parse_args()

    mensaje_texto = args.mensaje
    programa_id = args.programa_id # Obtiene el ID del programa de los argumentos
    enviar_mensaje(mensaje_texto) # Pasa el ID del programa a la función