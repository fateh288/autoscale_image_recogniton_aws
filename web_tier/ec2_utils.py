import boto3
import os
import time
import sys

os.environ['AWS_PROFILE'] = "baadal"
os.environ['AWS_DEFAULT_REGION'] = "us-east-1"

ec2_client = boto3.client('ec2', region_name='us-east-1')

def create_app_tier_instance(instance_name):
    with open('app_tier_user_data.sh', 'r') as f:
        to_execute_commands = f.read()
    
    print(f"Execution commands on remote instance: {to_execute_commands}")

    start_time = time.time()
    print("creating app tier instance")
    resp = ec2_client.run_instances(
        ImageId='ami-0c3e264f3230f049f',
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName='cloud_computing',
        SecurityGroupIds=['sg-01ce524eed3b740a8'],
        SubnetId='subnet-086decbe62844f66d',
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': instance_name
                    },
                ]
            }
        ],
        UserData=to_execute_commands
    )

    #https://stackoverflow.com/questions/49622575/schedule-to-start-an-ec2-instance-and-run-a-python-script-within-it

    INSTANCE_ID = resp['Instances'][0]['InstanceId']
    while True:
        response = ec2_client.describe_instance_status(InstanceIds=[INSTANCE_ID], IncludeAllInstances=True)
        state = response['InstanceStatuses'][0]['InstanceState']
        print(f"Status: {state['Code']} - {state['Name']}", file=sys.stderr)
        # https://docs.aws.amazon.com/sdk-for-ruby/v2/api/Aws/EC2/Types/InstanceState.html
        # If status is 16 ('running') or >=32 ('terminated'/'stopped'etc), then proceed, else, wait 5 seconds and try again
        if state['Code'] == 16:
            print(f"Instance {INSTANCE_ID} is running", file=sys.stderr)
            break
        elif state['Code'] >=32:
            print(f"Instance {INSTANCE_ID} has been stopped/terminated", file=sys.stderr)
            break
        else:
            time.sleep(5)
    print("instance created in ",time.time()-start_time," seconds", file=sys.stderr)
    return INSTANCE_ID

def get_instance_statuses():
    # TODO: correct this.. currently only giving running instances
    instance_status_map = {}
    resp = ec2_client.describe_instance_status(IncludeAllInstances=True)
    #print("resp=",resp)
    for instance in resp['InstanceStatuses']:
        instance_status_map[instance['InstanceId']] = instance['InstanceState']['Name']
    return instance_status_map

def terminate_instances(instance_id_list):
    ec2_client.terminate_instances(
        InstanceIds=instance_id_list
    )
