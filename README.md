This simple Flask-based application is created to demonstrate observability. It simulates real-world application behavior like successful requests, errors, and metrics exposure.
It is instrumented using the OpenTelemetry SDK to show spans to the OTEL Collector. 

It includes
- / – Serves a basic home page with a span named homepage.
- /fail – An endpoint that throws a simulated error.


Tracing:
- Uses the opentelemetry-sdk and opentelemetry-exporter-otlp packages.
- Sends traces over HTTP to the OTEL Collector.

Deployment:
- Comes with a Dockerfile for easy containerization.
- Can be run as a standalone docker compose wired to a self-hosted SigNoz stack.
