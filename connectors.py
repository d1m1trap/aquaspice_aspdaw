# Step 1: Import the all necessary libraries and SDK commands.
import os
import boto3
import botocore


# Step 2: The new session validates your request and directs it to your Space's specified endpoint using the AWS SDK.
def connects3():
    session = boto3.session.Session()
    client = session.client('s3',
                            endpoint_url='https://fra1.digitaloceanspaces.com',
                            # Find your endpoint in the control panel, under Settings. Prepend "https://".
                            config=botocore.config.Config(s3={'addressing_style': 'virtual'}),
                            # Configures to use subdomain/virtual calling format.
                            region_name='fra1',  # Use the region in your endpoint.
                            aws_access_key_id=os.getenv('SPACES_KEY'),
                            # Access key pair. You can create access key pairs using the control panel or API.
                            aws_secret_access_key=os.getenv(
                                'SPACES_SECRET'))  # os.getenv('SPACES_SECRET')) # Secret access key defined through an environment variable.
    return client


# response = client.list_buckets()
# print(response)


# Create a new Space.
# client.create_bucket(Bucket='my-new-space')

# List all buckets on your account.
# response = client.list_buckets()
# spaces = [space['Name'] for space in response['Buckets']]
# print("Spaces List: %s" % spaces)

# Step 3: Call the put_object command and specify the file to upload.
def upload_model(object_key='models/DataCT3201/mv_isft.joblib',
                 local_file_path='../models/DataCT3201/mv_isft.joblib'):
    print("Upload")
    # object_key = 'models/DataCT3201/mv_isft.joblib'  # Specify the object key (path) in the bucket
    # local_file_path = '../models/DataCT3201/mv_isft.joblib'
    client = connects3()
    client.put_object(Bucket='aspbucket',
                      # The path to the directory you want to upload the object to, starting with your Space name.
                      Key=object_key,  # Object key, referenced whenever you want to access this file later.
                      Body=local_file_path,
                      ACL='private',
                      )
    client.close()


def download_model(object_key='models/DataCT3201/mv_isft.joblib',
                   local_path='models/DataCT3201/mv_isft.joblib'):
    print("Download")
    client = connects3()
    # Retrieve the object from the bucket
    client.download_file('aspbucket', object_key, local_path)


# event/DOWBO/analytics/in
def connect_broker():
    import paho.mqtt.client as paho
    from dotenv import load_dotenv

    load_dotenv()

    # Define the broker URL and port
    broker_url = os.environ.get("BROKER_HOST")
    broker_port = int(os.environ.get("BROKER_PORT"))
    username = os.environ.get("BROKER_USER")
    password = os.environ.get("BROKER_PASS")

    def on_subscribe(client, userdata, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_message(client, userdata, msg):
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = paho.Client()
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.connect(broker_url, broker_port)
    # while not client.is_connected():
    #     client.loop()
    #     print(client.is_connected())
    #
    # print(client.is_connected())
    # client.disconnect()
    return client

    # client.subscribe('event/BASF/#', qos=1)

    # print(client.is_connected())
    # client.loop_forever()


connect_broker()
