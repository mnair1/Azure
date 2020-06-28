from __future__ import division

import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ses = boto3.client('ses')
email_address = 'XXXXXXXXXXXXX'

def lambda_handler(event, context):
    subject = 'New File uploaded to S3'
    body_text = 'A new file has been uploaded to S3. Here are the details: %s' %  (json.dumps(event))
    ses.send_email(Source=email_address,
                   Destination={'ToAddresses': [email_address]},
                   Message={'Subject': {'Data': subject}, 'Body': {'Text': {'Data': body_text}}})
    logger.info('Email has been sent')
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
