from __future__ import division
from __future__ import print_function

import boto3
import json
import logging
import base64

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ses = boto3.client('ses')
email_address = 'XXXXXXXXXXXXX'

def lambda_handler(event, context):
    for record in event['records']:
        #print(record['recordId'])
        payload = base64.b64decode(record['data'])  

        dict_payload=json.loads(payload)
        #print(dict_payload['CITY'])
        
        subject = 'High Power Usage Alert for ' + dict_payload['CITY']
        body_text =  dict_payload['CITY'] + ' is currently running at ' + str(dict_payload['COL_POWER']) + ' MW'
        ses.send_email(Source=email_address,
                   Destination={'ToAddresses': [email_address]},
                   Message={'Subject': {'Data': subject}, 'Body': {'Text': {'Data': body_text}}})
        logger.info('Email has been sent')
        return {
                'statusCode': 200,
                'body': json.dumps('High Power Usage Alert Generated.')
             }
   