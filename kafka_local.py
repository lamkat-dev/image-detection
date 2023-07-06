import logging
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Producer


def receipt(err, msg):
    if err is not None:
        print('Error: {}'.format(err))
    else:
        message = 'Produced message on topic {} with value of {}\n'.format(msg.topic(), msg.value().decode('utf-8'))
        logger.info(message)
        print(message)


if __name__ == '__main__':
    # Set up Kafka logging
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename='producer.log',
                        filemode='w')

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create admin client
    admin_client = AdminClient({"bootstrap.servers": "localhost:9092"})

    # Create Topic list, append new topic
    topic_list = []
    topic_list.append(NewTopic("test", 1, 1))
    # Publish topic list to admin client
    admin_client.create_topics(topic_list)

    # Create kafka Producer p
    p = Producer({'bootstrap.servers':'localhost:9092'})

    message = "this is a test message"

    p.poll(1)
    p.produce("test", message.encode('utf-8'), callback=receipt)
    p.flush()

