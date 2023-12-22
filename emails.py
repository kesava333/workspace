import boto3
emailList = []

ec2resource = boto3.resource('ec2', region_name='us-west-2')

# Send email to the owner on 24th day 
def sendEmail(email,body,Protected):
    host = "smtp.clearpath.ai"
    if Protected is not True:
        template ="Hello,"+'\n\n'+"You are receiving this email as you are the owner of an AWS simulation environment that has been left turned off for an extended continuous period of time. As part of the AWS Simulation termination policy, the following instances will be permanently deleted in 7 Days. "+"\n\n" +'\n'.join(map(str,body)) +"\n" +"If you need to extend the lease period of aws simulation, please start your VMs from orpheus. This will automatically extend the lease period by 30 days."+'\n\n'+ "Please refer to our policy for more information: https://wiki.clearpathrobotics.com/display/SI/AWS+Sunset+Policy "
    else:
        template = """Hello,"
            + "\n\n"
            + "You are receiving this email as you are the owner of an AWS simulation environment that has been left turned off for an extended continuous period 30 Days. If you don't see any value keeping this alive on AWS, Please reachout to #devops-support channel on slack or Create an SES ticket to remove the Simulation from AWS  "
            + "\n\n"
            + "\n".join(map(str, body))
            + "\n"
            + "If you wish"""
    message = 'Subject: {}\n\n{}'.format('Simulation VMs Sunset Policy Notification',template )
    cc_email = 'kginjupalli@clearpath.ai'
    message += f'\nCc: {cc_email}'
    server = smtplib.SMTP(host,25)
    server.sendmail("devops@clearpath.ai", [email, cc_email], message)
    
def sendEmailtemplate(senderItems,Protected=None):
        senderItems = [i for n, i in enumerate(senderItems)
        if i not in senderItems[n + 1:]]

        for email in senderItems:
            instanceDetails=[]
            instanceIds=[*set(list(email.values())[0])]
            for instance in instanceIds:
                name=[tags['Value'] for ids in ec2resource.instances.all() for tags in ids.tags if tags['Key'] == 'Name' and ids.instance_id == instance]
                instanceDetails.append(name[0] + " ==> "+ instance)
            sendEmail(list(email.keys())[0], instanceDetails,Protected)
            
def emailListAppend(instanceList):   
        for instance in instanceList:
            emailList.append(instance)
        return emailList
