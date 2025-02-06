from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from confluent_kafka import Consumer, Producer, KafkaError
from langchain_core.prompts import ChatPromptTemplate

# Configuración de Kafka
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'  # Reemplaza con tus servidores Kafka
INPUT_TOPIC = 'preguntas'
OUTPUT_TOPIC = 'respuestas'
GROUP_ID = 'agente_colores' # Reemplaza con un ID de grupo para el consumidor

# Configuración de Ollama
OLLAMA_BASE_URL = "http://localhost:11434" # Reemplaza con la URL de tu instancia de Ollama
MODEL = "gemma2" # Reemplaza con el modelo que quieres usar


def main():
    # Inicialización de LangChain y Ollama
    llm = ChatOllama(base_url=OLLAMA_BASE_URL, model=MODEL, verbose=True)

    # Configuración del consumidor de Kafka
    consumer_settings = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': GROUP_ID,
        'auto.offset.reset': 'latest',  # Consume desde el último mensaje
        'enable.auto.commit': False,  # Permite que el consumidor confirme automáticamente los mensajes
    }
    consumer = Consumer(consumer_settings)
    consumer.subscribe([INPUT_TOPIC])

    # Configuración del productor de Kafka
    producer_settings = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    }
    producer = Producer(producer_settings)


    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print('End of partition reached')
                    continue
                else:
                    print(f"Error: {msg.error()}")
                    continue

            event = msg.value()
            print(f"Evento recibido: {event}")

            try:
                messages = [
                    SystemMessage("""You are in charge of providing the letter R.
                                  Only answer "R" if you are asked to spell a word with the letter R in it. Any other case answer "Pass".
                                  Do not give any extra information
                                """
                        ),
                    HumanMessage(f"{event}"),
                ]

                ollama_response = llm.invoke(messages)  # El LLM ahora recibe un string
                
                print(ollama_response)
               
                string_response = ollama_response.content
                print(f"Respuesta de Ollama: {string_response}")
                
                if "Pass" not in string_response:
                    # Envío de la respuesta al topic de salida
                    producer.produce(OUTPUT_TOPIC, value=string_response)
                    producer.flush() # Asegura que el mensaje se envíe inmediatamente.
                    print(f"Respuesta enviada al topic {OUTPUT_TOPIC}")
                    consumer.commit()
            
                

            except Exception as e:
                print(f"Error al procesar el evento: {e}")

    except KeyboardInterrupt:
        consumer.close()
        print("Programa interrumpido por el usuario.")



if __name__ == "__main__":
    main()