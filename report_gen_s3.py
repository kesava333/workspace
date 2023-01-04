import json
import boto3
import re
import uuid
import time
import random
from datetime import datetime, timedelta
import os
import csv

bucketregion_name='ap-south-1'
# Mention the days to fetch the report in Days from Today
reportPeriod=5
bucketName="report-instancemani"

def lambda_handler(event, context):
    
    time=datetime.now()
    s3client = boto3.client('s3',region_name=bucketregion_name)
    
    header = ['InstanceID', 'Region', 'Status', 'Hours']
    
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
                        {'Name': str(iId), 'Value': str(iStatus)}
                    ])
            for r in response['Datapoints']:
                return(iId,region_name['RegionName'],statusToCheck,r['Sum'])
    
    
                
    client = boto3.client('ec2')
    
    for region_name in client.describe_regions()['Regions']:

        
        ec2 = boto3.resource('ec2',region_name=region_name['RegionName'])
        cloudwatch = boto3.client('cloudwatch',region_name=region_name['RegionName'])
        
        for instance in ec2.instances.all():
            id,state=instance.id,instance.state['Name']
        
            report.append(get_response(id,state))
        
        temp_csv_file = csv.writer(open("/tmp/csv_file.csv", "w+"))
        temp_csv_file.writerow(["Account Name", "Month", "Cost"])
        
        
        fin_report=[list(dimension) for dimension in list(report)]
        stamp="instanceSummaryReport-"+str(time.year)+"-"+str(time.month)+"-"+str(time.day)+"-"+str(time.hour)+":"+str(time.minute)
        
        with open('/tmp/'+str(stamp)+"."+'csv', 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            
            for data in fin_report:
               writer.writerow(data)
