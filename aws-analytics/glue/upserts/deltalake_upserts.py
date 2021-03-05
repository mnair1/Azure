# install Delta Lake Libraries https://jar-download.com/artifacts/io.delta/delta-core_2.12/0.1.0/source-code

import os
import sys
import boto3
import json
from awsglue.context import GlueContext
from awsglue.job import Job

from delta.tables import *
from pyspark.sql.functions import *

sqs_client = boto3.client('sqs', 'us-east-1')
athena_client = boto3.client('athena', 'us-east-1')

# TODO: To be moved into the Configuration Store
target_path = 's3://nb-deltalake/data/titles'
sqs_url = 'https://sqs.us-east-1.amazonaws.com/694941555642/deltalake-titles-queue'

source_file_path = []
message_receipts = []

def insert_data(spark):
	data = spark.read.format("csv").option("delimiter", "\t").load(source_file_path, header='true', inferSchema='true')
	data.repartition(1).write.partitionBy("start_year").format("delta").save(target_path)
	delta_table = DeltaTable.forPath(spark, target_path)
	delta_table.generate("symlink_format_manifest")
	
def upsert_data(spark):
	delta_table = DeltaTable.forPath(spark, target_path)
	data = spark.read.format("csv").option("delimiter", "\t").load(source_file_path, header='true', inferSchema='true')
	delta_table.alias("target").merge(
		source = data.alias("source"),
		condition = "target.tconst = source.tconst"
	).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
	delta_table.generate("symlink_format_manifest")

def reload_table_partitions():
	athena_client.start_query_execution(
		QueryString='MSCK REPAIR TABLE titles;',
		QueryExecutionContext={
			'Database': 'default'
		},
		ResultConfiguration={
			'OutputLocation': 's3://nb-deltalake/query_results/'
		}
	)

def get_files_from_sqs():
	response = sqs_client.receive_message(
		QueueUrl=sqs_url,
		MaxNumberOfMessages=10
	)
	if 'Messages' in response:
		for message in response['Messages']:
			message_json = json.loads(message['Body'])
			s3_bucket = message_json['Records'][0]['s3']['bucket']['name']
			file_key = message_json['Records'][0]['s3']['object']['key']
			source_file_path.append('s3://' + s3_bucket + '/' + file_key)
			message_receipts.append(message['ReceiptHandle'])
		if len(response['Messages']) > 0:
			get_files_from_sqs()

def delete_sqs_messages():
	for receipt in message_receipts:
		sqs_client.delete_message(
			QueueUrl=sqs_url,
			ReceiptHandle=receipt
		)

if __name__ == '__main__':

	sc = SparkContext().getOrCreate()
	glueContext = GlueContext(sc)
	spark = glueContext.spark_session
	spark.conf.set("spark.sql.shuffle.partitions",3)
	
	job = Job(glueContext)
	job.init('deltalake-processing-titles', {})

	get_files_from_sqs()

	if DeltaTable.isDeltaTable(spark, target_path):
		upsert_data(spark)
	else:
		insert_data(spark)

	reload_table_partitions()
	delete_sqs_messages()
	