import boto3
import json
from datetime import datetime
import calendar
import random
import time

stream_name = 'ny-power-fuel-hydro'

kinesis_client = boto3.client('kinesis', region_name='us-east-1')

def put_to_stream(city, temp, sensor_timestamp):
    payload = {
                'power': str(temp),
                'timestamp': str(sensor_timestamp),
                'city': city
              }

    print json.dumps(payload)

    put_response = kinesis_client.put_record(
                        StreamName=stream_name,
                        Data=json.dumps(payload),
                        PartitionKey=city)

while True:
    temp = random.randint(100, 500)
    sensor_timestamp = calendar.timegm(datetime.utcnow().timetuple())
    locations = ['Accord','Albany', 'Beacon','Brighton','Calcium', 'Bethpage','Centerport','Depauville', 'Elmira','Galeville','Lockport', 'Oneida']
    city = random.choice(locations)

    put_to_stream(city, temp, sensor_timestamp)

    # wait for 5 second
    time.sleep(5)
