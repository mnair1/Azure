import os
import sys
import boto3
import json
import datetime
import time
from datetime import timedelta
from dateutil import relativedelta
from awsglue.job import Job
from pyspark.context import SparkContext
from awsglue.context import GlueContext
athena_client = boto3.client('athena', 'us-east-1')

sc = SparkContext()
sc.addPyFile("s3://aws-analytics-deltalake/jars/io.delta_delta-core_2.11-0.6.1.jar")

from delta.tables import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, array, ArrayType, DateType

glueContext = GlueContext(sc)

spark = glueContext.spark_session.builder.config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension").config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog").getOrCreate()

conf = spark.sparkContext._conf.setAll([('spark.delta.logStore.class','org.apache.spark.sql.delta.storage.S3SingleDriverLogStore')])
spark.sparkContext._conf.getAll()

INTERACTIVE=True
DEBUG=True

if INTERACTIVE:
    JOB_DATE='2021-02-21'
else:
    args = getResolvedOptions(sys.argv, ['JOB_DATE'])
    JOB_DATE=args['JOB_DATE']

# Variables for GLue Tables
LAST_DAY = datetime.datetime.strptime(JOB_DATE, '%Y-%m-%d').date() - timedelta(days=1)
PARTITION='dt='+str(LAST_DAY)
INCRFILE_PREFIX=str(LAST_DAY.strftime('%Y')+LAST_DAY.strftime('%m')+LAST_DAY.strftime('%d'))

source_init_file_path = 's3://aws-analytics-assignments/raw/dms/fossil/coal_prod/LOAD*.csv'
source_incr_file_path = 's3://aws-analytics-assignments/raw/dms/fossil/coal_prod/'+INCRFILE_PREFIX+'*.csv'
raw_bucket='aws-analytics-assignments'

delta_path = "s3a://aws-analytics-deltalake/curated/delta_coal_prod/"

coal_prod_schema = StructType([StructField("Mode", StringType()),
                               StructField("Entity", StringType()),
                               StructField("Code", StringType()),
                               StructField("Year", IntegerType()),
                               StructField("Production", DecimalType(10,2)),
                               StructField("Consumption", DecimalType(10,2))
                               ])
    
def insert_data(spark):
    data = spark.read.csv(source_init_file_path, header='false', schema=coal_prod_schema)
    data.write.format("delta").save(delta_path)
    delta_table = DeltaTable.forPath(spark, delta_path)
    delta_table.generate("symlink_format_manifest")
	
def upsert_data(spark):
    delta_table = DeltaTable.forPath(spark, delta_path)
    data = spark.read.csv(source_incr_file_path, header='false', schema=coal_prod_schema)
    delta_table.alias("target").merge(
        source = data.alias("source"),
        condition = "target.Entity  = source.Entity AND target.Year  = source.Year"
    ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
    delta_table.delete("Mode = 'D'") 
    delta_table.generate("symlink_format_manifest")
	
def reload_table_partitions():
    athena_client.start_query_execution(
        QueryString='MSCK REPAIR TABLE delta_coal_prod;',
        QueryExecutionContext={
            'Database': 'non-renewable'
        },
        ResultConfiguration={
            'OutputLocation': 's3://amazon-athena-result-s3/'
        }
    )	

if __name__ == '__main__':	

    if DeltaTable.isDeltaTable(spark, delta_path):
        upsert_data(spark)
    else:
        insert_data(spark)
		
    reload_table_partitions()
