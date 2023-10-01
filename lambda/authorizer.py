import json


def lambda_handler(event, context):
    auth = 'Deny'

    if event['authorizationToken'] == 'hello':
        auth = 'Allow'

    auth_response = {
       "principalId":"hello",
       "policyDocument":{
          "Version":"2012-10-17",
          "Statement":[
             {
                "Action":"execute-api:Invoke",
                "Resource":[
                   "arn:aws:execute-api:*"
                ],
                "Effect": auth
             }
          ]
       }
    }

    return auth_response
