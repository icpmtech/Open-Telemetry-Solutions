from fastapi import FastAPI, Request
import time
import logging
from opentelemetry import trace, metrics
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

# Tracing imports
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

# Logging imports
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter

# Metrics imports
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

# ----------------------------------------
# Configuration
# ----------------------------------------
ORG_NAME = "XPTO Corp"  # Organization name for context

# FastAPI app + Swagger/OpenAPI config
app = FastAPI(
    title="FastAPI Observability Service",
    description=(
        "OpenTelemetry Tracing, Metrics & Logging with organization context\n"
        "Exports OTLP to collector for shipping into Elasticsearch"
    ),
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Shared OTEL Resource including org name
resource = Resource(attributes={
    SERVICE_NAME: "fastapi-service",
    "organization.name": ORG_NAME
})

# ----------------------------------------
# TRACING Setup
# ----------------------------------------
trace_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(trace_provider)
span_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4318/v1/traces")
span_processor = BatchSpanProcessor(span_exporter)
trace_provider.add_span_processor(span_processor)

# ----------------------------------------
# LOGGING Setup
# ----------------------------------------
log_provider = LoggerProvider(resource=resource)
set_logger_provider(log_provider)
log_exporter = OTLPLogExporter(endpoint="http://otel-collector:4318/v1/logs")
log_processor = BatchLogRecordProcessor(log_exporter)
log_provider.add_log_record_processor(log_processor)
otel_handler = LoggingHandler(level=logging.INFO, logger_provider=log_provider)
root_logger = logging.getLogger()
root_logger.addHandler(otel_handler)
root_logger.setLevel(logging.INFO)
logger = logging.getLogger("fastapi-app")

# ----------------------------------------
# METRICS Setup
# ----------------------------------------
metric_exporter = OTLPMetricExporter(endpoint="http://otel-collector:4318/v1/metrics")
metric_reader = PeriodicExportingMetricReader(metric_exporter, export_interval_millis=60000)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
meter = meter_provider.get_meter("fastapi-metrics")
request_counter = meter.create_counter(
    name="http.server.request.count",
    description="Number of HTTP requests",
    unit="1",
)
request_latency = meter.create_histogram(
    name="http.server.request.duration",
    description="HTTP request latency",
    unit="ms",
)

# Auto‑instrument FastAPI for tracing
FastAPIInstrumentor.instrument_app(app)

# Combined Middleware: Metrics + Trace Context + Structured Logging
@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    start_ns = time.time_ns()
    response = await call_next(request)
    end_ns = time.time_ns()
    latency_ms = (end_ns - start_ns) / 1e6

    # === Trace Context Attribute ===
    span = trace.get_current_span()
    if span and span.is_recording():
        if request.headers.get("x-request-id"):
            span.set_attribute("request.id", request.headers["x-request-id"])

    # === Metrics Attributes ===
    attrs = {
        "service.name": "fastapi-service",
        "organization.name": ORG_NAME,
        "http.method": request.method,
        "http.route": request.url.path,
        "http.status_code": response.status_code,
    }
    request_counter.add(1, attributes=attrs)
    request_latency.record(latency_ms, attributes=attrs)

    # === Structured Logging ===
    trace_id = None
    if span:
        ctx = span.get_span_context()
        if ctx.trace_id:
            trace_id = format(ctx.trace_id, "032x")
    # Ensure trace_id is a string, not None
    log_attrs = {
        **attrs,
        "trace_id": trace_id or "",
        "duration_ms": round(latency_ms, 2),
        "remote_ip": request.client.host,
    }
    logger.info("HTTP request completed", extra=log_attrs)

    return response

# Endpoints
@app.get("/", tags=["General"])
async def read_root(request: Request):
    logger.info(
        "Root endpoint accessed",
        extra={"endpoint": "/", "http.method": request.method, "organization.name": ORG_NAME}
    )
    return {"message": "Hello from FastAPI"}

@app.get("/trigger", tags=["Tracing"])
async def trigger_trace(request: Request):
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("manual-span") as span:
        logger.info(
            "Triggered manual span",
            extra={"endpoint": "/trigger", "organization.name": ORG_NAME}
        )
        return {"message": "Manual trace span sent to the collector"}

@app.get("/trigger-context", tags=["Tracing"])
async def trigger_context(request: Request):
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("manual-context-span") as span:
        span.set_attribute("user.id", "12345")
        span.set_attribute("session.id", "abcde")
        logger.info(
            "Manual span with custom context triggered",
            extra={"endpoint": "/trigger-context", "organization.name": ORG_NAME}
        )
        return {"message": "Manual trace span with custom context attributes sent"}

@app.get("/health", tags=["Health"])
async def health_check(request: Request):
    logger.info(
        "Health check accessed",
        extra={"endpoint": "/health", "organization.name": ORG_NAME}
    )
    return {"status": "healthy"}
