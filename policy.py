# Created by Kesava Ginjupalli (kginjupalli@clearpath.ai)

''' 
Terminate Instances based on  TerminateDate tag and the Choices are --> Reserved , Date, Deafult
Reserved  - Don't Terminate any instance with this tag value
Date - if the date is Older than the tagged date, Terminate those instances
Default - If the instance tag value set to be default, the lambda function will keep monitoring these instances for 30 days
 & terminate them after 30 days only if the instance is not powered on for 30 days 

TerminateDate == Reserved 
	    Protected -> Dont touch
TerminateDate == Default or NoTag Value
     stopped date Older then/equal 30 -> terminate the instance
     stopped date equal to 24 => Trigger the warning email
     instance is running -> Stop it at 9PM EST
     No tags -> Stop it at 9PM EST
'''

import time
import boto3
from datetime import date
from datetime import datetime
import re
import traceback
import logging
import subprocess
import sys
from botocore.exceptions import ClientError
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from utils import filterProtectedInstances, reportGeneration, instanceSegregation, terminateUnusedInstance
from emails import sendEmailtemplate, emailListAppend

subprocess.call('pip install tabulate -t /tmp/ --no-cache-dir'.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
sys.path.insert(1, '/tmp/')
from tabulate import tabulate

current_dateTime = datetime.now()
# Account Number of target AWS Account
AccountID='709708176998'
# AWS Region will be passed as a user input
RegionList=['us-east-1']
ec2client = boto3.client('ec2', region_name='us-east-1')
ec2resource = boto3.resource('ec2', region_name='us-east-1')
# RegionList = [region['RegionName'] for region in client.describe_regions()['Regions']]


for AWSRegion in RegionList:
    ec2client = boto3.client('ec2',region_name=AWSRegion)
    ec2resource = boto3.resource('ec2',region_name=AWSRegion)
    protectedInstances=[]
    data=[]
    today = datetime.today()

    # Set the logging level
    logging.basicConfig()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # create filter for the instances in running state
    filters = [
        {
                'Name': 'instance-state-name',
                'Values': ['running','stopped']
            }
    ]
    # filter instances based on the filters above
    instances = ec2resource.instances.filter(Filters=filters)
    # Column names for the report
    col_names = ["Instance Name", "Instance ID", "Timestamp" ,
    "Instance status", "Instance Powered off", "Instance terminated" ]
    # instantiate an empty array to house the running instances
    RunningInstances = []
    StoppedInstances = []
    TerminateInstances=[]
    emailList=[]
    emails=[]
    emailTriggerInstanceList=[]

    def emailSeperatorwrapper01(emailList):
        emails = []
        for vmid in emailList:
            for instance in ec2resource.instances.all():
                if instance.instance_id == vmid and 'Email' in [t['Key'] for t in instance.tags]:
                    emails+=[t['Value'] for t in instance.tags if 'Email' in t['Key']]
        return emails
                    
    def emailSeperatorwrapper02(emails,Protected=None):
        for email in emails:
            emailTriggerInstanceList.append(instanceSegregation(emailList,email))
        sendEmailtemplate(emailTriggerInstanceList)
    
    protectedMailList,protectedInstances=filterProtectedInstances()
    emailList.append(emailListAppend(protectedMailList))
    emails=emailSeperatorwrapper01(emailList)
    emailSeperatorwrapper02(emails,Protected=True)

    StoppedInstances,TerminateInstances,terminateUnusedemailList = terminateUnusedInstance()
    emailList.append(emailListAppend(terminateUnusedemailList))
    StoppedInstances=list(set(StoppedInstances))
    TerminateInstances=list(set(TerminateInstances))
    emails=emailSeperatorwrapper01(emailList)
    emailSeperatorwrapper02(emails,Protected=False)

    
    if not StoppedInstances:
        logging.info('No Unprotected Instances Found, nothing to stop')
    else:
        ec2client.stop_instances(InstanceIds=StoppedInstances)


    if TerminateInstances:
        print("Terminating the VMs because they are idle for 30 Days, Devops already send out the notification prior to 7 Days!")
        for instanceIdToTerminate in TerminateInstances:
            instance = ec2resource.Instance(instanceIdToTerminate)
            instance_name = [tag['Value'] for tag in instance.tags if tag['Key'] == 'Name'][0]
            print("The {} instance with ID {} is terminating ".format(instance_name, instanceIdToTerminate))
            ec2client.terminate_instances(InstanceIds=[instanceIdToTerminate])

    logging.info('Total number of Instances Terminated : '+ str(len(terminateUnusedemailList)))
    logging.info('Total number of Instances Stopped : '+ str(len(StoppedInstances)))
    logging.info('Total number of Instances Protected : '+ str(len(protectedMailList)))
    
    data.append(reportGeneration(protectedInstances))
    data.append(reportGeneration(TerminateInstances))
    data.append(reportGeneration(StoppedInstances))
    
    print(tabulate(data[0], headers=col_names, showindex="false", tablefmt="grid"))
