import json
import boto3
Project_Name = "crazy*"
#PlName = sys.argv[2]
Plentries = "10.0.0.0/16"
def lambda_handler(event, context):
    
    ec2 = boto3.client('ec2',region_name = 'ap-south-1')
    response = ec2.describe_vpcs()
    vpc_id = "vpc-0d25e6342dda0151f"
    
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
        
        instances = ec2.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': [Project_Name]}])
        instance_ids = [instance['InstanceId'] for reservation in instances['Reservations'] for instance in reservation['Instances']]
        
        for instance_id in instance_ids:
            nic = ec2.describe_network_interfaces(Filters=[{'Name': 'attachment.instance-id', 'Values': [instance_id]}])
            network_interfaces = nic['NetworkInterfaces']
        
            # Get the network interface ID
            if network_interfaces:
                network_interface_id = network_interfaces[0]['NetworkInterfaceId']
                response = ec2.associate_network_interface(
                NetworkInterfaceId=network_interface_id,
                Groups=[security_group_id]
                )
            else:
                print(f'No network interfaces found for instance {instance_id}')
    except Exception as e:
        print(e)
