import functools
import json
import logging
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def timeit(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        time_taken = time.time() - start

        _, context = args
        lambda_name = context.function_name

        logger.info(f'Function {lambda_name} took {time_taken:.4f} seconds to execute')
        return result

    return wrapper


@timeit
def lambda_handler(event, context):
    '''
    {
      "action": "INCREMENT",
      "number": 3
    }
    '''

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
