import json
import logging
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    transactionId = event['transactionId']
    transactionType = event['transactionType']
    transactionAmount = event['transactionAmount']

    transactionResponse = {
        'transactionId': transactionId,
        'transactionType': transactionType,
        'transactionAmount': transactionAmount,
    }

    response = {
        'statusCode': 200,
        'message': 'Transaction Successfully completed',
        'body': json.dumps(transactionResponse)
    }

    return response


if __name__ == "__main__":
    test_event = {
        'transactionId': str(str(uuid.uuid4())),
        'transactionType': 'PURCHASE',
        'transactionAmount': 600,
    }

    result = lambda_handler(test_event, None)
    print(result)
