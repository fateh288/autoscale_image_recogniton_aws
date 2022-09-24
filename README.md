nohup flask --app controller run --host=172.31.94.81 -p 8080

python3 multithread_workload_generator.py --num_request 100 --url 'http://172.31.94.81:5000/classify_image' --image_folder imagenet-100/