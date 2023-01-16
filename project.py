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
    except ClientError as e:
        print(e)
