import json
import boto3

client = boto3.client("ec2")
RoleARN="arn:aws:iam::aid:role/s3FullAccessEC2"




def lambda_handler(event, context):
    instanceId=event['details']['instance-id']
    try:
        iam_policy = get_instance_iam_policy(instanceId)
        print(iam_policy['Arn'])
        if iam_policy is None or iam_policy['Arn'] != iam_policy['Arn']:
            response = client.associate_iam_instance_profile(
                IamInstanceProfile={
                    'Arn': RoleARN,
                },
                InstanceId=instanceId
                )
            print(f"Successfully attached the IAM policy {RoleARN} with the instance {instanceId}")
        else:
            detach_instance_iam_policy(instanceId)
            attachIAMRole(instanceId)
    except Exception as e:
        raise e
    
def get_instance_iam_policy(instance_id):
    response = client.describe_iam_instance_profile_associations(
        Filters=[
            {
                'Name': 'instance-id',
                'Values': [instance_id]
            }
        ]
    )

    if len(response['IamInstanceProfileAssociations']) > 0:
        return response['IamInstanceProfileAssociations'][0]['IamInstanceProfile']
    else:
        return None

def detach_instance_iam_policy(instance_id):
    response = client.describe_iam_instance_profile_associations(
        Filters=[
            {
                'Name': 'instance-id',
                'Values': [instance_id]
            }
        ]
    )

    if len(response['IamInstanceProfileAssociations']) > 0:
        association_id = response['IamInstanceProfileAssociations'][0]['AssociationId']
        client.disassociate_iam_instance_profile(AssociationId=association_id)
        print(f"Successfully detached IAM policy from instance {instance_id}")
    else:
        print(f"Instance {instance_id} is not associated with any IAM policy")


def attachIAMRole(instance_id):
    response = client.associate_iam_instance_profile(
                IamInstanceProfile={
                    'Arn': RoleARN,
                },
                InstanceId=instance_id
                )
    print(f"Successfully attached the IAM policy {RoleARN} with the instance {instance_id}")
    return response
