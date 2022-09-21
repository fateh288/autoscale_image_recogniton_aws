#!/bin/bash
cd /home/ubuntu/autoscale_image_recogniton_aws/app_tier
python3 image_classifier.py
touch /home/ubuntu/userdata.txt