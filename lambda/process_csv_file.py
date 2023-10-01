import io
import json
import csv
import boto3

from typing import Tuple

s3 = boto3.client('s3')


def lambda_handler(event, context):
    try:
        records = event.get('Records')
        if not records:
            print("No records found in the event.")
            return

        record = records[0]
        bucket, key = get_bucket(record)

        response = s3.get_object(Bucket=bucket, Key=key)

        data = response['Body'].read().decode('utf-8')
        reader = csv.reader(io.StringIO(data))
        next(reader)

        for row in reader:
            if len(row) >= 3:
                year, mileage, price = row[0], row[1], row[2]
                print(f"Year: {year}, Mileage: {mileage}, Price: {price}")
            else:
                print("Invalid row format. Skipping.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")



def get_bucket(record) -> Tuple[str, str]:
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']

    print(f"Bucket: {bucket}")
    print(f"Key: {key}")

    return bucket, key
