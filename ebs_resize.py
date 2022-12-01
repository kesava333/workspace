#!/usr/bin/python3

import subprocess
from math import ceil
import requests
import sys
import time
import boto3
import subprocess

fs='/'
minimum_percentage=float(70)
region_name="ap-south-1"

def init_ec2_client():
    return boto3.client('ec2', region_name=region_name)

def get_instance_id():
    return requests.get('http://169.254.169.254/latest/meta-data/instance-id').content

def get_region():
    return requests.get('http://169.254.169.254/latest/meta-data/placement/region').content

def identify_ebs_volume(client):
    print("############")
    print(client)
    response = client.describe_instances(InstanceIds=[get_instance_id()])["Reservations"][0]["Instances"][0].get("BlockDeviceMappings")
    print(response)
    if len(response) > 1:
        print(f"We have identified {len(response)} EBS drive, please check manually!")
        sys.exit(1)
    else:
        return response[0]["Ebs"].get("VolumeId")


def get_volume_size(client, volume_id):
    response = client.describe_volumes(
        VolumeIds=[volume_id]
    )['Volumes'][0]['Size']
    return response

def extend_volume(client, volume_id, new_size):
    print(f'Going to extend volume {volume_id} to {new_size}G')
    try:
        response = client.modify_volume(
            VolumeId=volume_id,
            Size=new_size
        )
        return True
    except Exception as e:
        print(f'Unable to extend volume, exception: {e}')
        return False

def wait_volume_modified(client, volume_id):
    available_states = ["optimizing", "completed"]
    state = ""
    while state not in available_states:
        state = client.describe_volumes_modifications(VolumeIds=volume_id)['VolumesModifications'][0].get('ModificationState')
        print(f'Volume {volume_id} still not available, waiting...')
        time.sleep(5)
    return True



def check_usage(fs_to_check):
    print(f"Checking usage of partition {fs_to_check}")
    partition_usage = float(subprocess.check_output('df -h ' + fs_to_check + ' | tail -1 | awk \'{sub("%","");print $5}\'', shell=True).decode('ascii'))
    return partition_usage

def get_current_partition_size(fs_to_check):
    print(f"Getting current partition size {fs_to_check}")
    partition_size = float(subprocess.check_output('df -h ' + fs_to_check + ' | tail -1 | awk \'{gsub("G","");print $2}\'', shell=True).decode('ascii'))
    return partition_size

def calculate_value_to_provision(fs_to_increase, minimum_percentage):
    current_fs_size = float(subprocess.check_output('df -h ' + fs_to_increase + ' | tail -1 | awk \'{gsub("G","");print $2}\'', shell=True).decode('ascii'))
    current_fs_usage = float(subprocess.check_output('df -h ' + fs_to_increase + ' | tail -1 | awk \'{gsub("G","");print $3}\'', shell=True).decode('ascii'))
    space_to_add = int(ceil(float((current_fs_usage / minimum_percentage * 100) - current_fs_size)))
    if space_to_add < 5:
        space_to_add = 5
    print(f'If we want to increase FS {fs_to_increase} to have minimum {minimum_percentage}% used, we need to add {space_to_add}G to the partition')
    return int(space_to_add + current_fs_size)


def get_main_disk(fs):
    disk_to_extend = subprocess.check_output('lsblk -l | grep -B1 ' + fs + ' | head -1 | awk \'{print $1}\'', shell=True).strip().decode('ascii')
    return disk_to_extend

def extend_disk(fs):
    disk_to_extend = get_main_disk(fs)
    try:
        print(f'Extending disk {disk_to_extend}')
        disk_entend = subprocess.check_output(f'sudo growpart /dev/{disk_to_extend} 1', shell=True).strip().decode('ascii')
        print(disk_entend)
        return True
    except Exception as e:
        print(f'Unable to extend the disk, exception: {e}')
        return False

def extend_partition(fs):
    try:
        print(f'Extending partition {fs}')
        partition_entend = subprocess.check_output(f'sudo xfs_growfs -d {fs}', shell=True).decode('ascii')
        print(partition_entend)
        return True
    except Exception as e:
        print(f'Unable to extend partition, exception: {e}')
        return False


if __name__ == "__main__":
    partition_usage = check_usage(fs)
    client = init_ec2_client()
    if partition_usage > minimum_percentage:
        new_volume_size = calculate_value_to_provision(fs, minimum_percentage)
        volume_id = identify_ebs_volume(client)
        aws_volume_size = get_volume_size(client, volume_id)
        print(aws_volume_size)
        linux_volume_size = get_current_partition_size(fs)
        if aws_volume_size == linux_volume_size:
            extend_volume(client, volume_id, new_volume_size)
            wait_volume_modified(client, volume_id)
        extend_disk(fs)
        time.sleep(10)
        extend_partition(fs)
    else:
        print(f'Partition usage is {partition_usage}, no increase needed')
