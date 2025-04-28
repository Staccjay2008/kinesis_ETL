FROM bitnami/spark:3.3.0

USER root

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ETL script
COPY spark-stream.py /app/spark-stream.py

WORKDIR /app

# Default command to run the ETL
CMD ["spark-submit", "spark-stream.py"]