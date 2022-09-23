#!/bin/bash
su - ubuntu
cd /home/ubuntu
export AWS_SHARED_CREDENTIALS_FILE=/home/ubuntu/.aws/credentials
mkdir /home/ubuntu/images
sudo touch /home/ubuntu/userdata.txt
/usr/bin/pip3 install boto3
/usr/bin/pip3 install torch
/usr/bin/pip3 install numpy
cd /home/ubuntu/classifier/
sudo -u ubuntu /usr/bin/python3 /home/ubuntu/autoscale_image_recogniton_aws/app_tier/image_classifier.py 2>&1 | sudo tee /home/ubuntu/userdata.txt
