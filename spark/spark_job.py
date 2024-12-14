from pyspark.sql import SparkSession
import time
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource


# Init Spark session
spark = SparkSession.builder.appName("SparkTracingExample").getOrCreate()

# Initialize OpenTelemetry tracer with Jaeger exporter
tracer_provider = TracerProvider(
    resource=Resource.create({SERVICE_NAME: "spark-tracing-example"})
)


# Configure OTLP exporter for Jaeger
# otlp_exporter = OTLPSpanExporter(endpoint="grpc://jaeger:14250")  # 172.19.0.2 Replace with  OTLP endpoint
otlp_exporter = OTLPSpanExporter(endpoint="http://jaeger:4317")  # 172.19.0.2 Replace with OTLP endpoint

span_processor = BatchSpanProcessor(otlp_exporter)
tracer_provider.add_span_processor(span_processor)



# Init MemorySpanExporter (for debugging traces in memory)
memory_exporter = InMemorySpanExporter()

# Set up the BatchSpanProcessor with JaegerExporter and MemorySpanExporter
span_processor_memory = BatchSpanProcessor(memory_exporter)

# Add span processors to the tracer provider
tracer_provider.add_span_processor(span_processor_memory)

# Set global tracer provider
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

def main():
    with tracer.start_as_current_span("spark_job"):
        print("Running Spark job with tracing enabled.")
        # Simulate job execution
        time.sleep(2)
        df = spark.range(0, 10)
        df.show()

        # After the job, inspect traces in memory
        # This will print the collected spans in memory for debugging
        for span in memory_exporter.get_finished_spans():
            print("Finished Span:", span)

if __name__ == "__main__":
    main()

