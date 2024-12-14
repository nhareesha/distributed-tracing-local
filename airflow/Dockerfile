# Use the official Airflow image as base
FROM apache/airflow:2.6.2

# Switch to root user for installing dependencies
USER root

# Install required system dependencies (including procps for ps command and Java 11 for Spark)
RUN apt-get update && apt-get install -y \
    procps \
    openjdk-11-jdk \
    && rm -rf /var/lib/apt/lists/*

# Set the JAVA_HOME environment variable for OpenJDK 11 (Spark requires this)
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# Switch back to airflow user
USER airflow

# Install OpenTelemetry dependencies
RUN pip install --no-cache-dir \
    opentelemetry-api==1.15.0 \
    opentelemetry-sdk==1.15.0 \
    opentelemetry-instrumentation==0.39b0 \
    opentelemetry-exporter-jaeger==1.15.0 \
    apache-airflow-providers-apache-spark \
    opentelemetry-exporter-otlp

# Set up your working directory
WORKDIR /opt/airflow

# Copy your DAGs and plugins
COPY dags/ ./dags/
# Uncomment and modify this if you have custom plugins
# COPY plugins/ ./plugins/


