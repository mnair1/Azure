import boto3
kinesis = boto3.client('kinesis', region_name='us-east-1')
response = kinesis.put_record(
    StreamName='newStream',
    Data='the data',
    PartitionKey='partkey1'
)
