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
                            aws_secret_access_key=os.getenv('SPACES_SECRET'))  # os.getenv('SPACES_SECRET')) # Secret access key defined through an environment variable.
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
                      Body=local_file_path,  # The object's contents.
                      ACL='private',  # Defines Access-control List (ACL) permissions, such as private or public.
                      # Metadata={ # Defines metadata tags.
                      #     'x-amz-meta-my-key': 'your-value'
                      # }
                      )
    client.close()


def download_model(object_key='models/DataCT3201/mv_isft.joblib',
                   local_path='models/DataCT3201/mv_isft.joblib'):
    print("Download")
    client = connects3()
    # Retrieve the object from the bucket
    client.download_file('aspbucket', object_key, local_path)
