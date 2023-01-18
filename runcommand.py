import json
import paramiko
import boto3

sshKeyPath="WEBSERVER.pem"
scriptName="bash.sh"
sshUser='ec-user'


def lambda_handler(event, context):
    
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
    
    shell_output = open(scriptName, "r")
    op=(shell_output.read())
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
            ssh.connect(hostname=ip_address, username=sshUser, pkey=privkey)
            return True
        except Exception as e:
            
            time.sleep(interval)
            print('Retrying SSH connection to {}'.format(ip_address))
            ssh_connect_with_retry(ssh, ip_address, retries)
    
    

    ssh_connect_with_retry(ssh, instance[0].id, 3)

    ftp_client=ssh.open_sftp()
    ftp_client.put(scriptName,scriptName)
    ftp_client.close()
    stdin, stdout, stderr = ssh.exec_command("sudo bash ./"+scriptName)
    print('Shell Output:', stdout.read())
    print('SSH Errors:', stderr.read())
