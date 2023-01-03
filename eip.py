# Create by Kesava Ginjupalli - kginjupalli@clearpath.ai

import logging
import boto3
import sys

RegionList=sys.argv[1]

if RegionList == 'all':
    client = boto3.client('ec2')
    RegionList = [region['RegionName'] for region in client.describe_regions()['Regions']]
else:
    RegionList=RegionList.split()

for AWSRegion in RegionList:
    ec2 = boto3.client('ec2',region_name=AWSRegion)
    logging.basicConfig()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    addresses_dict = ec2.describe_addresses()
    for eip_dict in addresses_dict['Addresses']:
        if "InstanceId" not in eip_dict:
            print (eip_dict['PublicIp'] +
                " doesn't have any instances associated, releasing")
            ec2.release_address(AllocationId=eip_dict['AllocationId'])
