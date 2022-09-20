import os
from flask import Flask, request
import boto3
import numpy as np
import sys
import threading
import time

os.environ['AWS_PROFILE'] = "baadal"
os.environ['AWS_DEFAULT_REGION'] = "us-east-1"

app = Flask(__name__)

client = boto3.client('s3', region_name='us-east-1')

sqs_client = boto3.client('sqs', region_name='us-east-1')

request_queue_url = 'https://sqs.us-east-1.amazonaws.com/693518781741/image_classification_queue'

response_queue_url = "https://sqs.us-east-1.amazonaws.com/693518781741/image_classification_response_queue"

response_map = {}

def response_queue_polling_service():
    print("response queue polling service started")
    while True:
        response = sqs_client.receive_message(
            QueueUrl=response_queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=5,
        )
        if 'Messages' in response:
            messages = response['Messages']

            for resp in messages:
                request_receipt_handle = resp['ReceiptHandle']
                image_name,label = resp['Body'].split(":")
                response_map[image_name] = label

            print("response_map=",response_map, file=sys.stderr)
        time.sleep(5)

thread = threading.Thread(target=response_queue_polling_service)
thread.setDaemon(True)
thread.start()

def get_result(image_name):
    while True:
        if image_name in response_map:
            return response_map[image_name]
        time.sleep(1)

@app.route("/classify_image", methods=['POST'])
def classify_image():
    # get image sent in this request
    f = request.files['myfile']
    filename = f.filename 
    print(filename, file=sys.stderr)
    client.upload_fileobj(f, 'imagesbucketcse546', filename)
    sqs_client.send_message(
        QueueUrl=request_queue_url,
        MessageBody=filename
    )
    res = get_result(filename)
    print("filename=",filename,"res=",res, file=sys.stderr)
    return res
