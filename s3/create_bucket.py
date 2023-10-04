import logging
import boto3
from botocore.exceptions import ClientError


def create_bucket(bucket_name: str, region: str | None = None) -> bool:
    try:
        if not region:
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = boto3.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
    except ClientError as e:
        logging.error(e)
        return False

    return True
