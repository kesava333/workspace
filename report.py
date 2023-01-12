import json
import boto3
import re
import uuid
import time
import random
from datetime import datetime, timedelta
import os
import csv
import sys

bucketregion_name='us-east-2'
# Mention the days to fetch the report in Days from Today
reportPeriod=1
bucketName="ec2-cost-monitoring-s3"
regionToFilter='us-east-2'

ec2res = boto3.resource('ec2',region_name="us-east-2")

def get_tag(id):
    for instance in ec2res.instances.all():
        if instance.id == id:
            for tag in instance.tags:
                if tag['Key'] == 'Name':
                    return tag['Value']

time=datetime.now()
s3client = boto3.client('s3',region_name=bucketregion_name)

header = ['Name','InstanceID', 'Region', 'Status', 'Hours']

statusToCheck='running'

report=[]

def get_response(iId, iStatus):
        response = cloudwatch.get_metric_statistics(
                Namespace = 'InstanceStatusReport',
                Period = 2592000,
            # StartTime = datetime.utcnow() - timedelta(seconds = 10800),
                StartTime =  datetime.now() - timedelta(days=reportPeriod),
                EndTime = datetime.utcnow(),
                MetricName = 'InstanceStatus',
                Statistics=[
                "Sum",
            ],
                Dimensions = [
                    {'Name': str(iId), 'Value': str(statusToCheck)}
                ])
        
        for r in response['Datapoints']:
            return(get_tag(iId),iId,regionToFilter,str(iStatus),r['Sum'])


            
client = boto3.client('ec2')

    
ec2 = boto3.resource('ec2',region_name=regionToFilter)
cloudwatch = boto3.client('cloudwatch',region_name=regionToFilter)

for instance in ec2.instances.all():
    id,state=instance.id,instance.state['Name']
    report.append(get_response(id,state))

temp_csv_file = csv.writer(open("/tmp/csv_file.csv", "w+"))

fin_report=[list(dimension) for dimension in list(report)]
stamp="instanceSummaryReport-"+str(time.year)+"-"+str(time.month)+"-"+str(time.day)+"-"+str(time.hour)+":"+str(time.minute)


with open('/tmp/'+str(stamp)+"."+'csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    
    for data in fin_report:
      writer.writerow(data)
s3client.upload_file('/tmp/'+str(stamp)+"."+'csv', bucketName, str(stamp)+"."+'csv')
        
