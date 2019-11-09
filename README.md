# cirrus_ebs_util
utility templates and functions for ebs snapshot, ebs synch, ec2 launch from ebs snap
1. ebsdailybackup.yml - this template will launch to cloudwatch scheduled events
  - schedule1 to take daily ebs snapshot of the ebs volumes for each ec2 instance in this account
  - schedule2 to delete old ebs snapshots
2. ebs-backup folder
  - this folder contains the lambda function that takes snapshots of the ebs volumes - schedule1
3. ebs-snapshot-cleanup folder
  - this folder contains the lambda function that deletes old ebs snapshots
4. ebs-ssm-synch folder
  - this folder contains the lambda function that issues the SSM Run Command to do EBS synch from D drive to S3 bucket
5. IAC folder
  - this contains the application-stack.yml template to launch the ec2 instance and also launch the scheduler for SSM Synch                lambda function (in step 4 above)
6. ensure that the 3 zip files of the lambda functions are stored in a common autodesk s3 bicket
