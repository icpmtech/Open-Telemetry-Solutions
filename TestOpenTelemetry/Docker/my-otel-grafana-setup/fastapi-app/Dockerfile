FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    opentelemetry-api \
    opentelemetry-sdk \
    opentelemetry-exporter-otlp \
    opentelemetry-instrumentation-fastapi \
    prometheus-client

COPY . .

# Expose ports for application and Prometheus metrics
EXPOSE 8000 8001

# Set OTLP exporter endpoint environment variable
ENV OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318

# Run the app with OpenTelemetry instrumentation
CMD ["opentelemetry-instrument", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]