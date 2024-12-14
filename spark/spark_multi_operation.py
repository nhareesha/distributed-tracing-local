from pyspark.sql import SparkSession
import time
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource


# Initialize Spark session
spark = SparkSession.builder.appName("EnhancedSparkTracingExample").getOrCreate()

# Initialize OpenTelemetry tracer with Jaeger exporter
tracer_provider = TracerProvider(
    resource=Resource.create({SERVICE_NAME: "spark-enhanced-tracing-example"})
)

# Configure OTLP exporter for Jaeger
otlp_exporter = OTLPSpanExporter(endpoint="http://jaeger:4317")  # Replace with your OTLP endpoint
span_processor = BatchSpanProcessor(otlp_exporter)
tracer_provider.add_span_processor(span_processor)

# Initialize MemorySpanExporter (for debugging traces in memory)
memory_exporter = InMemorySpanExporter()
span_processor_memory = BatchSpanProcessor(memory_exporter)
tracer_provider.add_span_processor(span_processor_memory)

# Set global tracer provider
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

def main():
    with tracer.start_as_current_span("main_spark_job") as main_span:
        print("Starting Spark job with enhanced tracing.")

        # Step 1: Create a DataFrame
        with tracer.start_as_current_span("step_1_create_dataframe") as span:
            time.sleep(1)  # Simulate work
            df = spark.range(0, 100)
            span.set_attribute("rows", 100)
            span.set_attribute("columns", 1)
            print("DataFrame created.")

        # Step 2: Perform a transformation
        with tracer.start_as_current_span("step_2_filter_dataframe") as span:
            time.sleep(2)  # Simulate work
            filtered_df = df.filter("id % 2 == 0")
            span.set_attribute("filtered_rows", filtered_df.count())
            print("DataFrame filtered.")

        # Step 3: Perform an aggregation
        with tracer.start_as_current_span("step_3_aggregate_dataframe") as span:
            time.sleep(2)  # Simulate work
            aggregated_df = filtered_df.groupBy().sum("id")
            result = aggregated_df.collect()
            span.set_attribute("aggregated_result", result[0][0] if result else None)
            print("DataFrame aggregated.")

        # Step 4: Write the result
        with tracer.start_as_current_span("step_4_write_dataframe") as span:
            time.sleep(1)  # Simulate work
            output_path = "/tmp/spark-output"
            aggregated_df.write.mode("overwrite").csv(output_path)
            span.set_attribute("output_path", output_path)
            print(f"DataFrame written to {output_path}.")

        # After the job, inspect traces in memory
        for span in memory_exporter.get_finished_spans():
            print("Finished Span:", span.name, span.attributes)

if __name__ == "__main__":
    main()

