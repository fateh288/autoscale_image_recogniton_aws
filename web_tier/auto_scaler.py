from time import time
import boto3
import os

os.environ['AWS_PROFILE'] = "baadal"
os.environ['AWS_DEFAULT_REGION'] = "us-east-1"

max_instances = 20

sqs_client = boto3.client('sqs', region_name='us-east-1')

#ec2_client = boto3.resource('ec2')

queue_url = 'https://sqs.us-east-1.amazonaws.com/693518781741/image_classification_queue'

while True:
    # get message count in queue
    attributes = sqs_client.get_queue_attributes(
        QueueUrl=queue_url,
        AttributeNames=['ApproximateNumberOfMessages']
    )
    message_count = int(attributes['Attributes']['ApproximateNumberOfMessages'])
    print(f"Message count: {message_count}")

    time.sleep(5)