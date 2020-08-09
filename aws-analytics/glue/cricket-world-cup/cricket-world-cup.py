#!/usr/bin/env python
# coding: utf-8

# In[ ]:


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
from pyspark.sql import SQLContext
from pyspark.sql import HiveContext
from awsglue.job import Job
from pyspark.sql import functions as f
from pyspark.sql.types import *
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, array, ArrayType, DateType
from pyspark.sql import Row, Column
import datetime
import json
import boto3
import time
import logging
import calendar
import uuid
from dateutil import relativedelta
from dateutil.relativedelta import relativedelta
from awsglue.utils import getResolvedOptions


# In[ ]:


# Edit Variables below as per AWS account

INTERACTIVE=False
DEBUG=True  

if INTERACTIVE:
    JOB_DATE='20200708'
else:
    args = getResolvedOptions(sys.argv, ['JOB_DATE'])
    JOB_DATE=args['JOB_DATE']

S3PATHREAD="s3://aws-analytics-course/raw/cricket-world-cup/"+JOB_DATE+"/"
S3PATHWRITE="s3://aws-analytics-course/curated/cricket-world-cup"
REGION_NAME='us-east-1'
PARTITION='dt='+JOB_DATE
CATALOG_TABLE_LIST=[]

CURATED_DATABASE='curated_worldcup'

BOWLER_TBL='bowlers'

CRAWLER_NAME='worldcup'
CRAWLER_ARN='arn:aws:iam::175908995626:role/glue-role'


# In[ ]:


# -------------------------------------------------------------------------
# MODIFY WITH CARE
# -------------------------------------------------------------------------

sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
log = []
s3pathlist=[]

if not INTERACTIVE:
    spark = glueContext.spark_session
    
client = boto3.client('glue', region_name=REGION_NAME)


# In[ ]:


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
            ]}
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


# In[ ]:


bowler_df=read_s3_file(spark, 'CSV', S3PATHREAD+"Bowler_data.csv", delimiter=',',header='true')
bowler_df.show(5)


# In[ ]:


bowler_df=bowler_df           .withColumnRenamed('_c0','ID')           .withColumn('Overs', f.col('Overs').cast(IntegerType()))           .withColumn('Mdns', f.col('Mdns').cast(IntegerType()))           .withColumn('Runs', f.col('Runs').cast(IntegerType()))           .withColumn('Wkts', f.col('Wkts').cast(IntegerType()))           .withColumn('Econ', f.col('Econ').cast(IntegerType()))           .withColumn('Ave', f.col('Ave').cast(IntegerType()))           .withColumn('Player_ID', f.col('Player_ID').cast(IntegerType()))

bowler_df.show(5)


# In[ ]:


bowler_df.printSchema()


# In[ ]:


bowler_df.registerTempTable('bowlers')


# In[ ]:


bowler_df = spark.sql(" SELECT `ID`,`Overs`,`Mdns`,`Runs`,`Wkts`,`Econ`,`Ave`,`SR`, "                       " SUBSTR(`Opposition`, 2,20) as `Opposition`, "                       " `Ground`, TO_DATE(`Start Date`, 'dd MMM yyyy') AS Start_Date, "                       " SUBSTR(Match_ID, 6,10) AS Match_Number,`Bowler`,`Player_ID` "                       " FROM bowlers")
bowler_df.count()


# In[ ]:


write_s3_file(bowler_df, S3PATHWRITE, BOWLER_TBL, PARTITION)
append_path_to_list(CATALOG_TABLE_LIST, S3PATHWRITE, BOWLER_TBL) 
print(CATALOG_TABLE_LIST)


# In[ ]:


# Filtering using Dataframe commands
bowler_df.filter(bowler_df.Player_ID == 28081).count()


# In[ ]:


# Filtering using Spark SQL commands
spark.sql("SELECT * FROM bowlers where Player_ID = 28081").count()


# In[ ]:


# Average overs did a bowler bowl
avg_bowler_df = bowler_df.groupBy(bowler_df.Player_ID).avg('Overs')


# In[ ]:


avg_bowler_df.show()


# In[ ]:


avg_bowler_df = spark.sql("SELECT Player_ID, avg(Overs) FROM bowlers GROUP BY Player_ID")


# In[ ]:


avg_bowler_df.show()


# In[ ]:


# Bowlers with lowest Economy Rate per over
econ_bowler_df = spark.sql("SELECT Player_ID, (SELECT min(Econ) FROM bowlers) as Econ "                             " FROM bowlers WHERE Econ=(SELECT min(Econ) FROM bowlers)")
econ_bowler_df.show()


# In[ ]:


# Match Numbers played in Port of Spain
econ_bowler_df = spark.sql("SELECT DISTINCT SUBSTR(Match_ID, 6,10) AS Match_Number "                             " FROM bowlers WHERE Ground='Port of Spain'")
econ_bowler_df.show()


# In[ ]:


# -------------------------------------------------------------------------
# Script to delete previously catalogued tables
# -------------------------------------------------------------------------

delete_catalog_table(client, CURATED_DATABASE, BOWLER_TBL) 


# In[ ]:


# -------------------------------------------------------------------------
# Crawl tables
# -------------------------------------------------------------------------
create_crawler(client, CRAWLER_NAME, CRAWLER_ARN, CURATED_DATABASE)
update_crawler(client, CRAWLER_NAME, CATALOG_TABLE_LIST)
start_crawler(client,  CRAWLER_NAME)
delete_crawler(client, CRAWLER_NAME)


# In[ ]:




