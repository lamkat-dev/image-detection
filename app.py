import os
#from dotenv import load_dotenvimport time
import uuid
import logging
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Producer
import cv2
import psycopg2
import psycopg2.extras
import json
from ultralytics import YOLO

logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename='producer.log',
                        filemode='w')

logger = logging.getLogger()
logger.setLevel(logging.INFO)
admin_client = AdminClient({"bootstrap.servers": "localhost:9092"})


def getAFrame(camera_ip):
    """Connect to a network camera, capture and return an image."""
    cv2.CAP_PROP_BUFFERSIZE = 1
    vidcap = cv2.VideoCapture(camera_ip)

    if vidcap.isOpened():
        print("Successful Connection to Camera")
    else:
        print("Connection to Camera Failed")
        return None

    time.sleep(1)
    status, frame = vidcap.read()

    if status:
        print("Image retrieved Successfully")
        return frame
    else:
        print("Failed to retrieve Image")
        # TODO: return bus.jpg for predictions if image retrieval fails
        return None


def saveFrame(VID_CAP_DIR, image):
    """Save image locally.

    Keyword Arguments
    image -- the image to save
    """
    psycopg2.extras.register_uuid()
    id = uuid.uuid4()
    filepath = str(VID_CAP_DIR) + str(id) + ".jpg"
    print(filepath)
    status = cv2.imwrite(filepath, image)
    if status:
        print("Image saved successfully")
        return id, filepath
    else:
        print("Image did not save correctly")
        return None, None


def predictContents(image):
    """Predict image contents and return predictions.

    Keyword Arguments:
    image -- the image file to detect objects from
    """
    model = YOLO('yolov8n.pt')
    results = model.predict(image, conf=.5, save_conf=True)
    if results[0].boxes.cls.nelement() == 0:
        return None

    elif results[0].boxes.cls.nelement() == 1:
        predictions = model.names[int(results[0].boxes.cls)]
        return predictions
    else:
        predictions = []
        for result in results[0].boxes.cls.numpy():
            predictions.append(model.names[int(result)])
        print(predictions)
        return predictions


def kafka_producer():
    """Initiate Kafka Producer"""
    p = Producer({'bootstrap.servers':'localhost:9092'})
    print('Kafka Producer has been initiated...')
    return p


def receipt(err, msg):
    if err is not None:
        print('Error: {}'.format(err))
    else:
        message = 'Produced message on topic {} with value of {}\n'.format(msg.topic(), msg.value().decode('utf-8'))
        logger.info(message)
        print(message)


def write_data(id, filepath, contents, producer):
    data = {
        'uuid': str(id),
        'filepath': filepath,
        'contents': contents
    }
    dump = json.dumps(data)
    producer.poll(1)
    producer.produce('test', dump.encode('utf-8'), callback=receipt)
    producer.flush()
    time.sleep(3)


if __name__ == '__main__':
    """Use a Machine Learning model to predict the contents of an image.
    
    Connect to a camera on a network.
    Capture a frame from the camera.
    Save captured frame to local file system.
    Predict contents of the image.
    Writes prediction(s) to a database."""
    load_dotenv("app.env")
    CAMERA_IP = os.getenv('CAMERA_IP_ADDRESS')
    frame = getAFrame(CAMERA_IP)
    VID_CAP_DIR = os.getenv('VID_CAP_DIR')
    id, path = saveFrame(VID_CAP_DIR, frame)
    predictions = predictContents(frame)
    #predictions = predictContents("bus.jpg")


    # Create Topic list, append new topic
    topic_list = []
    topic_list.append(NewTopic("test", 1, 1))
    # Publish topic list to admin client
    admin_client.create_topics(topic_list)
    prod = kafka_producer()
    write_data(id, path, predictions, prod)
    # TODO: close camera
    # TODO: loop
