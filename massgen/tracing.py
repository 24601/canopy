"""
OpenTelemetry tracing configuration and utilities for MassGen Canopy.
Extensions and modifications for pluggable algorithms by Basit Mustafa (@24601).
"""

import os
import uuid
from contextlib import contextmanager
from functools import wraps
from typing import Any, Dict, Optional

from opentelemetry import trace
from opentelemetry.context import attach, detach, set_value
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.propagate import extract, inject
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Status, StatusCode

# Constants
MASSGEN_TRACE_ENABLED = os.getenv("MASSGEN_TRACE_ENABLED", "true").lower() == "true"
MASSGEN_TRACE_BACKEND = os.getenv("MASSGEN_TRACE_BACKEND", "duckdb")  # duckdb, otlp, jaeger, console
MASSGEN_OTLP_ENDPOINT = os.getenv("MASSGEN_OTLP_ENDPOINT", "http://localhost:4317")
MASSGEN_JAEGER_ENDPOINT = os.getenv("MASSGEN_JAEGER_ENDPOINT", "localhost:6831")
MASSGEN_SERVICE_NAME = os.getenv("MASSGEN_SERVICE_NAME", "massgen-canopy")
MASSGEN_TRACE_DB_PATH = os.getenv("MASSGEN_TRACE_DB_PATH", None)  # None = auto-generated path

# Context keys
CORRELATION_ID_KEY = "massgen.correlation_id"
ORCHESTRATION_ID_KEY = "massgen.orchestration_id"
ALGORITHM_KEY = "massgen.algorithm"


def setup_tracing() -> Optional[TracerProvider]:
    """Set up OpenTelemetry tracing with configured exporters."""
    if not MASSGEN_TRACE_ENABLED:
        return None

    resource = Resource.create(
        {
            "service.name": MASSGEN_SERVICE_NAME,
            "service.version": "1.0.0",
            "deployment.environment": os.getenv("MASSGEN_ENV", "development"),
        }
    )

    provider = TracerProvider(resource=resource)

    # Configure exporter based on backend
    if MASSGEN_TRACE_BACKEND == "duckdb":
        from .tracing_duckdb import DuckDBSpanExporter

        exporter = DuckDBSpanExporter(db_path=MASSGEN_TRACE_DB_PATH)
        print(f"📊 Tracing to DuckDB: {exporter.db_path}")
    elif MASSGEN_TRACE_BACKEND == "otlp":
        exporter = OTLPSpanExporter(
            endpoint=MASSGEN_OTLP_ENDPOINT, insecure=True  # For development; use secure in production
        )
    elif MASSGEN_TRACE_BACKEND == "jaeger":
        exporter = JaegerExporter(
            agent_host_name=MASSGEN_JAEGER_ENDPOINT.split(":")[0],
            agent_port=int(MASSGEN_JAEGER_ENDPOINT.split(":")[1]) if ":" in MASSGEN_JAEGER_ENDPOINT else 6831,
        )
    else:
        # Console exporter for debugging
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter

        exporter = ConsoleSpanExporter()

    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    # Instrument HTTP requests automatically
    RequestsInstrumentor().instrument()

    return provider


# Initialize tracing on module import
_tracer_provider = setup_tracing()


def get_tracer(name: str) -> trace.Tracer:
    """Get a tracer for a specific component."""
    if not MASSGEN_TRACE_ENABLED:
        return trace.get_tracer_provider().get_tracer(name)
    return trace.get_tracer(name)


def generate_correlation_id() -> str:
    """Generate a unique correlation ID."""
    return str(uuid.uuid4())


@contextmanager
def trace_context(
    correlation_id: Optional[str] = None, orchestration_id: Optional[str] = None, algorithm: Optional[str] = None
):
    """Context manager to propagate trace context."""
    tokens = []

    if correlation_id:
        tokens.append(attach(set_value(CORRELATION_ID_KEY, correlation_id)))
    if orchestration_id:
        tokens.append(attach(set_value(ORCHESTRATION_ID_KEY, orchestration_id)))
    if algorithm:
        tokens.append(attach(set_value(ALGORITHM_KEY, algorithm)))

    try:
        yield
    finally:
        for token in tokens:
            detach(token)


def traced(span_name: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None):
    """Decorator to trace function execution."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not MASSGEN_TRACE_ENABLED:
                return func(*args, **kwargs)

            tracer = get_tracer(func.__module__)
            name = span_name or f"{func.__module__}.{func.__name__}"

            with tracer.start_as_current_span(name) as span:
                # Add standard attributes
                span.set_attribute("code.function", func.__name__)
                span.set_attribute("code.namespace", func.__module__)

                # Add custom attributes
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)

                # Add context attributes
                from opentelemetry.context import get_value

                correlation_id = get_value(CORRELATION_ID_KEY)
                orchestration_id = get_value(ORCHESTRATION_ID_KEY)
                algorithm = get_value(ALGORITHM_KEY)

                if correlation_id:
                    span.set_attribute("massgen.correlation_id", correlation_id)
                if orchestration_id:
                    span.set_attribute("massgen.orchestration_id", orchestration_id)
                if algorithm:
                    span.set_attribute("massgen.algorithm", algorithm)

                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        return wrapper

    return decorator


def add_span_attributes(attributes: Dict[str, Any]):
    """Add attributes to the current span."""
    if not MASSGEN_TRACE_ENABLED:
        return

    span = trace.get_current_span()
    if span and span.is_recording():
        for key, value in attributes.items():
            if value is not None:
                # Convert non-string values to appropriate types
                if isinstance(value, (bool, int, float, str)):
                    span.set_attribute(key, value)
                elif isinstance(value, (list, tuple)):
                    # OpenTelemetry supports homogeneous arrays
                    if all(isinstance(v, bool) for v in value):
                        span.set_attribute(key, value)
                    elif all(isinstance(v, (int, float)) for v in value):
                        span.set_attribute(key, value)
                    elif all(isinstance(v, str) for v in value):
                        span.set_attribute(key, value)
                    else:
                        span.set_attribute(key, str(value))
                else:
                    span.set_attribute(key, str(value))


def record_error(error: Exception, attributes: Optional[Dict[str, Any]] = None):
    """Record an error in the current span."""
    if not MASSGEN_TRACE_ENABLED:
        return

    span = trace.get_current_span()
    if span and span.is_recording():
        span.record_exception(error, attributes=attributes)
        span.set_status(Status(StatusCode.ERROR, str(error)))


def create_child_span(name: str, attributes: Optional[Dict[str, Any]] = None) -> trace.Span:
    """Create a child span with the current span as parent."""
    tracer = get_tracer(__name__)
    span = tracer.start_span(name)

    if attributes:
        for key, value in attributes.items():
            span.set_attribute(key, value)

    return span


def propagate_context_to_headers() -> Dict[str, str]:
    """Extract trace context for propagation in HTTP headers."""
    headers = {}
    if MASSGEN_TRACE_ENABLED:
        inject(headers)
    return headers


def extract_context_from_headers(headers: Dict[str, str]):
    """Extract trace context from HTTP headers."""
    if MASSGEN_TRACE_ENABLED:
        context = extract(headers)
        return context
    return None
