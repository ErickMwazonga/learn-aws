import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    result = None
    action = event.get('action', None)

    if action == 'INCREMENT':
        result = event.get('number', 0) + 1
        logger.info(f'Calculated result of {result}')
    else:
        logger.error(f'{action} is not a valid action.')

    response = {
        'statusCode': 200,
        'result': result
    }

    return response


if __name__ == "__main__":
    test_event = {
        "action": "INCREMENT",
        "number": 3
    }

    result = lambda_handler(test_event, None)
    print(result)
