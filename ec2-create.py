#lambda to luanch EC2
#Created by Kesava Ginjupalli (kginjupalli@clearpath.ai)


import boto3
import os
ec2 = boto3.resource('ec2')

INSTANCE_TYPE = os.environ['INSTANCE_TYPE']               #These will be environment variables that we must specify in lambda
KEY_NAME = os.environ['KEY_NAME']
AMI=os.environ['AMI']
SUBNET_ID=os.environ['SUBNET_ID']

def lambda_handler(event, context):                       #Start of our function
    instance = ec2.create_instances(
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_NAME,
        ImageId=AMI,
        SubnetId=SUBNET_ID,
        SecurityGroupIds=[
                    'sg-0c94de36f25b5b96c', 'sg-06eb57a26f1b4b21f'
                ],

        MaxCount=1,
        MinCount=1,
        TagSpecifications=[{                              #This creates a tag for our resource
            'ResourceType': 'instance',
            'Tags': [{'Key': 'Name','Value': 'FleetManager-226'}]
        }]   
    )
    print("New instance created:", instance[0].id)
