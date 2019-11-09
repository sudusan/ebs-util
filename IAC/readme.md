this folder contains the following files and folders:
1. application-stack.yml
  - this stack will spin-up an ec2 instance as part of an autoscaling group
  - it will attach a new volume to the D drive, using the snapshot id from SSM Paramter store
  - it will launch a scheduled lambda function that will do EBS Synch via SSM Run Command
