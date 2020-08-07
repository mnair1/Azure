# -------------------------------------------------------------------------
# MODIFY WITH CARE
# Standard libraries to be used in AWS Glue jobs
# -------------------------------------------------------------------------

import sys
from pyspark.context import SparkContext
from pyspark.sql.session import SparkSession
from pyspark.sql import functions as f
from pyspark.sql.types import *
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, array, ArrayType, DateType
from pyspark.sql import Row, Column
import datetime
import json
import boto3
import logging
import calendar
import uuid
import time
from dateutil import relativedelta
from datetime import timedelta
import argparse

def read_s3_file(spark, type, path, delimiter='|', header='true', rowTag='placeholder', flatten=True, schema=''):
    '''
    function: read_s3_file
    description: Reads file of either CSV or XML format from S3.

    Args:
        spark: Spark session object.
        type: Format of the file. It can be either CSV or XML.
        path: Path of the file on S3.
        delimiter: Delimiter used in the file. (Applicable on CSV files only)
        header: If the CSV file has header or not. (Applicable on CSV files only)
        rowTag: Tag by which rows are defined in XML file. (Applicable on XML files only)
        flatten: If the XML hierarchy should be flatten or not.

    returns:
        spark.sql.dataframe: Returns a object of Spark Dataframe containing data of the read file from S3.

    Note:
        Format 'com.databricks.spark.xml' requires 'spark-xml_2.11-0.4.1.jar' file in JAR dependencies.
    '''
    if (type == 'CSV'):
        return spark.read.format("com.databricks.spark.csv").option("schema", schema).option("header", header).option("delimiter", delimiter).load(path)
    if (type == 'XML'):
        return spark.read.format('com.databricks.spark.xml').option('rowTag', rowTag).load(path)
    if (type == 'PARQUET'):
        return spark.read.parquet(path)
    
def write_s3_file(df, table_location, table, partition=None, uid=None, format='PARQUET', delimiter='\t', coalesce=1, header=False):
    '''
    function: write_s3_file
    description: Write a file of either Parquet or CSV format to S3.

    Args:
        df: spark.sql.dataframe to be written to S3.
        table_location: Location of where the file should be stored.
        table: Name of the table.
        partition: Date by which the file should be stored in S3.
        format: Format in which the file should be stored. (PARQUET is default)
        delimited: How to file should be delimited. (Applicable on CSV files only)
        coalesce: Number of spark.sql.dataframe partitions.
    '''
    try:
        if format == 'PARQUET':
            if uid is None:
                df.write.parquet(table_location+'/'+table+'/'+partition)
            else:
                df.write.parquet(table_location+'/'+table+'/'+uid+'/'+partition)
        if format == 'CSV':
            if partition is None:
                df.coalesce(coalesce).write.option("delimiter", delimiter).option("header", "true").option("quoteAll", "true").option("quote", "\"").csv(table_location+ '/' + uid + '/' + table)
            elif uid is None:
                df.coalesce(coalesce).write.option("delimiter", delimiter).option("quote", "\"").option("quoteAll", "true").csv(table_location +'/' + partition)
            else:
                df.coalesce(coalesce).write.option("delimiter", delimiter).option("quote", "\"").option("quoteAll", "true").csv(table_location +'/' + uid + '/' + partition)
    except Exception as e:
        raise Exception(e)


def append_path_to_list(list, location, table_name):
    list.append({'Path': location + '/' + table_name})
    
def update_crawler(client, crawler_name, s3targets):
    client.update_crawler(
        Name=crawler_name,
        Targets = {'S3Targets':s3targets}
            
    )
    
def start_crawler(client, crawler_name):
    print(crawler_name + ' started.')
    
    # Getting PRE-RUN READY status.
    while(True):
        time.sleep(1)
        response = client.get_crawler(
                        Name=crawler_name
                   )
        
        if response['Crawler']['State'] == 'READY':
            print(response['Crawler']['State'])
            break
            
    client.start_crawler(
        Name=crawler_name
    )
    
    # Getting RUNNING status for stdout.            
    while(True):
        time.sleep(15)
        response = client.get_crawler(
                        Name=crawler_name
                   )
        
        if response['Crawler']['State'] == 'RUNNING':
            print(response['Crawler']['State'])
            break
        
    # Getting STOPPING status for stdout.
    while(True):
        time.sleep(1)
        response = client.get_crawler(
                        Name=crawler_name
                   )
        
        if response['Crawler']['State'] == 'STOPPING':
            print(response['Crawler']['State'])
            break
    
   # Getting READY status.
    while(True):
        time.sleep(1)
        response = client.get_crawler(
                        Name=crawler_name
                   )
        
        if response['Crawler']['State'] == 'READY':
            print(response['Crawler']['State'])
            break

def delete_crawler(client, crawler_name):
    # Getting READY status before deleting making sure it won't delete a running crawler.
    while(True):
        time.sleep(1)
        response = client.get_crawler(
                        Name=crawler_name
                   )
        
        if response['Crawler']['State'] == 'READY':
            print(response['Crawler']['State'])
            break
    
    client.delete_crawler(
        Name=crawler_name
    )
    
    print(crawler_name + ' deleted.')

def append_log(log, logdate, id, message):
    '''
    function: append_log
    description: Appends to the log.

    Args:
        log: spark.sql.dataframe of logs.
        logdate: Date on which the log was created.
        id: Id to identify the logs.
        message: Message of the log.

    returns:
        spark.sql.dataframe: Returns a dataframe containing newly appended log.
    '''
    return log.append(Row(logdate,id, message))

def delete_catalog_table(client, database, table):
    try:
        response = client.delete_table(DatabaseName=database,Name=table)
    except Exception as e:
        print(table+' does not exist in glue catalog')

def job_notification_sns(region_name, log_bucket, job_log_dir, partition, sns_arn):
    '''
    function: format_log_date
    description: Returns current timestamp (date and time) for logs in Amazon Athena format.

    Args:
        region_name: AWS Region in which the SNS and S3.
        log_bucket: Name of the log bucket.
        job_log_dir: Folder in which the logs will be placed.
        partition: Folder (named as date of log creation) by which the logs will be partitioned.
        sns_arn: ARN of SNS topic to which the notificaions is to be published.
    '''

    sns = boto3.client('sns', region_name=region_name)
    s3 = boto3.client('s3' , region_name=region_name)
    s3r = boto3.resource('s3' , region_name=region_name)

    response = s3.list_objects(Bucket = log_bucket, Prefix = job_log_dir+'/'+partition)
    

def does_s3key_exist(bucket, key, ext):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket)
    objects = bucket.objects.all()
    FOUND=0
    for object in objects:
        if object.key.startswith(key) and object.key.endswith(ext):
            FOUND=1
    return FOUND



# -------------------------------------------------------------------------
#   Turn DEBUG ON if temporary tables are desired. DEBUG creates additional temporary tables for every step in the script.
#    DEBUG: If 'True', the script will store all dataframes, including the temporary ones.
#    INTERACTIVE: Set 'True' for Jupyter Notebook.
#                 Set 'False' for AWS Glue ETL job.
# -------------------------------------------------------------------------

INTERACTIVE=False
DEBUG=True  

if INTERACTIVE:
    JOB_DATE='2020-08-06'
    from awsglue.context import GlueContext
else:
    parser = argparse.ArgumentParser()
    parser.add_argument('--JOB_DATE', dest='JOB_DATE')
    args = parser.parse_args()
    print(args)
    JOB_DATE=args.JOB_DATE

# -------------------------------------------------------------------------
# MODIFY AS PER JOB
#    These are the variables that drive the whole job.
#    Modify each variable for each job accordingly.
# -------------------------------------------------------------------------

# Variables for GLue Tables
JOB_NAME='renewable-curation'
REGION_NAME='us-east-1'
UID=uuid.uuid4().hex
PARTITION='dt='+JOB_DATE

def get_partition():
    return JOB_DATE

# Variables for RAW Table Location on S3 and Glue Catalog Database
CATALOG_DATABASE='renewable'
RAW_DATABASE='renewable'
RAW_BUCKET='aws-analytics-course'
RAW_TAB_PREFIX='raw/files/renewable/'
RAW_TAB_LOCATION='s3://'+RAW_BUCKET+'/'+RAW_TAB_PREFIX

# Variables for Curated Table Location on S3 and Glue Catalog Database
CURATED_BUCKET='aws-analytics-course'
CURATED_TAB_LOCATION= 's3://'+RAW_BUCKET+'/curated/renewable'

# Variables for crawler.
CRAWLER_NAME=JOB_NAME+'_'+UID
CRAWLER_ARN='arn:aws:iam::175908995626:role/glue-role'

# -------------------------------------------------------------------------
# MODIFY WITH CARE
# -------------------------------------------------------------------------

sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
log = []
s3pathlist=[]

if not INTERACTIVE:
    spark = SparkSession(sc)
    
client = boto3.client('glue', region_name=REGION_NAME)

if does_s3key_exist(RAW_BUCKET, RAW_TAB_PREFIX+'hydropower-consumption/'+get_partition(), '') == 1:
    hydropower_consumption_df=spark.read.csv(RAW_TAB_LOCATION+'hydropower-consumption/'+get_partition(), header=True)
    hydropower_consumption_df=hydropower_consumption_df.withColumnRenamed("Hydropower (Terawatt-hours)",'consumption') \
                                                   .withColumn('Year', f.col('Year').cast(IntegerType())) \
                                                   .withColumn('consumption', f.col('consumption').cast(FloatType()))
    write_s3_file(hydropower_consumption_df, CURATED_TAB_LOCATION, 'hydropower_consumption', PARTITION, uid=None)
    append_path_to_list(s3pathlist, CURATED_TAB_LOCATION, 'hydropower_consumption') 
    #print(s3pathlist)
    #hydropower_consumption_df.printSchema()
    #hydropower_consumption_df.show(5)

if does_s3key_exist(RAW_BUCKET, RAW_TAB_PREFIX+'renewable-energy-consumption/'+get_partition(), '') == 1:
    renewable_energy_consumption_df=spark.read.csv(RAW_TAB_LOCATION+'renewable-energy-consumption/'+get_partition(), header=True)
    renewable_energy_consumption_df=renewable_energy_consumption_df \
          .withColumnRenamed("Other renewables (modern biofuels, geothermal, wave & tidal) (terawatt-hours)",'Other_renewables') \
          .withColumnRenamed("Traditional biofuels (terrawatt-hours)",'Traditional_biofuels') \
          .withColumnRenamed("Wind (Terawatt-hours)",'Wind') \
          .withColumnRenamed("Solar PV (Terawatt-hours)",'Solar') \
          .withColumnRenamed("Hydropower (TWh)",'Hydropower') \
          .withColumn('Year', f.col('Year').cast(IntegerType())) \
          .withColumn('Traditional_biofuels', f.col('Traditional_biofuels').cast(FloatType())) \
          .withColumn('Other_renewables', f.col('Other_renewables').cast(FloatType())) \
          .withColumn('Wind', f.col('Wind').cast(FloatType())) \
          .withColumn('Solar', f.col('Solar').cast(FloatType())) \
          .withColumn('Hydropower', f.col('Hydropower').cast(FloatType())) 

    write_s3_file(renewable_energy_consumption_df, CURATED_TAB_LOCATION, 'renewable_energy_consumption', PARTITION, uid=None)
    append_path_to_list(s3pathlist, CURATED_TAB_LOCATION, 'renewable_energy_consumption') 
    #print(s3pathlist)
    #renewable_energy_consumption_df.printSchema()
    #renewable_energy_consumption_df.show(5)

if does_s3key_exist(RAW_BUCKET, RAW_TAB_PREFIX+'solar-energy-consumption/'+get_partition(), '') == 1:
    solar_energy_consumption_df=spark.read.csv(RAW_TAB_LOCATION+'solar-energy-consumption/'+get_partition(), header=True)

    solar_energy_consumption_df=solar_energy_consumption_df \
              .withColumnRenamed("Solar PV Consumption (Terawatt-hours)",'consumption') \
              .withColumn('Year', f.col('Year').cast(IntegerType())) \
              .withColumn('consumption', f.col('consumption').cast(FloatType())) 
    
    write_s3_file(solar_energy_consumption_df, CURATED_TAB_LOCATION, 'solar_energy_consumption', PARTITION, uid=None)
    append_path_to_list(s3pathlist, CURATED_TAB_LOCATION, 'solar_energy_consumption') 
    #print(s3pathlist)
    #solar_energy_consumption_df.printSchema()
    #solar_energy_consumption_df.show(5)

if does_s3key_exist(RAW_BUCKET, RAW_TAB_PREFIX+'wind-energy-consumption-terawatt-hours-twh/'+get_partition(), '') == 1:
    wind_energy_consumption_df=spark.read.csv(RAW_TAB_LOCATION+'wind-energy-consumption-terawatt-hours-twh/'+get_partition(), header=True)

    wind_energy_consumption_df=wind_energy_consumption_df \
              .withColumnRenamed("Wind energy consumption (Terawatt-hours)",'consumption') \
              .withColumn('Year', f.col('Year').cast(IntegerType())) \
              .withColumn('consumption', f.col('consumption').cast(FloatType())) 
    
    write_s3_file(wind_energy_consumption_df, CURATED_TAB_LOCATION, 'wind_energy_consumption', PARTITION, uid=None)
    append_path_to_list(s3pathlist, CURATED_TAB_LOCATION, 'wind_energy_consumption') 
    #print(s3pathlist)
    #wind_energy_consumption_df.printSchema()
    #wind_energy_consumption_df.show(5)

# -------------------------------------------------------------------------
# Crawl tables
# -------------------------------------------------------------------------

try:
    create_crawler(client, CRAWLER_NAME, CRAWLER_ARN, RAW_DATABASE)
    update_crawler(client, CRAWLER_NAME, s3pathlist)
    start_crawler(client, CRAWLER_NAME)
    delete_crawler(client, CRAWLER_NAME)
    append_log(log, str(datetime.datetime.now()), 'Crawling of tables : ','SUCCESS')
except Exception as e:
    if INTERACTIVE:
        delete_crawler(client, CRAWLER_NAME)
        raise e
    else:
        delete_crawler(client, CRAWLER_NAME)
        raise e



