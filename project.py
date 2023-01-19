import json
import boto3
import sys
from botocore.exceptions import ClientError
#SgName = sys.argv[1]
Project_Name = sys.argv[1]
#PlName = sys.argv[2]
Plentries = sys.argv[2]
ec2 = boto3.client('ec2',region_name = 'us-east-2')

response = ec2.describe_vpcs()
vpc_id = response.get('Vpcs', [{}])[1].get('VpcId', '')

try:
    print("Creating Prefix List:")
    prefix_list_name=Project_Name+'-Pl'
    prefixListEntry=[
        {
            'Cidr': Plentries,
            'Description': 'Test entry 1'
        }
    ]
    prefix_list_entries = prefixListEntry

    prefixList = ec2.create_managed_prefix_list(
    DryRun=False,
    PrefixListName=prefix_list_name,
    Entries=prefix_list_entries,
    MaxEntries=5,
    AddressFamily='IPv4'
    )
    
    prefixListID=prefixList['PrefixList']['PrefixListId']
    print("Prefix List ID:" +prefixListID)
    
    response = ec2.create_security_group(GroupName=Project_Name+'-sg',
                                            Description=Project_Name+'-sg',
                                            VpcId=vpc_id)
                                    
    security_group_id = response['GroupId']
    print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))

    data = ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {'IpProtocol': 'tcp',
                'FromPort': 80,
                'ToPort': 80,
                'PrefixListIds': [{'PrefixListId': prefixListID}]},
            {'IpProtocol': 'tcp',
                'FromPort': 443,
                'ToPort': 443,
                'PrefixListIds': [{'PrefixListId': prefixListID}]}
        ])
    print('Ingress Successfully Set %s' % data)
    ec2.create_tags(
        Resources=[security_group_id],
        Tags=[
            {
                'Key': 'Name',
                'Value': Project_Name+'-sg'
            },
            {
                'Key': 'Environment',
                'Value': 'Simulation-Deploy'
            }
        ]
    )

   instance_name_tag = Project_Name
   instances = ec2.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': [instance_name_tag]}])
   instance_id = response['Reservations'][0]['Instances'][0]['InstanceId']
   response = ec2.modify_instance_attribute(
                InstanceId=instance_id,
                Groups=[security_group_id]
            )
except ClientError as e:
    print(e)
