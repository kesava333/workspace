import json
import boto3
import re
import uuid
import time
import random
from datetime import datetime, timedelta
import os
import csv

# Mention the days to fetch the report in Days from Today
reportPeriod=5


def lambda_handler(event, context):
    
    time=datetime.now()
    s3client = boto3.client('s3',region_name=bucketregion_name)
    
    header = ['InstanceID', 'Region', 'Status', 'Hours']
    
    statusToCheck='running'
    
    report=[]
    
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
    
                
    client = boto3.client('ec2')
    
    for region_name in client.describe_regions()['Regions']:

        
        ec2 = boto3.resource('ec2',region_name=region_name['RegionName'])
        cloudwatch = boto3.client('cloudwatch',region_name=region_name['RegionName'])
        
        for instance in ec2.instances.all():
            id,state=instance.id,instance.state['Name']
            print("Pushing report for instance: "+ id )
        
            if state == 'running' or 'pending':
                publishing_metrics(1)
                print("Instance is Running, Status Updated to cloudwatch")
            elif state == 'stopping' or 'stopped':
                publishing_metrics(0)
                print("Instance is Stopped, Status Updated to cloudwatch")
        
      
