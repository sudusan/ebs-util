this filder contains the lambda function that will trigger the SSM Run command
this function needs 2 encironment parameters
  - APPLICATION_NAME -  this is the name of the application (example = delwiki)
  - S3_SYNC_BUCKET - the name of the s3 bucket where files will need to be synched
  if there are multiple s3 buckets that will need sync ( use BUCKET1, BUCKET2, etc) and also modify the lambda function accordingly
the SSM Run Command will be triggered only if the launch time of the instance is > 1 day
