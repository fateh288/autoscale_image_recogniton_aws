#!/bin/bash
export AWS_SHARED_CREDENTIALS_FILE=/home/ubuntu/.aws/credentials
touch /home/ubuntu/userdata.txt
pip3 install boto3
pip3 install torch
pip3 install numpy
cd /home/ubuntu/autoscale_image_recogniton_aws/app_tier
/usr/bin/python3 image_classifier.py 2>&1 | tee /home/ubuntu/userdata.txt