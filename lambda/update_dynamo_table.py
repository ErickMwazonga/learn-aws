import os
import boto3

dynamodb = boto3.resource('dynamodb')


def lambda_handler(event: any, context: any) -> any:
    user = None
    visit_count = 0

    try:
        user = event["user"]
    except KeyError:
        raise KeyError('User is not set in the payload')

    table_name = os.environ["USER_VISITS_TABLE_NAME"]
    table = dynamodb.Table(table_name)

    response = table.get_item(Key={"user": user})

    print(response)
    response_metadata = response.get("ResponseMetadata")
    response_data = response.get("Item")

    if response_data:
        visit_count = response_data["visit_count"]

    visit_count += 1
    table.put_item(Item={"user": user, "visit_count": visit_count})

    message = f"Hello {user}! You have visited us {visit_count} times."

    return {
        "message": message,
        "statusCode": 200
    }


if __name__ == "__main__":
    os.environ["USER_VISITS_TABLE_NAME"] = "user-visit-count-table"
    test_event = {"user": "erick"}

    result = lambda_handler(test_event, None)
    print(result)
