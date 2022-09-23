import os
import boto3
import threading
import time
import json
import subprocess

os.environ['AWS_PROFILE'] = "baadal"
os.environ['AWS_DEFAULT_REGION'] = "us-east-1"

request_queue_url = 'https://sqs.us-east-1.amazonaws.com/693518781741/image_classification_queue'

response_queue_url = "https://sqs.us-east-1.amazonaws.com/693518781741/image_classification_response_queue"

sqs_client = boto3.client('sqs', region_name='us-east-1')

s3_client = boto3.client('s3', region_name='us-east-1')

with open('/home/ubuntu/classifier/imagenet-labels.json') as f:
    valid_labels = set(json.load(f))

def classify_service():
    def is_valid_inferred_class(inf_class):
        if inf_class in valid_labels:
            return True
        print("inf_class:",inf_class, " not found")
        return False

    response = sqs_client.receive_message(
        QueueUrl=request_queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10,
    )
    #print(response)
    if 'Messages' in response:
        request_receipt_handle = response['Messages'][0]['ReceiptHandle']
        image_name = response['Messages'][0]['Body']
        print("processing"+image_name, flush=True)
        image_location = '/home/ubuntu/images/'
        img_abs_path = f'{image_location}{image_name}'
        s3_client.download_file('imagesbucketcse546',image_name,image_location)
        cmd = f"sudo -u ubuntu /usr/bin/python3 /home/ubuntu/classifier/image_classification.py {img_abs_path}"
        print("cmd=",cmd, flush=True)
        image_classifier_command_output_copy = subprocess.check_output(cmd, shell=True)
        image_classifier_command_output = image_classifier_command_output_copy.decode("utf-8") 
        im_name, inferred_class = image_classifier_command_output.replace("\n","").split(",")
        print(im_name, inferred_class, flush=True)


        if is_valid_inferred_class(inferred_class):
            #TODO check Body param in the s3 bucket whether visible or not
            s3_client.put_object(Bucket='classificationresultscse546', Key=im_name, Body=image_classifier_command_output_copy, ContentType = "text/plain")
            
            delete_from_request_queue_resp = sqs_client.delete_message(
                QueueUrl=request_queue_url,
                ReceiptHandle=request_receipt_handle,
            )
            
            print("deleted "+image_name+" from request queue", flush=True)
            
            send_to_response_queue_resp = sqs_client.send_message(
                QueueUrl=response_queue_url,
                MessageBody=image_name+":"+inferred_class
            )
            print("sent "+image_name+":"+inferred_class+" to response queue", flush=True)

print("Starting classification service", flush=True)
while True:        
    classify_service()