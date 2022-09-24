import os
from flask import Flask, request
import boto3
import numpy as np
import sys
import threading
import time
import auto_scaler

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
            MaxNumberOfMessages=5,
            WaitTimeSeconds=5,
        )
        if 'Messages' in response:
            messages = response['Messages']

            for resp in messages:
                response_receipt_handle = resp['ReceiptHandle']
                image_name,label = resp['Body'].split(":")
                response_map[image_name] = label
                delete_from_response_queue_resp = sqs_client.delete_message(
                    QueueUrl=response_queue_url,
                    ReceiptHandle=response_receipt_handle,
                )
                print("deleted "+image_name+":"+label+" from response queue")
        time.sleep(5)


response_queue_thread = threading.Thread(target=response_queue_polling_service)
response_queue_thread.setDaemon(True)
response_queue_thread.start()

auto_scaler_thread = threading.Thread(target=auto_scaler.auto_scaling_service)
auto_scaler_thread.setDaemon(True)
auto_scaler_thread.start()


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
    if filename not in response_map:
        client.upload_fileobj(f, 'imagesbucketcse546', filename)
        sqs_client.send_message(
            QueueUrl=request_queue_url,
            MessageBody=filename
        )
    res = get_result(filename)
    print("filename=",filename,"res=",res, file=sys.stderr)
    return res
