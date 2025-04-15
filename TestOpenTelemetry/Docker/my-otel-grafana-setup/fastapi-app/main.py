from fastapi import FastAPI, Request
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
import asyncio

# Explicit Swagger UI configuration along with application title and description.
app = FastAPI(
    title="FastAPI Tracing Service",
    description="Service demonstrating OpenTelemetry tracing with additional manual spans, custom context attributes, and Swagger UI.",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Middleware to add custom context to each request.
@app.middleware("http")
async def add_context_middleware(request: Request, call_next):
    # Proceed to get the response first.
    response = await call_next(request)
    # Get the current active span.
    current_span = trace.get_current_span()
    if current_span:
        # Add a custom attribute if the "x-request-id" header exists.
        request_id = request.headers.get("x-request-id")
        if request_id:
            current_span.set_attribute("request.id", request_id)
    return response

# Set up OpenTelemetry Tracing for the FastAPI service.
resource = Resource(attributes={SERVICE_NAME: "fastapi-service"})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

# Configure the OTLP HTTP exporter to send traces to the collector's endpoint.
otlp_exporter = OTLPSpanExporter(
    endpoint="http://otel-collector:4318/v1/traces"
)
span_processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(span_processor)

# Automatically instrument FastAPI routes.
FastAPIInstrumentor.instrument_app(app)

@app.get("/", tags=["General"], include_in_schema=True)
async def read_root():
    return {"message": "Hello from FastAPI"}

@app.get("/trigger", tags=["Tracing"], include_in_schema=True)
async def trigger_trace():
    # Create a manual span to demonstrate sending trace data.
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("manual-span"):
        return {"message": "Manual trace span sent to the collector"}

@app.get("/trigger-context", tags=["Tracing"], include_in_schema=True)
async def trigger_context():
    # Create a span and add custom context attributes.
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("manual-context-span") as span:
        # Adding manual custom context attributes.
        span.set_attribute("user.id", "12345")
        span.set_attribute("session.id", "abcde")
        span.set_attribute("custom.context", "example value")
        return {"message": "Manual trace span with custom context attributes sent"}

@app.get("/health", tags=["Health"], include_in_schema=True)
async def health_check():
    return {"status": "healthy"}
