import glob
import boto3
import aws_kinesis_agg.aggregator
import time
import uuid
myStreamName = "aggstream"
def send_record(agg_record):
    pk, _, data = agg_record.get_contents()
    kinesis_client.put_record(StreamName=myStreamName, Data=data, PartitionKey=pk)
kinesis_client = boto3.client('kinesis', region_name="us-east-1")
kinesis_agg = aws_kinesis_agg.aggregator.RecordAggregator()
kinesis_agg.on_record_complete(send_record)
def main():

    path = '../../s3/*.csv'
    filenames = glob.glob(path)

    for filename in filenames:
        with open(filename, 'r', encoding='utf-8') as data:
            pk = str(uuid.uuid4())
            for record in data:
                print(record)
                kinesis_agg.add_user_record(pk, record)
        send_record(kinesis_agg.clear_and_get())
        time.sleep(5)
main()
