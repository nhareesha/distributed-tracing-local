# spark/spark_job.py
from pyspark.sql import SparkSession
import time
from opentelemetry import trace

# Initialize Spark session
spark = SparkSession.builder.appName("SparkTracingExample").getOrCreate()

# Initialize OpenTelemetry tracer
tracer = trace.get_tracer(__name__)

def main():
    with tracer.start_as_current_span("spark_job"):
        print("Running Spark job with tracing enabled.")
        # Simulate job execution
        time.sleep(2)
        df = spark.range(0, 10)
        df.show()

if __name__ == "__main__":
    main()

