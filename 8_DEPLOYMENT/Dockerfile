FROM python:3.11-slim

WORKDIR /app

# Ensure Python doesn't buffer stdout/stderr or write bytecode
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install curl for container health check probe
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies using deployment requirements
COPY requirements.txt ./
COPY 8_DEPLOYMENT/requirements-deploy.txt ./8_DEPLOYMENT/
RUN pip install --no-cache-dir -r 8_DEPLOYMENT/requirements-deploy.txt

# Copy application source code
COPY . /app/

# Configure non-root security context
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/sh appuser && \
    chown -R appuser:appgroup /app

USER appuser

EXPOSE 5000

# Automated container healthcheck against Flask health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Launch production Gunicorn WSGI process
CMD ["gunicorn", "--config", "8_DEPLOYMENT/gunicorn.conf.py", "8_DEPLOYMENT.wsgi:app"]
