def auto_scaling_service():
    # TODO: imports not working when imported from another thread, so placed here. FInd right way to do this.
    import time
    import boto3
    import os
    import ec2_utils
    import sys

    from concurrent.futures import ThreadPoolExecutor

    os.environ['AWS_PROFILE'] = "baadal"
    os.environ['AWS_DEFAULT_REGION'] = "us-east-1"

    max_instances = 20

    sqs_client = boto3.client('sqs', region_name='us-east-1')

    queue_url = 'https://sqs.us-east-1.amazonaws.com/693518781741/image_classification_queue'

    ALWAYS_RUNNING_INSTANCE_SET = set(['i-01e169412a2fa0a74'])
    universal_instance_number = 1
    executor = ThreadPoolExecutor(max_instances)
    future_set = set()

    while True:
        # get message count in queue
        attributes = sqs_client.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=['ApproximateNumberOfMessages']
        )
        message_count = int(attributes['Attributes']['ApproximateNumberOfMessages'])
        print(f"Message count: {message_count}")
        instance_status_map = ec2_utils.get_instance_statuses()
        
        instance_count = -1 # subtract 1 for web tier instance and count only app tier instances
        for instance_id, status in instance_status_map.items():
            if status == 'running' or status == 'pending':
                instance_count += 1
        print(f"App Tier Instance count: {instance_count}")


        if message_count > instance_count:
            num_instances_to_launch = min(message_count-instance_count, max_instances-instance_count)
            if num_instances_to_launch>0:
                print(f"Launching {num_instances_to_launch} instances")
                
                for i in range(num_instances_to_launch):
                    instance_name = f'app_tier_instance_{universal_instance_number}'
                    future = executor.submit(ec2_utils.create_app_tier_instance, instance_name)
                    universal_instance_number += 1
        elif message_count == 0:
            print("No messages in queue",file=sys.stderr)
            to_terminate_list = []
            for instance_id, status in instance_status_map.items():
                if instance_id not in ALWAYS_RUNNING_INSTANCE_SET and (status == 'running' or status == 'pending'):
                    to_terminate_list.append(instance_id)
            if to_terminate_list:
                print(f"Terminating instances: {to_terminate_list}",file=sys.stderr)
                ec2_utils.terminate_instances(to_terminate_list)
                pass

        time.sleep(100)