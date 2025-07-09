# Smart City Real-Time ELT Pipeline

## About

This project simulates a real-time Smart City environment using streaming IoT data (vehicles, GPS, traffic cameras, weather, and emergency events). It demonstrates how to build an end-to-end ELT data pipeline using Apache Kafka, Apache Spark, AWS S3, AWS Glue, Athena, and Redshift.

## Description

The pipeline consists of:
- Simulated IoT devices sending real-time data to Kafka topics.
- Apache Spark consuming Kafka topics and writing the data to Amazon S3 in Parquet format.
- AWS Glue crawling the data to create tables.
- Amazon Athena and Redshift Spectrum used for querying the data later.

This project is entirely containerized using Docker Compose.

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd smart-city-pipeline
```

### 2. Start Kafka, Zookeeper, and Spark via Docker Compose
```bash
docker-compose up -d
```

Make sure your `docker-compose.yml` includes `zookeeper`, `kafka`, and `spark`.

### 3. Start Producing Simulated Data
```bash
python producer.py
```

This script sends data to multiple Kafka topics like `vehicle_data`, `gps_data`, etc.

### 4. Start Spark Stream Processing
```bash
python spark_streaming.py
```

This script reads from Kafka, processes the data, and writes Parquet files to S3.

---

### 5. AWS Setup

- **Create an S3 bucket** (e.g., `smartcity-spark-streaming-data-tejas`)
- Add the bucket name and AWS credentials in your `config.py`
- Example:
  ```python
  configuration = {
      "AWS_ACCESS_KEY": "<your-access-key>",
      "AWS_SECRET_KEY": "<your-secret-key>"
  }
  ```

- **Create a Glue Crawler**:
  - Target: S3 bucket path used in Spark output
  - Output: Create a new database and tables

- **Query Data with Athena or Redshift**:
  - In Athena: Point to the Glue database and run queries
  - In Redshift Spectrum: Use external schema to query S3 tables

## Architecture

The following diagram illustrates the full architecture of the Smart City pipeline:

![image](https://github.com/user-attachments/assets/30b4ac7e-9aed-4358-9d24-dbbe5970a4a0)

1. Python producers simulate smart city data and send it to Kafka.
2. Spark consumes Kafka topics, processes data, and writes to Amazon S3.
3. AWS Glue crawls the S3 data and creates schema tables.
4. Athena and Redshift Spectrum are used for downstream SQL-based querying.

## Technologies Used

- Apache Kafka, Zookeeper
- Apache Spark Structured Streaming
- Python
- Amazon S3, Glue, Athena, Redshift Spectrum
- Docker & Docker Compose

## Notes

- This project follows the **ELT** pattern: data is loaded first into S3, then transformed via Glue/Athena.
- Checkpointing is used in Spark to support exactly-once semantics.
