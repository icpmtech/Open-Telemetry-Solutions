After Starting
Run:

bash
Copy
Edit
docker-compose up -d
Open:

Kibana: http://localhost:5601

Grafana: http://localhost:3000

User: admin

Pass: admin

In Kibana Dev Tools, paste the index template:

json
Copy
Edit
PUT _index_template/otel_template
{
  "index_patterns": ["otel-*"],
  "data_stream": {},
  "template": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0
    },
    "mappings": {
      "properties": {
        "@timestamp": { "type": "date" },
        "trace_id": { "type": "keyword" },
        "message": { "type": "text" }
      }
    }
  },
  "priority": 500,
  "_meta": {
    "description": "Template for OpenTelemetry indexes (traces, logs, etc.)"
  }
}
Now you can send otel-* data to Elasticsearch and visualize it directly in Grafana via the preconfigured datasource.