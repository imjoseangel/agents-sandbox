from confluent_kafka import Consumer, KafkaError
import json

# Configuración de Kafka
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'  # Reemplaza con tus servidores Kafka
TOPICS = ["preguntas","respuestas"]  # Reemplaza con un patrón para los topics que quieres escuchar

GROUP_ID = 'mi_grupo'  # Reemplaza con un ID de grupo para el consumidor

def consumir_eventos():
    """Consume mensajes de topics que coinciden con un patrón y los imprime por pantalla."""

    # Configuración del consumidor
    settings = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': GROUP_ID,
        'auto.offset.reset': 'latest',  # Consume desde el último mensaje
        'enable.auto.commit': False,  # Permite que el consumidor confirme automáticamente los mensajes
    }

    # Inicializa el consumidor de Confluent Kafka
    consumer = Consumer(settings)

    # Suscribe a topics que coinciden con un patrón
    consumer.subscribe(TOPICS)


    try:
        # Bucle infinito para leer mensajes continuamente
        while True:
            msg = consumer.poll(1.0)  # Espera un segundo por un mensaje

            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print('End of partition reached')
                    continue
                else:
                    print(f"Error: {msg.error()}")  # Imprime el error
                    # Aquí puedes decidir si quieres salir del bucle o continuar
                    # break  # Rompe el bucle si quieres salir en caso de error
                    continue  # Continua con el siguiente mensaje.

            evento = msg.value()
            topic = msg.topic()
            print(f"Evento recibido en topic {topic}: {evento}")

    except KeyboardInterrupt:
        print("Programa interrumpido por el usuario.")

    finally:
        consumer.close()  # Cierra el consumidor

if __name__ == "__main__":
    consumir_eventos()