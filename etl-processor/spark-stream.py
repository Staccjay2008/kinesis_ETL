import boto3
import json
import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf, from_json, window, avg, to_timestamp
from pyspark.sql.types import StructType, StringType, IntegerType

# 1. Initialize Spark Session
spark = SparkSession.builder \
    .appName("ManualKinesisETLPipeline") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://localstack:4566") \
    .config("spark.hadoop.fs.s3a.access.key", "test") \
    .config("spark.hadoop.fs.s3a.secret.key", "test") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

# 2. Define the Schema
schema = StructType() \
    .add("article_id", StringType()) \
    .add("title", StringType()) \
    .add("author", StringType()) \
    .add("publish_date", StringType()) \
    .add("content", StringType())

# 3. Word Count UDF
@udf(IntegerType())
def word_count(content):
    if content:
        return len(content.split())
    return 0

# 4. Connect to Kinesis via boto3
kinesis_client = boto3.client(
    'kinesis',
    endpoint_url='http://localstack:4566',
    aws_access_key_id='test',
    aws_secret_access_key='test',
    region_name='us-east-1'
)

# Get shard iterator
response = kinesis_client.describe_stream(StreamName='MyStream')
shard_id = response['StreamDescription']['Shards'][0]['ShardId']

shard_iterator = kinesis_client.get_shard_iterator(
    StreamName='MyStream',
    ShardId=shard_id,
    ShardIteratorType='LATEST'
)['ShardIterator']

print("Starting manual Kinesis consumption...")

# 5. Main Loop
while True:
    record_response = kinesis_client.get_records(ShardIterator=shard_iterator, Limit=100)

    records = record_response['Records']
    shard_iterator = record_response['NextShardIterator']

    if not records:
        print("No new records, sleeping for 5 seconds...")
        time.sleep(5)
        continue

    # Decode and parse each record
    parsed_records = []
    for record in records:
        try:
            parsed = json.loads(record['Data'])
            parsed_records.append(parsed)
        except json.JSONDecodeError:
            continue

    if not parsed_records:
        continue

    # 6. Create DataFrame
    df = spark.createDataFrame(parsed_records, schema=schema)

    # 7. Enrich Data
    df = df.withColumn("word_count", word_count(col("content")))
    df = df.withColumn("publish_timestamp", to_timestamp(col("publish_date")))

    # Export a small sample (e.g., 5 records) to local file
    sample_records = df.limit(5)

    # Save as JSON inside the container
    sample_records.coalesce(1).write.mode("overwrite").json("/app/output/sample_enriched/")

    # 8. Write enriched data to S3
    df.write.mode("append").parquet("s3a://my-bucket/enriched/")

    print(f"Wrote {len(parsed_records)} enriched records to S3.")


    hourly_avg = df.groupBy(window(col("publish_timestamp"), "1 hour")) \
        .agg(avg("word_count").alias("avg_word_count_hour"))

    daily_avg = df.groupBy(window(col("publish_timestamp"), "1 day")) \
        .agg(avg("word_count").alias("avg_word_count_day"))

    print("Hourly Average Word Count:")
    hourly_avg.show(truncate=False)

    print("Daily Average Word Count:")
    daily_avg.show(truncate=False)


    time.sleep(10)
