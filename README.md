```markdown
# 📊 Observability Stack with OpenTelemetry, Prometheus, Grafana & FastAPI (Docker)

This project sets up a complete observability pipeline using Docker Compose, including:

- **OpenTelemetry Collector** – Receives and processes telemetry data (both metrics and traces)
- **Prometheus** – Scrapes and stores metrics data
- **Grafana** – Visualizes the metrics with dashboards
- **FastAPI Application** – An instrumented web application that sends trace data to the Collector

For additional examples and extended OpenTelemetry solutions, check out the [Open-Telemetry-Solutions](https://github.com/icpmtech/Open-Telemetry-Solutions) repository.

---

## 📁 Project Structure

```
my-otel-grafana-setup/
├── docker-compose.yml
├── otel-collector-config.yaml
├── prometheus.yml
├── grafana/
│   └── provisioning/
│       └── datasources/
│           └── datasource.yml
└── fastapi-app/
    ├── Dockerfile
    ├── requirements.txt
    └── main.py
```

- **docker-compose.yml:** Defines all four services (Collector, Prometheus, Grafana, FastAPI).
- **otel-collector-config.yaml:** Configures the Collector to receive OTLP telemetry and export both metrics and traces.
- **prometheus.yml:** Configures Prometheus to scrape metrics from the Collector.
- **grafana/provisioning/datasources/datasource.yml:** Automatically provisions Grafana with Prometheus as the default datasource.
- **fastapi-app/**: Contains the FastAPI application that sends trace data to the Collector.

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone <repo-url>
cd my-otel-grafana-setup
```

### 2. Run Docker Compose

Start all services by executing:

```bash
docker-compose up -d
```

This command will launch:
- **OpenTelemetry Collector** on ports 4317 (gRPC) and 4318 (HTTP)
- **Prometheus** on port 9090
- **Grafana** on port 3000
- **FastAPI Application** on port 8000

---

## 🛠️ Configuration Files

### docker-compose.yml

```yaml
version: '3.8'
services:
  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    volumes:
      - ./otel-collector-config.yaml:/etc/otelcol-contrib/config.yaml
    ports:
      - "1888:1888"   # pprof for performance profiling
      - "4317:4317"   # OTLP gRPC receiver
      - "4318:4318"   # OTLP HTTP receiver
      - "8890:8890"   # Prometheus metrics exported by the Collector
      - "8889:8889"   # Prometheus exporter metrics (if needed)
      - "13133:13133" # Health check endpoint

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    volumes:
      - ./grafana/provisioning:/etc/grafana/provisioning
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    ports:
      - "3000:3000"

  fastapi-app:
    build: ./fastapi-app
    ports:
      - "8000:8000"
    environment:
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318/v1/traces
    depends_on:
      - otel-collector
```

### otel-collector-config.yaml

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: "0.0.0.0:4317"
      http:
        endpoint: "0.0.0.0:4318"

exporters:
  prometheus:
    endpoint: "0.0.0.0:8890"
  debug: {}  # Sends trace data to Collector logs for debugging

service:
  pipelines:
    metrics:
      receivers: [otlp]
      exporters: [prometheus]
    traces:
      receivers: [otlp]
      exporters: [debug]
```

### prometheus.yml

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'otel-collector'
    static_configs:
      - targets: ['otel-collector:8890']
```

### grafana/provisioning/datasources/datasource.yml

```yaml
apiVersion: 1
datasources:
- name: Prometheus
  type: prometheus
  access: proxy
  url: http://prometheus:9090
  isDefault: true
  editable: false
```

---

## 🚀 FastAPI Application

### fastapi-app/Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### fastapi-app/requirements.txt

```plaintext
fastapi
uvicorn
opentelemetry-api
opentelemetry-sdk
opentelemetry-exporter-otlp-proto-http
opentelemetry-instrumentation-fastapi
```

### fastapi-app/main.py

```python
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

app = FastAPI()

# Configure OpenTelemetry for FastAPI
resource = Resource(attributes={SERVICE_NAME: "fastapi-service"})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

# Configure the OTLP exporter to send traces to the Collector.
otlp_exporter = OTLPSpanExporter(
    endpoint="http://otel-collector:4318/v1/traces"
)
span_processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(span_processor)

# Instrument FastAPI routes automatically
FastAPIInstrumentor.instrument_app(app)

@app.get("/")
async def read_root():
    return {"message": "Hello from FastAPI"}

@app.get("/trigger")
async def trigger_trace():
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("manual-span"):
        return {"message": "Manual trace span sent to the collector"}
```

---

## 🖥️ Access the Interfaces

- **Grafana**: [http://localhost:3000](http://localhost:3000)  
  _Login: `admin / admin`_
- **Prometheus**: [http://localhost:9090](http://localhost:9090)
- **FastAPI Application**: [http://localhost:8000](http://localhost:8000)  
  - The `/` endpoint returns a welcome message.
  - The `/trigger` endpoint generates a manual trace.

---

## 📡 Sending Telemetry

Your instrumented FastAPI app sends trace data to the Collector at:
- `http://otel-collector:4318/v1/traces` (from within Docker networks)

From outside Docker, you can test using:
- `http://localhost:4318/v1/traces` (if port 4318 is mapped externally)

For metrics, send to:
- `http://localhost:4318/v1/metrics` (HTTP) or  
- `grpc://localhost:4317` (gRPC)

You can also utilize tools like [otel-cli](https://github.com/equinix-labs/otel-cli) to send sample telemetry.

---

## ⚠️ Port 55679 Error Fix (zPages)

If you encounter this error:

```
Ports are not available: exposing port TCP 0.0.0.0:55679
```

### Solutions:
- **Option 1**: Remove the port mapping for 55679 from your `docker-compose.yml` if you’re not using zPages.
- **Option 2**: Change it to a free port, for example:
  ```yaml
  - "55678:55679"
  ```
Then restart your services:

```bash
docker-compose down
docker-compose up -d
```

---

## 🧱 Build Dashboards in Grafana

Once your metrics are coming in:
1. Log into Grafana at [http://localhost:3000](http://localhost:3000).
2. Create new dashboards to visualize key metrics such as:
   - Request rates
   - Custom app metrics
   - Error counts
   - And more!

---

## 📚 Additional Resources

Explore more OpenTelemetry and observability solutions in the [Open-Telemetry-Solutions](https://github.com/icpmtech/Open-Telemetry-Solutions) repository.

---

## 📬 Feedback & Contributions

Have ideas or improvements? Open an issue or submit a pull request! Contributions are welcome.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

By integrating a FastAPI application into this observability stack and leveraging additional resources from the Open-Telemetry-Solutions repository, you now have a complete end-to-end solution for monitoring both application performance and infrastructure metrics. Happy monitoring!
```