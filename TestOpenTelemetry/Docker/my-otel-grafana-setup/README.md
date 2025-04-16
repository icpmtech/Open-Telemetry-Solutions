
# 📊 Observability Stack with OpenTelemetry, Prometheus, Elasticsearch & Grafana (Docker)

This project sets up a full **observability pipeline** using Docker Compose, including:

- **OpenTelemetry Collector** – Receives and exports telemetry data (metrics/logs)
- **Prometheus** – Scrapes and stores application metrics
- **Elasticsearch** – Stores structured logs and traces
- **Grafana** – Visualizes both metrics and logs through prebuilt dashboards
- **Kibana** – UI to query and inspect logs in Elasticsearch

---

## 📁 Project Structure

```
my-otel-grafana-setup/
├── docker-compose.yml
├── otel-collector-config.yaml
├── prometheus.yml
├── elastic_templates/
│   └── otel_template.json
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       │   ├── datasource.yml
│       │   └── elasticsearch.yml
│       └── dashboards/
│           ├── dashboard.yaml
│           └── json/
│               └── otel-dashboard.json
├── infra/
│   ├── image.png
│   ├── main.bicep
│   └── parameters.json
├── manual-operations/
│   └── configure-elastic.md
└── fastapi-app/   # Optional instrumented app
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone <repo-url>
cd my-otel-grafana-setup
```

### 2. Launch the Stack

```bash
docker-compose up -d
```

This will start the following services:

| Component                | Port                    |
|-------------------------|-------------------------|
| OpenTelemetry Collector | 4317 (gRPC), 4318 (HTTP)|
| Prometheus              | 9090                    |
| Elasticsearch           | 9200                    |
| Kibana                  | 5601                    |
| Grafana                 | 3000                    |

---

## 🛠️ Key Configuration Files

- `otel-collector-config.yaml`: OpenTelemetry Collector pipeline configuration
- `prometheus.yml`: Prometheus scrape job setup
- `elastic_templates/otel_template.json`: Index template for `otel-*` indices (logs/traces)
- `grafana/provisioning/datasources/`: Auto-adds Prometheus and Elasticsearch as data sources
- `grafana/provisioning/dashboards/`: Auto-loads dashboard showing log streams and metrics over time

---

## 📥 Sending Telemetry

Send OpenTelemetry data using any instrumented app or tools like [`otel-cli`](https://github.com/equinix-labs/otel-cli).

### Metrics

- HTTP: `http://localhost:4318/v1/metrics`
- gRPC: `grpc://localhost:4317`

### Logs (via OTLP exporter)

Ensure your app sends logs with the required fields: `@timestamp`, `trace_id`, `message`, etc.

---

## 🖥️ Access the Interfaces

- **Grafana**: [http://localhost:3000](http://localhost:3000)  
  - Login: `admin / admin`
- **Kibana**: [http://localhost:5601](http://localhost:5601)  
  - Use **Dev Tools** to apply `otel_template.json`
- **Prometheus**: [http://localhost:9090](http://localhost:9090)

---

## 📊 Preloaded Grafana Dashboard

Grafana auto-loads a dashboard that includes:

- **Log Stream**: Live view of logs from `otel-*` indices
- **Time Series Panel**: Visualize log volume over time

📂 Find it under: **Folder:** `otel` → **Dashboard:** `OpenTelemetry Logs`

---

## ⚠️ Port Conflicts (Optional)

If you see an error like:

```
Ports are not available: exposing port TCP 0.0.0.0:55679
```

Do one of the following:

- Remove the line from `docker-compose.yml`:
  ```yaml
  - "55679:55679"
  ```
- Or change to a free port:
  ```yaml
  - "55678:55679"
  ```

Then restart:

```bash
docker-compose down
docker-compose up -d
```

---

## 🧱 Build More Dashboards in Grafana

Use **Dashboards > New** to explore and visualize:

- Request rates
- Error counts
- OpenTelemetry logs with filters
- Combined metrics & logs views

---

## 📦 Extending the Stack

- Add **Jaeger** for trace visualization
- Use **Loki** as an alternative log backend
- Deploy to the cloud using `infra/` Bicep templates

---

## 📬 Feedback & Contributions

Feel free to open issues or pull requests with suggestions or improvements.

---

## 📄 License

MIT
```

---

Let me know if you'd like a version:

- 📎 Converted to **HTML** or **PDF**
- 📈 With **trace dashboards** included in Grafana
- 🛠️ Tailored for a specific cloud environment (e.g., Azure, AWS)

