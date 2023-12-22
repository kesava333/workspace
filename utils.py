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


current_dateTime = datetime.now()
# Account Number of target AWS Account
AccountID='709708176998'
# AWS Region will be passed as a user input
RegionList=['us-east-1']
ec2client = boto3.client('ec2', region_name='us-east-1')
ec2resource = boto3.resource('ec2', region_name='us-east-1')

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

def filterProtectedInstances():
    ec2Instances = ec2client.describe_instances(
        Filters=[
            {
                'Name': 'tag:TerminateDate',
                'Values': [
                    'Reserved'
                    ]
                },
            ],
        )
    for reservation in ec2Instances['Reservations']:
        for instance in reservation['Instances']:
            ec2instance =ec2resource.Instance(str(instance['InstanceId']))
            launchTime = ec2instance.launch_time
            stoppedDate=date(today.year,today.month,today.day)-date(launchTime.year,launchTime.month,launchTime.day)
            if ec2instance.state['Name'] == 'stopped' and stoppedDate.days == 0 :
                emailList.append(str(instance['InstanceId']))
            protectedInstances.append(str(instance['InstanceId']))
    return emailList,protectedInstances


def reportGeneration(instanceList):
    time.sleep(10)
    stack = traceback.extract_stack()
    filename, lineno, function_name, code = stack[-2]
    attributePassed=re.compile(r'\((.*?)\).*$').search(code).groups()[0]
    # Get the Name tag
    for instanceId in instanceList:
        instanceReportAttribute=[]
        ec2instance = ec2resource.Instance(instanceId)
        for tags in ec2instance.tags:
            if tags["Key"] == 'Name':
                instanceReportAttribute.insert(0,tags['Value'])
        if ec2instance.tags is None or 'Name' not in [t['Key'] for t in ec2instance.tags]:
            instanceReportAttribute.insert(0,instanceId)
        instanceReportAttribute.insert(1,instanceId)
        instanceReportAttribute.insert(2,today.strftime("%a %d-%b-%Y %I:%M:%S %p"))

        # Get the instance status
        instance = ec2resource.Instance(instanceId)
        instanceReportAttribute.insert(3,instance.state['Name'])

        if (instance.state['Name'] == 'stopped' or instance.state['Name'] == 'stopping')  and attributePassed == "StoppedInstances":
            instanceReportAttribute.insert(4,"Yes")
        else:
            instanceReportAttribute.insert(4,"No")
        if (instance.state['Name'] == 'Terminated' or instance.state['Name'] == 'shutting-down') and attributePassed == "TerminateInstances":
            instanceReportAttribute.insert(5,"Yes")
        else:
            instanceReportAttribute.insert(5,"No")
        data.append(instanceReportAttribute)
    return data


def terminateUnusedInstance():
    if not instances:
            logging.info('No Instances found, nothing to stop')
    else:
        for instance in instances:
            if instance.id in protectedInstances:
                # check to see if instances are protected
                logging.info(instance.id + " is a protected instance, not shutting down.")
            else:
                ec2instance =ec2resource.Instance(instance.id)
                for tags in ec2instance.tags:
                    instance_email = [tag['Value'] for tag in instance.tags if tag['Key'] == 'Email'][0]
                    instance_name = [tag['Value'] for tag in instance.tags if tag['Key'] == 'Name'][0]
                    # Deafult behaviour
                    if tags["Key"] == 'TerminateDate' and  tags["Value"] == 'Default':
                        launchTime = ec2instance.launch_time
                        stoppedDate=date(today.year,today.month,today.day)-date(launchTime.year,launchTime.month,launchTime.day)
                        if ec2instance.state['Name'] == 'stopped' and stoppedDate.days >= 30 :
                            logging.info("The Instance "+ instance.id + " stopped for 30+days, Terminating it as per sunset policy")
                            TerminateInstances.append(instance.id)
                        elif ec2instance.state['Name'] == 'stopped' and stoppedDate.days == 0 :
                            logging.info("The Instance Name: {} with Email: {} is Stopped for 24 Days, sending out email to the owner as per sunset policy... ".format(instance_name,instance_email))
                            emailList.append(instance.id)
                        elif ec2instance.state['Name'] == 'running':
                            logging.info("The Instance Name: {} with Email: {} will be powered off, Because the instance tag is default and scheduled to stop as per sunset policy... ".format(instance_name,instance_email))
                            StoppedInstances.append(instance.id)
                        elif ec2instance.state['Name'] == 'stopped' :
                            StoppedInstances.append(instance.id)
                    # For training VMS
                    elif tags["Key"] == 'TerminateDate' and  tags["Value"] == 'training':
                        if ec2instance.state['Name'] == 'running':
                             logging.info("The Instance Name: {} with Email: {} owered off, Because the instance tag is training and will be stopped as per sunset policy... ".format(instance_name,instance_email))
                             StoppedInstances.append(instance.id)
                        elif ( ec2instance.state["Name"] == "stopped" and stoppedDate.days == 0 ):
                            logging.info("The Instance Name: {} with Email: {}  stopped for 30 Days, sending out email to the owner as per sunset policy... ".format(instance_name,instance_email))
                            emailList.append(str(instance.id))
    return StoppedInstances,TerminateInstances,emailList

def instanceSegregation(emailList,email):
        emailDict={email:[]}
        for vmid in emailList:
            for instance in ec2resource.instances.all():
                if instance.instance_id == vmid and email in [t['Value'] for t in instance.tags]:
                    emailDict[email].append(str(instance.instance_id))
        return emailDict
