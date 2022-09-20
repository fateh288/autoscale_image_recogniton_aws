import os
import boto3
import threading
import time

os.environ['AWS_PROFILE'] = "baadal"
os.environ['AWS_DEFAULT_REGION'] = "us-east-1"

request_queue_url = 'https://sqs.us-east-1.amazonaws.com/693518781741/image_classification_queue'

response_queue_url = "https://sqs.us-east-1.amazonaws.com/693518781741/image_classification_response_queue"

sqs_client = boto3.client('sqs', region_name='us-east-1')

def classify_service():
    
    def is_valid_inferred_class(cls):
        if cls in ["cat", "dog"]:
            return True
        return False

    response = sqs_client.receive_message(
        QueueUrl=request_queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10,
    )
    #print(response)
    request_receipt_handle = response['Messages'][0]['ReceiptHandle']
    image_name = response['Messages'][0]['Body']
    print("processing"+image_name)

    inferred_class = "cat"
    
    if is_valid_inferred_class(inferred_class):
        delete_from_request_queue_resp = sqs_client.delete_message(
            QueueUrl=request_queue_url,
            ReceiptHandle=request_receipt_handle,
        )
        print("deleted "+image_name+" from request queue")
        send_to_response_queue_resp = sqs_client.send_message(
            QueueUrl=response_queue_url,
            MessageBody=image_name+":"+inferred_class
        )
        print("sent "+image_name+":"+inferred_class+" to response queue")


thread = threading.Thread(target=classify_service)
thread.start()
time.sleep(10)