# Backup all in-use volumes for an ec2 instance with tag=Backup, and store the snapshot-id in paramter store
# this function takes in 2 environment parameters - APPLICATION_NAME and ENVIRONMENT. 
# the key for the snapshot in the parameter store is: /APPLICATION_NAME/ENVIRONMENT/DEVICE_NAME

import boto3
from datetime import timezone, datetime
import os
import collections

ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    my_session = boto3.session.Session()
    my_region = my_session.region_name
    ssm_client = boto3.client('ssm', region_name=my_region)
    print("Region is: %s" % (my_region))

    currentDT = datetime.now(timezone.utc)
    application_name = os.environ['APPLICATION_NAME']
    s3bucket = os.environ['S3_SYNC_BUCKET']
    ec = boto3.client('ec2', region_name=my_region)
    reservations = ec.describe_instances(
        Filters=[
            {'Name': 'tag:Backup', 'Values': ['Backup']},
            {'Name': 'tag:Name', 'Values': [application_name]},
        ]
    ).get(
        'Reservations', []
    )

    instances = sum(
        [
            [i for i in r['Instances']]
            for r in reservations
        ], [])

    print ("Current Time is: %s" % (currentDT.strftime("%Y-%m-%d %H:%M:%S")))
    print ("Found %s instances that need backing up" % len(instances))
    for instance in instances:
        launch_time = instance['LaunchTime']
        time_diff = currentDT - launch_time
        days = time_diff.days
        print(days)
        if days < 1:
            print("ec2 launch time is less than 1 day")
            continue
        print("time difference is: %s" %(str(time_diff)))
        instance_id = instance['InstanceId']
        print("Launch time for instance: %s is: %s" % (instance_id, launch_time))
        syncCommand = 'aws s3 sync D:\ s3://' + s3bucket + ' --delete --exclude "System Volume Information\*"'
        ssm_client.send_command(
            Targets=[
                {
                    'Key':'tag:Name',
                    'Values':[
                        application_name,
                    ]
                },
            ],
            DocumentName='AWS-RunPowerShellScript',
            Parameters={
                'commands':[
                    syncCommand,
                ]
            },
        )