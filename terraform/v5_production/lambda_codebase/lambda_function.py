import json
import boto3
import os

def lambda_handler(event, context):
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file('hello.txt', os.environ["bucket_name"], 'hello_target.txt')
    