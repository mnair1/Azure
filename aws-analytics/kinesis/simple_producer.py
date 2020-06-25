import boto3
import json
from datetime import datetime
import calendar
import random
import time

my_stream_name = 'sensors'

kinesis_client = boto3.client('kinesis', region_name='us-east-1')

def put_to_stream(sensor_id, temp, sensor_timestamp):
    payload = {
                'temp': str(temp),
                'timestamp': str(sensor_timestamp),
                'sensor_id': sensor_id
              }

    print payload

    put_response = kinesis_client.put_record(
                        StreamName=my_stream_name,
                        Data=json.dumps(payload),
                        PartitionKey=sensor_id)

while True:
    temp = random.randint(20, 50)
    sensor_timestamp = calendar.timegm(datetime.utcnow().timetuple())
    locations = ['TORONTO','OTTAWA', 'MONTREAL']
    sensor_id = random.choice(locations)

    put_to_stream(sensor_id, temp, sensor_timestamp)

    # wait for 5 second
    time.sleep(5)
