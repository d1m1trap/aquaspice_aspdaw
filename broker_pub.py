import os
import random
import time
import ssl
from paho.mqtt import client as mqtt_client
from dotenv import load_dotenv

client_id = f'subscribe-{random.randint(0, 100)}'

load_dotenv()

broker_url = os.environ.get("BROKER_HOST")
broker_port = int(os.environ.get("BROKER_PORT"))
username = os.environ.get("BROKER_USER")
password = os.environ.get("BROKER_PASS")
topic_in = os.environ.get("BROKER_TOPIC_IN")
topic_out = os.environ.get("BROKER_TOPIC_OUT")

ca_certificate = "letsencrypt-aquaspice.crt"
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)

    client.tls_set(
        ca_certs=ca_certificate,
        cert_reqs=ssl.CERT_REQUIRED,
        tls_version=ssl.PROTOCOL_TLSv1_2,
        ciphers=None
    )

    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker_url, broker_port)
    return client


topic = topic_out
def subscribe(client: mqtt_client, topic=topic):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        # received_messages.append(msg.payload.decode())

    client.subscribe(topic)
    client.on_message = on_message

def publish(client):
    msg_count = 1
    while True:
        time.sleep(1)
        msg = f"messages: {msg_count}"
        result = client.publish(topic, msg)
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")
        msg_count += 1
        if msg_count > 2:
            break


def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)
    # subscribe(client)
    client.loop_stop()


if __name__ == '__main__':
    run()