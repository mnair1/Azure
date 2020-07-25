import boto3
import json
from datetime import datetime
import calendar
import random
import time

stream_name = 'stock'

kinesis_client = boto3.client('kinesis', region_name='us-east-1')

def put_to_stream(symbol, price, ticker_timestamp):
    payload = {
                'symbol': str(symbol),
                'price': price,
                'timestamp': str(ticker_timestamp)
              }

    print(payload)

    put_response = kinesis_client.put_record(
                        StreamName=stream_name,
                        Data=json.dumps(payload),
                        PartitionKey=symbol)

while True:
    price = random.uniform(10.5, 500.5)
    ticker_timestamp = calendar.timegm(datetime.utcnow().timetuple())
    symbols = ['AAPL','AMZN','MSFT', 'FB', 'MCD', 'SBUX']
    symbol = random.choice(symbols)

    put_to_stream(symbol, price, ticker_timestamp)

    # wait for 5 second
    time.sleep(5)

