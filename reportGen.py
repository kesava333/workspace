import json
import boto3
import re
import uuid
import time
import random
from datetime import datetime, timedelta
import os
import csv

region_name='ap-south-1'
bucketName=""
time=datetime.now()
client = boto3.client('s3')


ec2 = boto3.resource('ec2',region_name=region_name)
cloudwatch = boto3.client('cloudwatch',region_name=region_name)
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

def get_response(iId, iStatus):
        response = cloudwatch.get_metric_statistics(
                Namespace = 'InstanceStatusReport',
                Period = 18000,
                StartTime = datetime.utcnow() - timedelta(seconds = 10800),
                EndTime = datetime.utcnow(),
                MetricName = 'InstanceStatus',
                 Statistics=[
                "Sum",
            ],
                Dimensions = [
                    {'Name': str(iId), 'Value': str(iStatus)}
                ])
        for r in response['Datapoints']:
            return(iId,region_name,statusToCheck,r['Sum'])


for instance in ec2.instances.all():
    id,state=instance.id,instance.state['Name']
    print("Pushing report for instance: "+ id )

    if state == 'running' or 'pending':
        publishing_metrics(1)
        print("Instance is Running, Status Updated to cloudwatch")
    elif state == 'stopping' or 'stopped':
        publishing_metrics(0)
        print("Instance is Stopped, Status Updated to cloudwatch")

    report.append(get_response(id,state))

temp_csv_file = csv.writer(open("/tmp/csv_file.csv", "w+"))
temp_csv_file.writerow(["Account Name", "Month", "Cost"])


fin_report=[list(dimension) for dimension in list(report)]
stamp="instanceSummaryReport-"+str(time.year)+"-"+str(time.month)+"-"+str(time.day)+"-"+str(time.hour)+":"+str(time.minute)


with open(str(stamp)+"."+'csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for data in fin_report:
       writer.writerow(data)

client.upload_file( str(stamp)+"."+'csv', bucketName, str(stamp)+"."+'csv')
