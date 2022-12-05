import json
import boto3
import re
import uuid
import time
import random
from datetime import datetime, timedelta
import os

region_name='us-east-2'

def lambda_handler(event, context):
    
    ec2 = boto3.resource('ec2',region_name=region_name)
    cloudwatch = boto3.client('cloudwatch',region_name=region_name)
    
    for instance in ec2.instances.all():
        id,state=instance.id,instance.state['Name']
        print("Pushing report for instance: "+ id )
        
        def publishing_metrics(data):
            response = cloudwatch.put_metric_data(
               MetricData = [
               {
                    'MetricName': 'InstanceStatus',
                    'Dimensions': [
                        {
                            'Name': str(id),
                            'Value': str(state)
                        },
                     ],
                        'Unit': 'None' ,
                        'Value': data
                },
                ],
                Namespace = 'InstanceStatusReport')
       
        if state == 'running' or 'pending':
            publishing_metrics(1)
            print("Instance is Running, Status Updated to cloudwatch")
        elif state == 'stopping' or 'stopped':
            publishing_metrics(0)
            print("Instance is Stopped, Status Updated to cloudwatch")
        
        response = cloudwatch.get_metric_statistics(
                Namespace = 'InstanceStatusReport',
                Period = 3000,
                StartTime = datetime.utcnow() - timedelta(seconds = 600),
                EndTime = datetime.utcnow(),
                MetricName = 'InstanceStatus',
                 Statistics=[
                "SampleCount",
            ],
                Dimensions = [
                    {'Name': str(id), 'Value': str(state)}
                ])
        for r in response['Datapoints']:
            print(r['SampleCount'])
