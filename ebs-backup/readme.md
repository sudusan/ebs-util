this folder contains the lambda function that will perform ebs snapshot 
- for all volumes of an ec2 instance
- for all ec2 instances in all regions for this AWS Account
- the ec2-instance must have the following tags:
  1. key=Name, value=app_name
  2. key=Backup, value=Backup
- the snapshot id for each volume will be stored in the SSM Parameter Store using the following key:
  - key name = /app_name/device_volume_name
  - value = snapshot id
- each snapshot will have the following tag:
  1. key=DeleteOn, value= aDate
