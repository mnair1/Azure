# -------------------------------------------------------------------------
# MODIFY WITH CARE
# Standard libraries to be used in AWS Glue jobs
# -------------------------------------------------------------------------

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from pyspark.sql.session import SparkSession
from awsglue.job import Job
from pyspark.sql import functions as f
from pyspark.sql.types import *
from pyspark.sql.types import StructType, StructField, FloatType, IntegerType, StringType, array, ArrayType, DateType
from pyspark.sql import Row, Column
import datetime
import json
import boto3
import logging
import calendar
import uuid
import time
from datetime import timedelta
from dateutil import relativedelta
import botocore
import argparse

def get_partition():
    return str(datetime.datetime.now().date())

def get_raw_table_name(tables, i):
    location=tables['TableList'][i]['StorageDescriptor']['Location']
    return location[location.rindex(".")+1: len(location) ]

def get_raw_table_columns(client, catalog_database, catalog_table):
    table = client.get_table(DatabaseName=catalog_database,Name=catalog_table)
    return table['Table']['StorageDescriptor']['Columns']

def handle_error(spark, log, message, region_name, log_bucket, job_log_dir, job_log_location, partition, sns_arn):
    '''
        function: handle_error
        description: Stops the program, logs the event, sends a SNS notification.

        Args:
            spark: Spark session object.
            log: List of logs.
            message: Exception that has happened.
            region_name: Name of the AWS region.
            log_bucket: Bucket name for logs.
            job_log_dir: Key of logs directory.
            job_log_location: Location of logs.
            partition: Date by which logs are paritioned.
            sns_arn: ARN of SNS topic.
    '''
    append_log(log, str(datetime.datetime.now()), str(message), 'FAILURE')
    log_df=create_log_df(spark, log)
    log_df.show()
    write_s3_file(log_df, job_log_location, '', partition, format='CSV')
    job_notification_sns(region_name, log_bucket, job_log_dir, partition, sns_arn)
    raise message

def create_crawler(client, crawler_name, iam_role_arn, database_name):
    return client.create_crawler(
        Name=crawler_name,
        Role=iam_role_arn,
        DatabaseName=database_name,
        Targets={
            'S3Targets':[
                {'Path':'s3://bucket/placeholder'}
            ]},
        SchemaChangePolicy={
            "UpdateBehavior": "LOG",
            "DeleteBehavior": "DEPRECATE_IN_DATABASE"
        },
        Configuration="{\"Version\":1.0,\"CrawlerOutput\":{\"Partitions\":{\"AddOrUpdateBehavior\":\"InheritFromTable\"}},\"Grouping\":{\"TableGroupingPolicy\":\"CombineCompatibleSchemas\"}}"
        )

def read_table_from_catalog(glueContext, database, table_name):
    '''
    function: read_table_from_catalog
    description: Reads a table using Glue catalog.

    Args:
        glueContext: GlueContext class object.
        database: Glue catalog database name.
        table_name: Glue catalog table name.
    
    Returns:
        spark.sql.dataframe: Returns a object of Spark Dataframe containing data of the table coming from Glue catalog.
    '''
    return glueContext.create_dynamic_frame.from_catalog(
             database=database,
             table_name=table_name).toDF()

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
                df.write.mode('append').parquet(table_location+'/'+table+'/'+partition)
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
    JOB_DATE='2020-07-14'
else:
    args = getResolvedOptions(sys.argv, ['JOB_DATE'])
    JOB_DATE=args['JOB_DATE']


# -------------------------------------------------------------------------
# MODIFY AS PER JOB
#    These are the variables that drive the whole job.
#    Modify each variable for each job accordingly.
# -------------------------------------------------------------------------

# Variables for Glue Tables
JOB_NAME='non-renewable'
REGION_NAME='us-east-1'
UID=uuid.uuid4().hex

# Variables for Job Log
LOG_BUCKET='aws-analytics-course'
JOB_LOG_DIR='log/'+JOB_NAME
JOB_LOG_LOCATION='s3://'+LOG_BUCKET+'/'+JOB_LOG_DIR
SNS_ARN='arn:aws:sns:us-east-1:175908995626:monitor-alert'
TODAY = get_partition()
UPDATED=datetime.datetime.today().replace(second=0, microsecond=0)

#INCRFILE_PREFIX=datetime.date.today().strftime('%Y')+datetime.date.today().strftime('%m')+str((int(datetime.date.today().strftime('%d'))))
LAST_DAY = datetime.datetime.strptime(JOB_DATE, '%Y-%m-%d').date() - timedelta(days=1)
PARTITION='dt='+str(LAST_DAY)
INCRFILE_PREFIX=str(LAST_DAY.strftime('%Y')+LAST_DAY.strftime('%m')+LAST_DAY.strftime('%d'))
#print(INCRFILE_PREFIX)

# Variables for RAW Table Location on S3 and Glue Catalog Database
CATALOG_DATABASE='non-renewable'
RAW_DATABASE='non-renewable'
RAW_BUCKET='aws-analytics-course'
RAW_SUFFIX='raw/dms/fossil/'
RAW_TAB_LOCATION='s3://'+RAW_BUCKET+'/'+RAW_SUFFIX+'/'

# Variables for Curated Table Location on S3 and Glue Catalog Database
CURATED_BUCKET='aws-analytics-course'
CURATED_TAB_LOCATION= 's3://'+RAW_BUCKET+'/curated/'+JOB_NAME

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
s3 = boto3.client('s3', region_name=REGION_NAME)

coal_prod_schema = StructType([StructField("Mode", StringType()),
                               StructField("Entity", StringType()),
                               StructField("Code", StringType()),
                               StructField("Year", IntegerType()),
                               StructField("Production", DecimalType(10,2)),
                               StructField("Consumption", DecimalType(10,2))
                               ])
if does_s3key_exist(RAW_BUCKET, RAW_SUFFIX+'coal_prod/'+INCRFILE_PREFIX, '.csv') == 1:
    coal_prod_df=spark.read.csv(RAW_TAB_LOCATION+'coal_prod/'+INCRFILE_PREFIX+'*.csv', header=False, schema=coal_prod_schema)
    coal_prod_df=coal_prod_df.withColumn('Updated', f.lit(UPDATED))
    write_s3_file(coal_prod_df, CURATED_TAB_LOCATION, 'coal_prod', PARTITION, uid=None)
    append_path_to_list(s3pathlist, CURATED_TAB_LOCATION, 'coal_prod') 
    #print(s3pathlist)
    #coal_prod_df.show(5)

fossil_capita_schema = StructType([StructField("Mode", StringType()),
                               StructField("Entity", StringType()),
                               StructField("Code", StringType()),
                               StructField("Year", IntegerType()),
                               StructField("Coal", DecimalType(10,2)),
                               StructField("Crude_oil", DecimalType(10,2)),
                               StructField("Natural_gas", DecimalType(10,2))
                               ])

if does_s3key_exist(RAW_BUCKET, RAW_SUFFIX+'fossil_capita/'+INCRFILE_PREFIX, '.csv') == 1:
    fossil_capita_df=spark.read.csv(RAW_TAB_LOCATION+'fossil_capita/'+INCRFILE_PREFIX+'*.csv', header=False, schema=fossil_capita_schema)
    fossil_capita_df=fossil_capita_df.withColumn('Updated', f.lit(UPDATED))
    write_s3_file(fossil_capita_df, CURATED_TAB_LOCATION, 'fossil_capita', PARTITION, uid=None)
    append_path_to_list(s3pathlist, CURATED_TAB_LOCATION, 'fossil_capita') 
    #print(s3pathlist)
    #fossil_capita_df.show(5)

gas_prod_schema = StructType([StructField("Mode", StringType()),
                               StructField("Entity", StringType()),
                               StructField("Code", StringType()),
                               StructField("Year", IntegerType()),
                               StructField("Production", DecimalType(10,2))
                               ])

if does_s3key_exist(RAW_BUCKET, RAW_SUFFIX+'gas_prod/'+INCRFILE_PREFIX, '.csv') == 1:
    gas_prod_df=spark.read.csv(RAW_TAB_LOCATION+'gas_prod/'+INCRFILE_PREFIX+'*.csv', header=False, schema=gas_prod_schema)
    gas_prod_df=gas_prod_df.withColumn('Updated', f.lit(UPDATED))
    write_s3_file(gas_prod_df, CURATED_TAB_LOCATION, 'gas_prod', PARTITION, uid=None)
    append_path_to_list(s3pathlist, CURATED_TAB_LOCATION, 'gas_prod') 
    #print(s3pathlist)
    #gas_prod_df.show(5)

oil_prod_schema = StructType([StructField("Mode", StringType()),
                               StructField("Entity", StringType()),
                               StructField("Code", StringType()),
                               StructField("Year", IntegerType()),
                               StructField("Production", DecimalType(10,2))
                               ])

if does_s3key_exist(RAW_BUCKET, RAW_SUFFIX+'oil_prod/'+INCRFILE_PREFIX, '.csv') == 1:
    oil_prod_df=spark.read.csv(RAW_TAB_LOCATION+'oil_prod/'+INCRFILE_PREFIX+'*.csv', header=False, schema=oil_prod_schema)
    oil_prod_df=oil_prod_df.withColumn('Updated', f.lit(UPDATED))
    write_s3_file(oil_prod_df, CURATED_TAB_LOCATION, 'oil_prod', PARTITION, uid=None)
    append_path_to_list(s3pathlist, CURATED_TAB_LOCATION, 'oil_prod') 
    #print(s3pathlist)
    #oil_prod_df.show(5)

# -------------------------------------------------------------------------
# Crawl tables
# -------------------------------------------------------------------------

try:
    create_crawler(client, CRAWLER_NAME, CRAWLER_ARN, RAW_DATABASE)
    update_crawler(client, CRAWLER_NAME, s3pathlist)
    start_crawler(client, CRAWLER_NAME)
    delete_crawler(client, CRAWLER_NAME)
    append_log(log, str(datetime.datetime.now()), 'Crawling of AMS tables : ','SUCCESS')
except Exception as e:
    if INTERACTIVE:
        delete_crawler(client, CRAWLER_NAME)
        raise e
    else:
        delete_crawler(client, CRAWLER_NAME)
        


