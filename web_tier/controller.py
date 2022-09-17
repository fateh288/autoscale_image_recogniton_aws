from flask import Flask, request
import boto3
import numpy as np
import sys

app = Flask(__name__)

client = boto3.client('s3', region_name='us-east-1')


@app.route("/classify_image", methods=['POST'])
def classify_image():
    # get image sent in this request
    f = request.files['myfile']
    filename = f.filename 
    print(filename, file=sys.stderr)

    client = boto3.client('s3', region_name='us-east-1')

    client.upload_file('images/image_0.jpg', 'mybucket', 'image_0.jpg')
    return filename
