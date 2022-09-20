flask --app controller run --host=0.0.0.0

python3 workload_generator.py --num_request 3 --url 'http://172.31.94.81:5000/classify_image' --image_folder "/home/ubuntu/CSE546_Sum22_workload_generator/imagenet-100/"