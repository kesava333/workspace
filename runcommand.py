import json

sshUsername="ec2-user"
sshKeyPath="/home/ec2-user/WEBSERVER.pem"

def lambda_handler(event, context):                       #Start of our function
    instance = ec2.create_instances(
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_NAME,
        ImageId=AMI,
        SubnetId=SUBNET_ID,
        SecurityGroupIds=[
                    'sg-0c94de36f25b5b96c', 'sg-06eb57a26f1b4b21f'
                ],

        MaxCount=1,
        MinCount=1,
        TagSpecifications=[{                              #This creates a tag for our resource
            'ResourceType': 'instance',
            'Tags': [{'Key': 'Name','Value': 'FleetManager-226'}]
        }]   
    )
    print("New instance created:", instance[0].id)
    
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    def ssh_connect_with_retry(ssh, ip_address, retries=5):
        if retries > 6:
            return False
        privkey = paramiko.RSAKey.from_private_key_file(sshKeyPath)
        interval = 5
        try:
            retries += 1
            print('SSH into the instance: {}'.format(ip_address))
            ssh.connect(hostname=ip_address, username='ec2-user', pkey=privkey)
            return True
        except Exception as e:
            print(e)
            time.sleep(interval)
            print('Retrying SSH connection to {}'.format(ip_address))
            ssh_connect_with_retry(ssh, ip_address, retries)
    
    
    
    ssh_connect_with_retry(ssh, instance[0].id, 0)
    
    stdin, stdout, stderr = ssh.exec_command("sudo bash bash.sh")
    print('stdout:', stdout.read())
    print('stderr:', stderr.read())
