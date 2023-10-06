'''
Backup every s3 object upload to a backup bucket

STEPS
1. Create source and primary bucket
2. Create IAM role for lambda with [AmazonS3FullAccess, CloudWatchLogsFullAccess] policies  to S3(Testing)
3. Create lambda function
4. Add a lambda trigger for S3 post event and choose the s3 source bucket // In s3 add Event Notification in Properties
'''

import os
import json

import boto3


s3 = boto3.client('s3')

def lambda_handler(event, context):
    source_bucket_name = 'lazuli-primary-bucket'
    backup_bucket_name = 'lazuli-backup-bucket'

    for record in event['Records']:
        source_key = record['s3']['object']['key']

        # Construct the target (backup) key
        backup_key = 'backup/' + os.path.basename(source_key)

        try:
            s3.copy_object(
                CopySource={'Bucket': source_bucket_name, 'Key': source_key},
                Bucket=backup_bucket_name,
                Key=backup_key
            )
            print(f"Backup successful: {source_key} -> {backup_key}")
        except Exception as e:
            print(f"Error copying {source_key} to backup bucket: {str(e)}")
