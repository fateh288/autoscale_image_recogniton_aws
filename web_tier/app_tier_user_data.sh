#!/bin/bash
cd /home/ubuntu/classifier/
sudo -u ubuntu /usr/bin/python3 /home/ubuntu/autoscale_image_recogniton_aws/app_tier/image_classifier.py 2>&1 | sudo tee /home/ubuntu/userdata.txt
