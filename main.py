# main.py
"""
Simple Flask app instrumented with OpenTelemetry
------------------------------------------------
* Traces are exported via OTLP/HTTP to an OTEL Collector
* Prometheus metrics are exposed at /metrics
"""

import os
from flask import Flask, render_template, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

# ── OpenTelemetry imports ────────────────────────────────────────────────────
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# ── OTEL setup ───────────────────────────────────────────────────────────────
OTEL_ENDPOINT = os.getenv(
    "OTEL_EXPORTER_OTLP_ENDPOINT",
    "http://localhost:4318",           # change if collector is elsewhere
).rstrip("/")

resource = Resource(attributes={"service.name": "simple-app"})
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(
    OTLPSpanExporter(
        endpoint=f"{OTEL_ENDPOINT}/v1/traces"   # http://.. implies insecure
    )
)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

# ── Flask + Prometheus metrics ───────────────────────────────────────────────
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

REQUESTS = Counter("demo_app_requests_total", "Total HTTP requests")
ERRORS   = Counter("demo_app_errors_total",   "Total error responses")

@app.route("/")
def home():
    REQUESTS.inc()
    with tracer.start_as_current_span("homepage"):
        return render_template("index.html")

@app.route("/work")
def work():
    REQUESTS.inc()
    with tracer.start_as_current_span("do_work"):
        return "Doing some work..."

@app.route("/fail")
def fail():
    REQUESTS.inc()
    ERRORS.inc()
    with tracer.start_as_current_span("forced_failure"):
        raise Exception("Intentional failure!")

@app.errorhandler(Exception)
def handle_exception(err):
    # Return a 500 response for demonstration
    return f"Error: {err}", 500

@app.route("/metrics")
def metrics():
    """Prometheus scrape endpoint."""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Default to port 8000 so docker-compose maps 8000:8000
    app.run(host="0.0.0.0", port=8000)