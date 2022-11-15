#Created by Kesava Ginjupalli (kginjupalli@clearpath.ai)

# EC2StopInstance Dead Man Switch
# Terminate Instances based on  TerminateDate tag and the Choices are --> Never, Date, Deafult
# Never - Don't Terminate any instance with this tag value
# Date - if the date is Older than the tagged date, Terminate those instances

'''Default - If the instance tag value set to be default, the lambda function will keep monitoring these instances for 30 days
 & terminate them after 30 days only if the instance is not powered on for 30 days '''

'''
TerminateDate == Never
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

subprocess.call('pip install tabulate -t /tmp/ --no-cache-dir'.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
sys.path.insert(1, '/tmp/')

from tabulate import tabulate
region = "us-east-1"

protectedInstances=[]
data=[]

today = datetime.today()

ec2resource = boto3.resource('ec2',region_name=region)
ec2client = boto3.client('ec2', region_name=region)

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
"Instance status", "Instance Powered off due to lambda", "Instance terminated due to lambda" ]

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
                    'Never'
                    ]
                },
            ],
        )
    for reservation in ec2Instances['Reservations']:
        for instance in reservation['Instances']:
            protectedInstances.append(str(instance['InstanceId']))
    return protectedInstances

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
                    try:
                        if tags["Key"] == 'TerminateDate':
                            instanceLife = datetime.strptime(tags["Value"], '%Y-%m-%d')
                            if instanceLife <= today :
                                TerminateInstances.append(instance.id)
                                logging.info(instance.id + " will be terminated, Because the instance is expired")
                            elif instanceLife > today:
                                StoppedInstances.append(instance.id)
                                logging.info(instance.id + " will be powered off, Because the instance is not expired")
                    except Exception as e:
                        if tags["Key"] == 'TerminateDate' and  tags["Value"] == 'Default':
                            # print(ec2instance.tags)
                            launchTime = ec2instance.launch_time
                            stoppedDate=date(today.year,today.month,today.day)-date(launchTime.year,launchTime.month,launchTime.day)
                            if ec2instance.state['Name'] == 'stopped' and stoppedDate.days >= 30 :
                                logging.info("The Instance "+ instance.id + " stopped for 30+days")
                                TerminateInstances.append(instance.id)
                            elif ec2instance.state['Name'] == 'stopped' and stoppedDate.days <= 5 :
                                logging.info("The Instance "+ instance.id + " stopped for 24 Days, sending out email...")
                                emailList.append(instance.id)
                            elif ec2instance.state['Name'] == 'running':
                                StoppedInstances.append(instance.id)
                                logging.info(instance.id + " will be powered off, Because the instance tag is default and scheduled to stop")
                            elif ec2instance.state['Name'] == 'stopped' :
                                protectedInstances.append(instance.id)
                    if ec2instance.tags is  None or (ec2instance.tags is not None and 'TerminateDate' not in [t['Key'] for t in ec2instance.tags]):
                        launchTime = ec2instance.launch_time
                        stoppedDate=date(today.year,today.month,today.day)-date(launchTime.year,launchTime.month,launchTime.day)
                        if ec2instance.state['Name'] == 'stopped' and stoppedDate.days >= 30 :
                            logging.info("The Instance "+ instance.id + " stopped for 30+days")
                            TerminateInstances.append(instance.id)
                        elif ec2instance.state['Name'] == 'stopped' and stoppedDate.days <= 5:
                            logging.info("The Instance "+ instance.id + " stopped for 24 Days, sending out email...")
                            emailList.append(instance.id)
                        elif ec2instance.state['Name'] == 'running':
                            StoppedInstances.append(instance.id)
                            logging.info(instance.id + " will be powered off, Because the instance has no tag associated and scheduled to stop")
                        elif ec2instance.state['Name'] == 'stopped' :
                            protectedInstances.append(instance.id)


def instanceSegregation(instanceList,email):
    emailDict={email:[]}
    for vmid in emailList:
        for instance in ec2resource.instances.all():
            if instance.instance_id == vmid and email in [t['Value'] for t in instance.tags]:
                emailDict[email].append(str(instance.instance_id))
    return emailDict


def sendEmail(email,body):
    host = "smtp.clearpath.ai"
    template ="Hello,"+'\n\n'+"You are receiving this email as the owner of an AWS simulation environment that has been left turned off for an extended continuous period of time. As part of the AWS Simulation termination policy, the following instances will be permanently deleted in 7 Days. "+"\n\n" +'\n'.join(map(str,body)) +"\n" +"Please reach out to devops team if there any concerns"
    message = 'Subject: {}\n\n{}'.format('Simulation VMs Sunset Policy Notification',template )
    server = smtplib.SMTP(host,25)
    # text = template
    server.sendmail("devops@clearpath.ai", email, message)

def sendEmailtemplate(senderItems):
    senderItems = [i for n, i in enumerate(senderItems)
    if i not in senderItems[n + 1:]]

    for email in senderItems:
        instanceDetails=[]
        instanceIds=[*set(list(email.values())[0])]
        for instance in instanceIds:
            name=[tags['Value'] for ids in ec2resource.instances.all() for tags in ids.tags if tags['Key'] == 'Name' and ids.instance_id == instance]
            instanceDetails.append(name[0] + " ==> "+ instance)
        print(instanceDetails)
        sendEmail(list(email.keys())[0], instanceDetails)

filterProtectedInstances()
terminateUnusedInstance()
StoppedInstances=list(set(StoppedInstances))
TerminateInstances=list(set(TerminateInstances))
emails=[]
emailTriggerInstanceList=[]

for vmid in emailList:
    for instance in ec2resource.instances.all():
        if instance.instance_id == vmid and 'Email' in [t['Key'] for t in instance.tags]:
            emails+=[t['Value'] for t in instance.tags if 'Email' in t['Key']]


for email in emails:
    emailTriggerInstanceList.append(instanceSegregation(emailList,email))
sendEmailtemplate(emailTriggerInstanceList)
if not StoppedInstances:
    logging.info('No Unprotected Instances Found, nothing to stop')
else:
    ec2client.stop_instances(InstanceIds=StoppedInstances)

if TerminateInstances:
    print("Terminating the VMs because they are idle for 30 Days, Devops already send out the notification prior to 7 Days!")
    #ec2client.terminate_instances(InstanceIds=TerminateInstances)
    print("dummy Terminating ")


reportGeneration(StoppedInstances)
reportGeneration(TerminateInstances)
reportGeneration(protectedInstances)

logging.info('Terminated Instance List :' + str(TerminateInstances))
logging.info('Total number of Instances Terminated : '+ str(len(TerminateInstances)))
logging.info('Total number of Instances Stopped : '+ str(len(StoppedInstances)))
logging.info('Total number of Instances Protected : '+ str(len(protectedInstances)))

print(tabulate(data, headers=col_names, showindex="false", tablefmt="grid"))