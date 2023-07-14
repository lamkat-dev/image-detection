from confluent_kafka import Producer, Consumer

# This script works on Windows.

def produce_message(bootstrap_servers, topic, message):
    # Create producer configuration
    producer_config = {'bootstrap.servers': bootstrap_servers}

    # Create a Kafka producer
    producer = Producer(producer_config)

    # Produce the message to the specified topic
    producer.produce(topic, message.encode('utf-8'))

    # Flush producer messages
    producer.flush()
    # producer.close()


def consume_messages(bootstrap_servers, topic):
    # Create consumer configuration
    consumer_config = {
        'bootstrap.servers': bootstrap_servers,
        'group.id': 'my-consumer-group',
        'auto.offset.reset': 'earliest'
    }

    # Create a Kafka consumer
    consumer = Consumer(consumer_config)

    # Subscribe to the specified topic
    consumer.subscribe([topic])

    try:
        while True:
            # Poll for new messages
            message = consumer.poll(1.0)

            if message is None:
                continue

            if message.error():
                print(f'Consumer error: {message.error()}')
                continue

            # Print the consumed message
            print(f'Consumed message: {message.value().decode("utf-8")}')

    except KeyboardInterrupt:
        pass

    finally:
        # Close the consumer
        consumer.close()


# Configure the Kafka cluster connection details
bootstrap_servers = 'localhost:9092'
topic = 'test-topic'

# Produce a message
print('Time to produce a message!')
produce_message(bootstrap_servers, topic, 'Hello, Kafka!')

# Consume messages
print('Time to consume a message!')
consume_messages(bootstrap_servers, topic)