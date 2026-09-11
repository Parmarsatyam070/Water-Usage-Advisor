"""
Gunicorn Production Server Configuration
Phase 6 - Deployment & Serving Layer

Configures the WSGI server for multi-worker, multi-threaded execution within Linux
containers (Docker, Render, Cloud Run) with sensible defaults and environment overrides.
"""

import os

# Server socket
port = os.getenv("PORT", "5000")
bind = os.getenv("GUNICORN_BIND", f"0.0.0.0:{port}")

# Worker processes & concurrency
# 2 workers x 2 threads provides concurrency while keeping memory profile constrained for ML models
workers = int(os.getenv("GUNICORN_WORKERS", "2"))
threads = int(os.getenv("GUNICORN_THREADS", "2"))
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "gthread")

# Timeouts & Keepalive
timeout = int(os.getenv("GUNICORN_TIMEOUT", "60"))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", "5"))
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", "30"))

# Logging to stdout / stderr for container log aggregators
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
accesslog = "-"
errorlog = "-"

# Preload disabled to ensure separate model handle per worker and graceful worker recycling
preload_app = False
