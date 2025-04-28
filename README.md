# Data Engineer Mini ETL Pipeline

---

## 📚 Official Problem Statement

### Objective

Develop a data processing pipeline that transforms a large volume of text data from a Kinesis stream into a format suitable for the continuous training of a text summarization model. The pipeline should leverage Python and be designed with enterprise-scale data processing tools in mind.

---

### Background

You're part of a dynamic team at a company specializing in NLP services dedicated to assisting news aggregators and content curators. The company's mission is to automate the summarization of articles and reports from diverse sources, enabling rapid access to distilled insights. This task is crucial for staying ahead in the fast-paced world of news and content curation, where the ability to quickly summarize and understand large volumes of text data can provide a significant competitive edge.

---

### Overview

The NLP model must be trained on a regular schedule to keep up-to-date on the stylistic elements of modern journalism. Therefore in this challenge, you are entrusted with the development of a data pipeline capable of processing incoming text data efficiently. The ultimate goal is to enhance this data in ways that bolster machine learning (ML) training scenarios. This includes considering how the result is stored, ensuring that it supports efficient data access patterns suitable for large-scale processing and ML model training.

---

### Challenge Requirements

- Retrieve each record from a Kinesis stream.
- Enrich each record by adding a calculated feature (e.g., word count).
- Compute the average of this metric across records.
- Store the enriched records in an S3 bucket.
- Only the enriched records need to be stored; the calculated average does not need to be stored.

---

# 🚀 My Solution Overview

This project implements the full ETL pipeline using Spark and Python, running fully locally using Docker and LocalStack.

👉 Ingest data from Kinesis using **boto3**  
👉 Enrich records with **word count**  
👉 Save enriched records to **S3 (Parquet format)**  
👉 **Compute and print** hourly and daily word count averages (but **do not store** them)  
👉 Save **sample enriched records** locally for inspection

---

# ⚙️ Tech Stack

- **Apache Spark 3.3.0** (Structured batch processing)
- **Python 3.8** (boto3 for Kinesis integration)
- **LocalStack** (Simulating AWS S3 and Kinesis)
- **Docker + Docker Compose**

---

# 👩‍💻 How to Run the Project

### 1. Prerequisites

- Docker
- Docker Compose
- AWS CLI (optional, for checking LocalStack S3 contents)

---

### 2. Commands

From project root:

```bash
docker-compose up --build
```

📉 This will:
- Start LocalStack (simulated AWS services)
- Start the populate-script (publishing fake articles to Kinesis)
- Start the Spark ETL processor (ingesting, enriching, writing to S3)

---

# 📦 Project Structure

```
mini-etl-pipeline/
├── docker-compose.yml
├── populate-script/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── populate_stream.py
└── etl-processor/
    ├── Dockerfile
    ├── requirements.txt
    └── spark-etl.py
```

---

# 📚 Outputs

| Data | Location |
|:---|:---|
| Enriched records | `s3a://my-bucket/enriched/` |
| Sample enriched records (5 examples) | `/app/output/sample_enriched/` inside container |

📉 **Hourly and daily averages are printed to console only**, not stored in files.

---

# 📋 Design Decisions

- **Kinesis Ingestion:**  
  Instead of using Spark's native Kinesis connector (which is not available on public Maven Central), records are pulled manually from Kinesis using Python’s `boto3` client.

- **Data Enrichment:**  
  Added a new field `word_count` to measure article size, improving downstream ML feature engineering.

- **Storage Format:**  
  Enriched records are saved into Parquet format inside S3 for efficient ML training.

---

# 🧐 Assumptions Made

- Stream ingestion is implemented by polling Kinesis manually using boto3.
- A small sample (5 records) of enriched data is saved for local inspection.
- Hourly and daily word count averages are computed per batch, printed to console, but **not saved**.

---

# ✅ Known Limitations

- The job polls Kinesis every few seconds in mini-batches — it's not true continuous micro-batch streaming.
- Averaged metrics are transient (only available in real-time logs).

---

# 📩 Submission Note

This pipeline is fully Dockerized and runs locally without the need for real AWS accounts.  
It processes, enriches, and stores streaming text data for ML training preparation as specified.

---

