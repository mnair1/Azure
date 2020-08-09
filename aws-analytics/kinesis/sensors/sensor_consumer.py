import boto3
import json
from datetime import datetime
import time

stream_name = 'sensors'
kinesis_client = boto3.client('kinesis', region_name='us-east-1')
response = kinesis_client.describe_stream(StreamName=stream_name)
shard_id = response['StreamDescription']['Shards'][0]['ShardId']
shard_iterator = kinesis_client.get_shard_iterator(StreamName=stream_name,
                                                      ShardId=shard_id,
                                                      ShardIteratorType='LATEST')
shard_iterator = shard_iterator['ShardIterator']
record_response = kinesis_client.get_records(ShardIterator=shard_iterator,
                                              Limit=2)
while 'NextShardIterator' in record_response:
    record_response = kinesis_client.get_records(ShardIterator=record_response['NextShardIterator'],
                                                  Limit=2)
    print(record_response)
    # wait for 5 seconds
    time.sleep(5)
