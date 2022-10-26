import logging
import boto3

vm_tags=[{
  'Key': 'Name',
  'Value': 'VM'
}]

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
    resource =boto3.resource('ec2', region_name=AWSRegion)

    instances = [i for i in resource.instances.all()]

    for vm in instances:
        if vm.tags is None or 'Name' not in [t['Key'] for t in vm.tags]:
          logging.info("Adding tags to Instance - "+ vm.instance_id)
          ec2.create_tags(Resources=[str(vm.instance_id)], Tags=vm_tags)

    volumes = [i for i in resource.volumes.all()]
    for vol in volumes:
        if vol.tags is None or 'Name' not in [t['Key'] for t in vol.tags]:
          logging.info("Adding tags to Volume - "+ vol.volume_id)
          ec2.create_tags(Resources=[str(vol.volume_id)], Tags=vm_tags)

    for snaps in ec2.describe_snapshots(OwnerIds=['self'])['Snapshots']:
        if 'Tags' in snaps:
          tagsList = [tag['Key'] for tag in snaps['Tags']]
          if 'Name' not in tagsList:
            logging.info("Adding tags to Snapshots - "+ snaps['SnapshotId'])
            ec2.create_tags(Resources=[str(snaps['SnapshotId'])], Tags=vm_tags)
        else:
          logging.info("Adding tags to Snapshots - "+ snaps['SnapshotId'])
          ec2.create_tags(Resources=[str(snaps['SnapshotId'])], Tags=vm_tags)
