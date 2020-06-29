from __future__ import division

import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ses = boto3.client('ses')
email_address = 'XXXXXXXXXXXXX'

def lambda_handler(event, context):
    subject = 'High Power Usage Alert'
    body_text = 'High Power Usage Alert for %s' %  (json.dumps(event['city']))
    ses.send_email(Source=email_address,
                   Destination={'ToAddresses': [email_address]},
                   Message={'Subject': {'Data': subject}, 'Body': {'Text': {'Data': body_text}}})
    logger.info('Email has been sent')
    return {
        'statusCode': 200,
        'body': json.dumps('High Power Usage Alert Generated.')
    }
