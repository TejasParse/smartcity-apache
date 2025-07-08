from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, DoubleType, TimestampType, StructField, StringType, IntegerType
from pyspark.sql.functions import from_json, col
from config import configuration

def main():
    spark = SparkSession.builder.appName("SmartCityStreaming")\
    .config("spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,"
            "org.apache.hadoop:hadoop-aws:3.3.1,"
            "org.amazonaws:aws-java-sdk:1.11.469")\
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")\
    .config("spark.hadoop.fs.s3a.access.key", configuration.get("AWS_ACCESS_KEY"))\
    .config("spark.hadoop.fs.s3a.secret.key", configuration.get("AWS_SECRET_KEY"))\
    .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")\
    .getOrCreate()

    # Adjsut the log level to minimize the console output on executors
    spark.sparkContext.setLogLevel("WARN")

    # vehicle schema
    vehicleSchema = StructType([
        StructField("id", StringType(), True),
        StructField("deviceId", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("location", StringType(), True),
        StructField("speed", DoubleType(), True),
        StructField("direction", StringType(), True),
        StructField("make", StringType(), True),
        StructField("model", StringType(), True),
        StructField("year", IntegerType(), True),
        StructField("fuelType", StringType(), True),
    ])

    # gps schema
    gpsSchema = StructType([
        StructField("id", StringType(), True),
        StructField("deviceId", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("speed", DoubleType(), True),
        StructField("direction", StringType(), True),
        StructField("vehicleType", StringType(), True)
    ])

    # trafficSchema
    trafficSchema = StructType([
        StructField("id", StringType(), True),
        StructField("deviceId", StringType(), True),
        StructField("cammeraId", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("location", StringType(), True),
        StructField("snapShot", StringType(), True)
    ])

    # weatherData
    weatherSchema = StructType([
        StructField("id", StringType(), True),
        StructField("deviceId", StringType(), True),
        StructField("location", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("temperature", DoubleType(), True),
        StructField("weatherCondition", StringType(), True),
        StructField("precipitation", DoubleType(), True),
        StructField("windSpeed", DoubleType(), True),
        StructField("humidity", IntegerType(), True),
        StructField("airQualityIndex", DoubleType(), True),
    ])

    # emergencySchema
    emergencySchema = StructType([
        StructField("id", StringType(), True),
        StructField("deviceId", StringType(), True),
        StructField("incidentId", StringType(), True),
        StructField("type", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("location", StringType(), True),
        StructField("status", StringType(), True),
        StructField("description", StringType(), True),
    ])

    def read_kafka_topic(topic, schema):
        return (spark.readStream
                .format("kafka")
                .option("kafka.bootstrap.servers", "broker:29092")
                .option("subscribe", topic)
                .option("startingOffsets", "earliest")
                .load()
                .selectExpr("CAST(value AS STRING)")
                .select(from_json(col("value"), schema).alias("data"))
                .select("data.*")
                .withWatermark("timestamp", "2 minutes")
                )

    def streamWrite(input, checkpointFolder, output):
        return (input.writeStream
               .format("parquet")
               .option("checkpointLocation", checkpointFolder)
               .option("path", output)
               .outputMode("append")
               .start()
               )

    vehicleDF = read_kafka_topic("vehicle_data", vehicleSchema).alias("vehicle")
    gpsDF = read_kafka_topic("gps_data", gpsSchema).alias("gps")
    trafficDF = read_kafka_topic("traffic_data", trafficSchema).alias("traffic")
    weatherDF = read_kafka_topic("weather_data", weatherSchema).alias("weather")
    emergencyDF = read_kafka_topic("emergency_data", emergencySchema).alias("emergency")

    # Join all the dfs with idf and timestamp
    # join

    query1 = streamWrite(vehicleDF, f"s3a://{configuration.get("BUCKET_NAME")}/checkpoints/vehicle_data", 
                f"s3a://{configuration.get("BUCKET_NAME")}/data/vehicle_data")
    query2 = streamWrite(gpsDF, f"s3a://{configuration.get("BUCKET_NAME")}/checkpoints/gps_data", 
                f"s3a://{configuration.get("BUCKET_NAME")}/data/gps_data")
    query3 = streamWrite(trafficDF, f"s3a://{configuration.get("BUCKET_NAME")}/checkpoints/traffic_data", 
                f"s3a://{configuration.get("BUCKET_NAME")}/data/traffic_data")
    query4 = streamWrite(weatherDF, f"s3a://{configuration.get("BUCKET_NAME")}/checkpoints/weather_data", 
                f"s3a://{configuration.get("BUCKET_NAME")}/data/weather_data")
    query5 = streamWrite(emergencyDF, f"s3a://{configuration.get("BUCKET_NAME")}/checkpoints/emergency_data", 
                f"s3a://{configuration.get("BUCKET_NAME")}/data/emergency_data")
    
    query5.awaitTermination()


if __name__ == "__main__":
    main()