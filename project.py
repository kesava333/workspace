import json
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    
    response = ec2.describe_vpcs()
    vpc_id = response.get('Vpcs', [{}])[1].get('VpcId', '')
    
    try:
        response = ec2.create_security_group(GroupName='Kesava-Test',
                                             Description='kesava-test',
                                             VpcId=vpc_id)
        response = ec2.create-managed-prefix-list(prefix-list-name='Kesava-Test',
                                             Description='kesava-test')                                     
        security_group_id = response['GroupId']
        print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))
    
        data = ec2.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {'IpProtocol': 'tcp',
                 'FromPort': 80,
                 'ToPort': 80,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                {'IpProtocol': 'tcp',
                 'FromPort': 22,
                 'ToPort': 22,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
            ])
        print('Ingress Successfully Set %s' % data)
        ec2.create_tags(
        Resources=[security_group_id],
        Tags=[
            {
                'Key': 'Name',
                'Value': 'My Security Group'
            },
            {
                'Key': 'Environment',
                'Value': 'Production'
            }
        ]
    )
    except ClientError as e:
        print(e)
----
import json
import boto3



security_group_name="test1"
security_group_description="test1"
ingress_sg=[
        {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
        {'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
    ]
prefix_list_name="demo1"
prefixListEntry=[
        {
            'Cidr': '192.0.2.0/24',
            'Description': 'Test entry 1'
        },
        {
            'Cidr': '198.51.100.0/24',
            'Description': 'Test entry 2'
        }
    ]
    
vpc_id="vpcid"

def lambda_handler(event, context):
    # TODO implement
    # Create a client for the EC2 service

    ec2 = boto3.client('ec2')
    try:
        # Create a security group
        response = ec2.create_security_group(
            GroupName=security_group_name,
            Description=security_group_description,
             VpcId=vpc_id
        )

        # Get the security group ID
        security_group_id = response['GroupId']


        ec2.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=ingress_sg
        )
     except ClientError as e:
        print(e)

    
    prefix_list_entries = prefixListEntry
    

    prefixList = ec2.create_managed_prefix_list(
    DryRun=False,
    PrefixListName=prefix_list_name,
    Entries=prefix_list_entries,
    MaxEntries=100,
    AddressFamily='IPv4'
    )
    
    prefixListID=prefixList['PrefixList']['PrefixListId']
    
    
    -----------------------------
    instance_name_tag = 'my-instance'
    instances = ec2.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': [instance_name_tag]}])
    instance_id = response['Reservations'][0]['Instances'][0]['InstanceId']
    response = ec2.modify_instance_attribute(
                InstanceId=instance_id,
                Groups=[security_group_id]
            )

    
    
    
