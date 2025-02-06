import argparse
from confluent_kafka import Producer
import json

# Configuración de Kafka
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'  # Reemplaza con tus servidores Kafka
TOPIC_NAME = 'preguntas'  # Reemplaza con el nombre de tu topic

def enviar_mensaje(mensaje):
    """Envía un mensaje a un topic de Kafka."""

    # Configuración del productor
    settings = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    }

    # Inicializa el productor de Confluent Kafka
    producer = Producer(settings)

    try:
        # Envía el mensaje al topic
        producer.produce(TOPIC_NAME, value=mensaje)  # value= mensaje, serializado automáticamente.
        producer.flush() # Asegura que el mensaje se envíe inmediatamente.
        print(f"Mensaje enviado: {mensaje}")

    except Exception as e:
        print(f"Error al enviar el mensaje: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Envía un mensaje a un topic de Kafka.")
    parser.add_argument("mensaje", help="El mensaje a enviar.")
    args = parser.parse_args()

    mensaje_texto = args.mensaje
    enviar_mensaje(mensaje_texto)