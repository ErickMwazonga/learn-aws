import os
import boto3

from PIL import Image
from io import BytesIO

s3 = boto3.client('s3')

def lambda_handler(event, context):
    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']

        # Generate a thumbnail
        thumbnail = generate_thumbnail(bucket_name, object_key)

        # Upload the thumbnail to the thumbnails bucket
        upload_thumbnail(thumbnail, 'thumbnails-bucket', object_key)

def generate_thumbnail(source_bucket, object_key):
    image = s3.get_object(Bucket=source_bucket, Key=object_key)
    image_data = image['Body'].read()
    img = Image.open(BytesIO(image_data))

    # Create a thumbnail
    img.thumbnail((100, 100))
    thumbnail_data = BytesIO()
    img.save(thumbnail_data, format='JPEG')

    return thumbnail_data.getvalue()

def upload_thumbnail(thumbnail, destination_bucket, object_key):
    s3.put_object(
        Bucket=destination_bucket,
        Key=f'thumbnails/{object_key}',
        Body=thumbnail,
        ContentType='image/jpeg'
    )
