
# 📊 Observability Stack with OpenTelemetry, Prometheus & Grafana (Docker)

This project sets up a complete observability pipeline using Docker Compose, including:

- **OpenTelemetry Collector** – Receives and processes telemetry data
- **Prometheus** – Scrapes and stores metrics
- **Grafana** – Visualizes the metrics with dashboards

---

## 📁 Project Structure

```
my-otel-grafana-setup/
├── docker-compose.yml
├── otel-collector-config.yaml
├── prometheus.yml
└── grafana/
    └── provisioning/
        └── datasources/
            └── datasource.yml
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone <repo-url>
cd my-otel-grafana-setup
```

### 2. Run Docker Compose

```bash
docker-compose up -d
```

This will start:
- OpenTelemetry Collector on ports 4317 (gRPC) and 4318 (HTTP)
- Prometheus on port 9090
- Grafana on port 3000

---

## 🛠️ Configuration Files

### `otel-collector-config.yaml`

Configures OpenTelemetry Collector to receive OTLP metrics and expose them to Prometheus.

### `prometheus.yml`

Tells Prometheus to scrape metrics from the OpenTelemetry Collector on port `8888`.

### `grafana/provisioning/datasources/datasource.yml`

Automatically provisions Prometheus as a data source in Grafana.

---

## 🖥️ Access the Interfaces

- **Grafana**: [http://localhost:3000](http://localhost:3000)  
  Login: `admin / admin`
- **Prometheus**: [http://localhost:9090](http://localhost:9090)

---

## 📡 Sending Telemetry

Send metrics to the OTLP Collector:
- `http://localhost:4318/v1/metrics` (HTTP)
- `grpc://localhost:4317` (gRPC)

Use your instrumented app or tools like [`otel-cli`](https://github.com/equinix-labs/otel-cli).

---

## ⚠️ Port 55679 Error Fix (zPages)

If you encounter this error:

```
Ports are not available: exposing port TCP 0.0.0.0:55679
```

### Solutions:

- **Option 1**: Remove this line from `docker-compose.yml` if you're not using zPages:
  ```yaml
  - "55679:55679"
  ```

- **Option 2**: Change to a free port, e.g.:
  ```yaml
  - "55678:55679"
  ```

Then restart:

```bash
docker-compose down
docker-compose up -d
```

---

## 🧱 Build Dashboards in Grafana

Once your metrics are coming in, go to **Dashboards > New** in Grafana to start visualizing:

- Request rates
- Custom app metrics
- Error counts
- ...and more!

---

## 📬 Feedback & Contributions

Feel free to open issues or pull requests if you improve the stack or have ideas!

---

## 📄 License

MIT
