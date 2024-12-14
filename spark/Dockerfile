FROM openjdk:11-jre-slim

# Install dependencies
RUN apt-get update && apt-get install -y wget tar

# Install dependencies and Python3
RUN apt-get update && apt-get install -y \
    wget \
    tar \
    python3 \
    python3-pip  # Add Python 3 and pip for package management

RUN pip3 install --no-cache-dir opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation opentelemetry-exporter-otlp opentelemetry-exporter-jaeger
RUN pip3 install --no-cache-dir apache-airflow-providers-apache-spark

# Install OpenTelemetry Java agent (from Maven Central)
RUN mkdir /otel-java-agent && \
    wget https://repo1.maven.org/maven2/io/opentelemetry/javaagent/opentelemetry-javaagent/2.5.0/opentelemetry-javaagent-2.5.0.jar -O /otel-java-agent/otel-javaagent.jar

# Install Spark
RUN wget https://archive.apache.org/dist/spark/spark-3.2.0/spark-3.2.0-bin-hadoop3.2.tgz && \
    tar xvf spark-3.2.0-bin-hadoop3.2.tgz && \
    mv spark-3.2.0-bin-hadoop3.2 /spark && \
    rm spark-3.2.0-bin-hadoop3.2.tgz  # Clean up the tar file to reduce image size

# Set up Spark environment variables
ENV SPARK_HOME=/spark
ENV PATH=$SPARK_HOME/bin:$PATH

# Set Java options for OpenTelemetry Java agent
ENV JAVA_OPTS="-javaagent:/otel-java-agent/otel-javaagent.jar"

# Copy the Spark job Python script
COPY spark_job.py /spark/spark_job.py

# Set working directory
WORKDIR /spark

# Run Spark submit with OpenTelemetry Java agent
CMD ["spark-submit", "--conf", "spark.jars=/otel-java-agent/otel-javaagent.jar", "/spark/spark_job.py"]

