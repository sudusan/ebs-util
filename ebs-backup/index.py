# Backup all in-use volumes for an ec2 instance with tag=Backup, and store the snapshot-id in paramter store
# this function takes in 2 environment parameters - APPLICATION_NAME and ENVIRONMENT. 
# the key for the snapshot in the parameter store is: /APPLICATION_NAME/ENVIRONMENT/DEVICE_NAME

import boto3
import datetime
import os
import collections

def lambda_handler(event, context):
    
    ec1 = boto3.client('ec2')
    regions = ec1.describe_regions().get('Regions',[] )
    for region in regions:
        this_region = region['RegionName']
        print("Region Name is: %s" % (this_region))
        ecRegionalClient = boto3.client('ec2', region_name=this_region)
        ssm = boto3.client('ssm', region_name=this_region)

        reservations = ecRegionalClient.describe_instances(
            Filters=[
                {'Name': 'tag-key', 'Values': ['Backup', 'Backup']},
            ]
        ).get(
            'Reservations', []
        )

        instances = sum(
            [
                [i for i in r['Instances']]
                for r in reservations
            ], [])

        print ("Found %d instances that need backing up" % len(instances))

        to_tag = collections.defaultdict(list)

        for instance in instances:
            try:
                retention_days = [
                    int(t.get('Value')) for t in instance['Tags']
                    if t['Key'] == 'Retention'][0]
            except IndexError:
                retention_days = 7
            app_name = 'blank'
            for tag in instance['Tags']:
                if tag['Key'] == 'Name':
                    app_name = tag['Value']
                    break
            if app_name == 'blank':
                break
            for dev in instance['BlockDeviceMappings']:
                if dev.get('Ebs', None) is None:
                    continue
                vol_id = dev['Ebs']['VolumeId']
                device_name = dev['DeviceName']
                print ("Found EBS volume %s on instance %s" % (
                    vol_id, instance['InstanceId']))

                snap = ecRegionalClient.create_snapshot(
                    VolumeId=vol_id,
                )

                # add snapshot id to parameter store
                snapid = snap['SnapshotId']
                parameterName = '/' + app_name + device_name 
                print("Parameter Name: %s" %(parameterName))
                try:
                    ssm.delete_parameter(Name=parameterName)
                except:
                    print("Parameter Name: %s not found" %(parameterName))
                ssm.put_parameter(Name=parameterName, Value=snapid, Overwrite=True, Type='String')
                to_tag[retention_days].append(snap['SnapshotId'])

                print ("Retaining snapshot %s of volume %s from instance %s for %d days" % (
                    snap['SnapshotId'],
                    vol_id,
                    instance['InstanceId'],
                    retention_days,
                ))

            for retention_days in to_tag.keys():
                delete_date = datetime.date.today() + datetime.timedelta(days=retention_days)
                delete_fmt = delete_date.strftime('%Y-%m-%d')
                print ("Will delete %d snapshots on %s" % (len(to_tag[retention_days]), delete_fmt))
                ecRegionalClient.create_tags(
                Resources=to_tag[retention_days],
                Tags=[
                    {'Key': 'DeleteOn', 'Value': delete_fmt},
                ]
            )