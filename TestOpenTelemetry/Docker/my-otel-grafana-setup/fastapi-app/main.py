from fastapi import FastAPI, Request
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

# --- LOGGING OTEL ---
import logging
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter

# Configurações da app FastAPI
app = FastAPI(
    title="FastAPI Tracing Service",
    description="Service demonstrating OpenTelemetry tracing with additional manual spans, custom context attributes, and Swagger UI.",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Middleware para adicionar contexto aos traces
@app.middleware("http")
async def add_context_middleware(request: Request, call_next):
    response = await call_next(request)
    current_span = trace.get_current_span()
    if current_span:
        request_id = request.headers.get("x-request-id")
        if request_id:
            current_span.set_attribute("request.id", request_id)
    return response

# Recursos OTEL (usados em tracing e logging)
resource = Resource(attributes={SERVICE_NAME: "fastapi-service"})

# --- TRACING OTEL ---
trace_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(trace_provider)

trace_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4318/v1/traces")
trace_processor = BatchSpanProcessor(trace_exporter)
trace_provider.add_span_processor(trace_processor)

# --- LOGGING OTEL ---
log_provider = LoggerProvider(resource=resource)
set_logger_provider(log_provider)

log_exporter = OTLPLogExporter(endpoint="http://otel-collector:4318/v1/logs")
log_processor = BatchLogRecordProcessor(log_exporter)
log_provider.add_log_record_processor(log_processor)

# Handler para enviar logs do Python via OTEL
otel_handler = LoggingHandler(level=logging.INFO, logger_provider=log_provider)
logging.getLogger().addHandler(otel_handler)
logging.getLogger().setLevel(logging.INFO)  # Importante!

# Instrumentação automática do FastAPI
FastAPIInstrumentor.instrument_app(app)

# Logger para a aplicação
logger = logging.getLogger("fastapi-app")

@app.get("/", tags=["General"], include_in_schema=True)
async def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Hello from FastAPI"}

@app.get("/trigger", tags=["Tracing"], include_in_schema=True)
async def trigger_trace():
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("manual-span"):
        logger.info("Triggered manual span")
        return {"message": "Manual trace span sent to the collector"}

@app.get("/trigger-context", tags=["Tracing"], include_in_schema=True)
async def trigger_context():
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("manual-context-span") as span:
        span.set_attribute("user.id", "12345")
        span.set_attribute("session.id", "abcde")
        span.set_attribute("custom.context", "example value")
        logger.warning("Manual span with custom context triggered")
        return {"message": "Manual trace span with custom context attributes sent"}

@app.get("/health", tags=["Health"], include_in_schema=True)
async def health_check(request: Request):
    span = trace.get_current_span()
    # Extrair trace_id se existir (para correlação)
    trace_id = span.get_span_context().trace_id
    trace_id_hex = format(trace_id, '032x') if trace_id else None

    logger.info("Health check accessed", extra={
        "endpoint": "/health",
        "method": request.method,
        "trace_id": trace_id_hex,
        "path": request.url.path,
        "remote_ip": request.client.host
    })

    return {"status": "healthy"}
