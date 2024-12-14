from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from datetime import datetime
import time

# Configure OpenTelemetry Tracer with a custom service name
trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({"service.name": "airflow_tracing"})
    )
)

# Configure Jaeger Exporter
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",  # Use the hostname of your Jaeger service
    agent_port=6831,          # Default port for the Jaeger agent
)

# Add the Span Processor to the Tracer Provider
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))

# Initialize Tracer
tracer = trace.get_tracer(__name__)


def trace_task(task_id, task_name):
    """Task function that generates spans for tracing."""
    with tracer.start_as_current_span(task_name) as span:
        # Add task-specific attributes to the span
        span.set_attribute("task_id", task_id)
        span.set_attribute("task_name", task_name)

        try:
            print(f"Executing {task_name}")
            time.sleep(1)  # Simulate some processing
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.StatusCode.ERROR)


# Define the DAG
default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 12, 7),
    "depends_on_past": False,
}

dag = DAG(
    dag_id="spark_tracing_example",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
)

# Define Tasks
start_task = DummyOperator(task_id="start", dag=dag)

trace_task_1 = PythonOperator(
    task_id="trace_task_1",
    python_callable=trace_task,
    op_args=["trace_task_1", "Task 1"],  # Pass task_id and task_name
    dag=dag,
)

trace_task_2 = PythonOperator(
    task_id="trace_task_2",
    python_callable=trace_task,
    op_args=["trace_task_2", "Task 2"],
    dag=dag,
)

spark_task = SparkSubmitOperator(
    task_id="spark_task",
    application="/opt/airflow/spark_job.py",  # Path to your Spark job
    conn_id="spark_default",                 # Airflow Spark connection ID
    conf={"spark.master": "local[*]", "spark.submit.deployMode": "client"},  # Use local mode for testing (if needed)
    dag=dag,
)

# Define Task Dependencies
start_task >> trace_task_1 >> trace_task_2 >> spark_task

