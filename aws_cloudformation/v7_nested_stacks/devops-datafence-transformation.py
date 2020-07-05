# -------------------------------------------------------------------------
# Standard libraries
# -------------------------------------------------------------------------

import sys
from pyspark.context import SparkContext
from pyspark.sql.session import SparkSession
from pyspark.sql import functions as f
from pyspark.sql.types import *
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, array, ArrayType, DateType
from pyspark.sql import Row, Column


sc = SparkContext.getOrCreate()
spark = SparkSession(sc)
    
# -------------------------------------------------------------------------
# Create reusable functions
# -------------------------------------------------------------------------
	
def read_s3_file(spark, type, path, delimiter='|', header='true'):
    if (type == 'CSV'):
        return spark.read.format("com.databricks.spark.csv").option("header", header).option("delimiter", delimiter).load(path)
    if (type == 'PARQUET'):
        return spark.read.parquet(path)
    
def write_s3_file(df, table_location, table, partition=None, format='PARQUET', delimiter='\t', coalesce=1, header=False):
    if format == 'PARQUET':
        df.write.parquet(table_location+'/'+table+'/'+partition, mode = "overwrite")
    if format == 'CSV':
        df.coalesce(coalesce).write.option("delimiter", delimiter).option("quote", "\"").option("quoteAll", "true").csv(table_location +'/' + partition)

S3Bucket='devops-datafence-us-east-1-175908995626-s3-bucket-cf'
sample_file = 'sample_input.csv'


S3CONSUMPPTIONFILE='s3://'+S3Bucket+'/'+sample_file
print(S3CONSUMPPTIONFILE)
consumption_df=read_s3_file(spark, 'CSV', S3CONSUMPPTIONFILE, delimiter=',',header='true')
consumption_df.show(10)

S3WRITECONSUMPPTIONFILE='s3://'+S3Bucket+'/'+sample_file + ".out"
write_s3_file(consumption_df, S3WRITECONSUMPPTIONFILE, "", format='CSV', delimiter=",", partition="001")