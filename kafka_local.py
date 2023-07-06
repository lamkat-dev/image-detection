from confluent_kafka import Producer
import logging


def receipt(logger, err, msg):
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

    # Create kafka Producer p
    p = Producer({'bootstrap.servers':'localhost:9092'})
