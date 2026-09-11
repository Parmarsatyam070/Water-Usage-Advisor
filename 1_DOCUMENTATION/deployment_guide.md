# Smart Water Usage Advisor — Operations & Deployment Guide

**Project:** Smart Water Usage Advisor (UN Sustainable Development Goal 6: Clean Water & Sanitation)  
**Lifecycle Stage:** Phase 6 — Deployment, Documentation & Final Presentation  
**Document Version:** 1.0 (Production & Operations Manual)  

---

## 1. System Overview & Architecture

The Smart Water Usage Advisor is an AI-driven decision support system designed to optimize residential and municipal water consumption, detect pipeline leaks, forecast short-term demand, and provide grounded water conservation advice.

The deployment stack packages:
1. **Application Server (`web`):** Python Flask REST API served via Gunicorn WSGI process manager (multi-worker, multi-threaded) and hosting static frontend assets.
2. **Database Engine (`db`):** Authoritative PostgreSQL relational database engine with 12 normalized tables and persistent named volume storage.
3. **AI Component Facade:** Pre-trained Random Forest demand forecaster (`5_AI_COMPONENTS/predictive_models/models/forecasting_model.joblib`), 4-layer hybrid Isolation Forest anomaly detector (`5_AI_COMPONENTS/anomaly_detection/models/isolation_forest.joblib`), and grounded conversational RAG chatbot with curated municipal conservation knowledge.

---

## 2. System Prerequisites

### Local Development / Evaluation:
- **Operating System:** Linux (Ubuntu 20.04+), macOS (12+), or Windows 10/11 (with WSL2 or Docker Desktop).
- **Docker & Docker Compose:** Docker Engine 24.0+ and Docker Compose v2.20+.
- **Python (for host development/testing):** Python 3.10, 3.11, 3.12, 3.13, or 3.14.
- **System Memory:** Minimum 2 GB RAM (4 GB recommended for concurrent Docker execution).
- **Disk Space:** Minimum 2 GB free disk space for Docker images and volumes.

---

## 3. Environment Variables & Secret Configuration

The application follows twelve-factor application principles, injecting sensitive configuration exclusively at runtime via environment variables.

| Variable Name | Required? | Default Value (Dev/Test) | Description & Security Constraint |
| :--- | :---: | :--- | :--- |
| `ENVIRONMENT` | Yes | `development` | Runtime mode: `development`, `testing`, or `production`. In `production`, fail-closed validation is enforced. |
| `PORT` | No | `5000` | Port bound by application server / Gunicorn. |
| `SECRET_KEY` | Production | `dev-fallback-secret-water-advisor-2026` | Flask session and CSRF signature key. In production, must be an explicit, cryptographically random secret. |
| `JWT_SECRET_KEY` | Production | `dev-fallback-jwt-secret-water-advisor-2026` | Secret key for signing RFC 7519 HMAC-SHA256 tokens. In production, must be an explicit, cryptographically random secret. |
| `DATABASE_URL` | Yes | `postgresql://postgres:postgres@localhost:5432/smart_water_advisor_db` | Connection string for PostgreSQL database engine. |
| `DATABASE_ENGINE` | No | `postgresql` | Engine selector: `postgresql` (authoritative) or `sqlite` (testing fallback). |
| `CORS_ALLOWED_ORIGINS`| No | `http://localhost:5000,http://127.0.0.1:5000` | Comma-separated list of permitted CORS origins. Never use wildcards (`*`) in production. |
| `ENABLE_DEMO_TOKEN` | No | `false` | Development toggle for instant token generation. Automatically disabled in `production`. |
| `GUNICORN_WORKERS` | No | `2` | Number of worker processes allocated to Gunicorn. |
| `GUNICORN_THREADS` | No | `2` | Number of concurrent execution threads per Gunicorn worker. |
| `GUNICORN_TIMEOUT` | No | `60` | Worker timeout in seconds before restarting unresponsive process. |
| `GEMINI_API_KEY` | Optional | *(none)* | Google Gemini LLM API key. If omitted, the chatbot defaults to the deterministic grounded provider. |

### Generating Cryptographically Secure Secrets:
Before production deployment, generate cryptographically random 64-character hex strings:

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Generate JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 4. Local Deployment via Docker Compose (Primary Target)

Docker Compose provides a reproducible local multi-container environment with no runtime dependency on external CDNs or third-party application services.

### Step 1: Clone Repository & Enter Directory
```bash
git clone https://github.com/ParmarSatyam070/AI-Sustainability-internship.git
cd AI-Sustainability-internship
```

### Step 2: Configure Environment (Optional Override)
Copy `.env.example` to `.env` if custom ports or credentials are desired:
```bash
cp .env.example .env
```

### Step 3: Build & Launch Multi-Container Stack
```bash
docker compose -f 8_DEPLOYMENT/docker-compose.yml up --build -d
```

### Step 4: Verify Container Health & Status
```bash
docker compose -f 8_DEPLOYMENT/docker-compose.yml ps
```
Both `smart-water-db` and `smart-water-web` should display status `Up (healthy)`.

### Step 5: Access the Web Application
Open your browser and navigate to:
```text
http://localhost:5000/
```

### Step 6: Execute Deployment Smoke Test
```bash
python 8_DEPLOYMENT/verify_deployment.py --url http://localhost:5000
```

### Step 7: Teardown
```bash
# Stop containers while preserving database volume:
docker compose -f 8_DEPLOYMENT/docker-compose.yml down

# Stop containers and purge database volume:
docker compose -f 8_DEPLOYMENT/docker-compose.yml down -v
```

---

## 5. PostgreSQL Volume Initialization, Persistence & Backup

### Authoritative Schema Initialization:
- Schema location: `4_DEVELOPMENT/backend/database/init_schema.sql` (defining all 12 normalized tables).
- Mounted in Compose to `/docker-entrypoint-initdb.d/01_init_schema.sql:ro`.
- **Execution Condition:** The official PostgreSQL container image executes scripts in `/docker-entrypoint-initdb.d/` **ONLY when initializing a fresh, empty volume**.

### Volume Reuse & Persistence:
- All database state is stored in the persistent Docker named volume `pgdata`.
- On container restarts (`docker compose restart` or `docker compose down && docker compose up`), PostgreSQL detects the existing database cluster, skips initialization scripts, and preserves all user accounts, meter configurations, and telemetry data.

### Database Seeding:
To populate or reset sample personas and telemetry data:
```bash
# Execute seeding script inside the running web container
docker compose -f 8_DEPLOYMENT/docker-compose.yml exec web python 4_DEVELOPMENT/backend/database/seed_database.py
```

### Backup and Restore Procedures:
```bash
# Create an SQL dump backup:
docker compose -f 8_DEPLOYMENT/docker-compose.yml exec db pg_dump -U postgres smart_water_advisor_db > backup.sql

# Restore from an SQL dump:
cat backup.sql | docker compose -f 8_DEPLOYMENT/docker-compose.yml exec -T db psql -U postgres -d smart_water_advisor_db
```

---

## 6. Standalone Local Execution (Without Docker)

For evaluation on machines without Docker Desktop installed:

```bash
# 1. Activate Python virtual environment:
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 2. Run standalone production-style server:
python run_production_api.py --port 5000

# 3. Access in browser:
http://localhost:5000/
```

---

## 7. Cloud Deployment to Render.com (Public Target)

Render builds the application directly from the **same repository `8_DEPLOYMENT/Dockerfile`** used for local container verification.

```
GitHub repository
        ↓
Render Docker Web Service
        ↓
Build using the SAME 8_DEPLOYMENT/Dockerfile
        ↓
Run with Gunicorn
        ↓
Managed PostgreSQL
```

> [!NOTE]
> **Cloud Deployment Status**:
> Render deployment configuration is prepared and documented herein. Public cloud deployment has not been empirically verified, as no active public Render instance or public smoke test currently exists.

### Step-by-Step Render Deployment:

1. **Create Managed PostgreSQL on Render:**
   - Log into [Render Dashboard](https://dashboard.render.com/).
   - Click **New +** → **PostgreSQL**.
   - Set Name: `smart-water-db`.
   - Select Region (e.g. Frankfurt, Oregon, Singapore).
   - Select Free Tier.
   - Note the **Internal Database URL** (for web service connection).

2. **Initialize Schema on Render PostgreSQL:**
   - Connect via Render Web Shell or local `psql`:
     ```bash
     psql "<External Database URL>" < 4_DEVELOPMENT/backend/database/init_schema.sql
     ```
   - Seed sample telemetry records:
     ```bash
     DATABASE_URL="<External Database URL>" python 4_DEVELOPMENT/backend/database/seed_database.py
     ```

3. **Deploy Docker Web Service on Render:**
   - In Render Dashboard, click **New +** → **Web Service**.
   - Connect your GitHub repository: `ParmarSatyam070/AI-Sustainability-internship`.
   - Select Branch: `main`.
   - Select Runtime: **Docker**.
   - Specify Docker Command / Build context:
     - **Dockerfile Path:** `8_DEPLOYMENT/Dockerfile`
     - **Docker Build Context:** `.` (Repository root)
   - Instance Type: Free (512 MB RAM, 0.1 CPU).

4. **Configure Environment Variables in Render Dashboard:**
   Add the following environment variables under **Environment**:
   - `ENVIRONMENT` = `production`
   - `SECRET_KEY` = `<Generated 64-character hex key>`
   - `JWT_SECRET_KEY` = `<Generated 64-character hex key>`
   - `DATABASE_URL` = `<Internal Database URL from Step 1>`
   - `DATABASE_ENGINE` = `postgresql`
   - `CORS_ALLOWED_ORIGINS` = `https://<your-service-name>.onrender.com`
   - `GUNICORN_WORKERS` = `2`
   - `GUNICORN_THREADS` = `2`
   - `GUNICORN_TIMEOUT` = `60`
   - `ENABLE_DEMO_TOKEN` = `false`

5. **Deploy & Verify:**
   - Click **Create Web Service**.
   - Wait for Docker build and healthcheck to complete.
   - Run verification probe against the public HTTPS endpoint:
     ```bash
     python 8_DEPLOYMENT/verify_deployment.py --url https://<your-service-name>.onrender.com
     ```

---

## 8. Operational Troubleshooting & Diagnostics

### Symptom 1: Container Fails Startup with `ValueError: SECURITY ERROR`
- **Cause:** In `production` mode, `JWT_SECRET_KEY` or `SECRET_KEY` is missing or set to a default fallback.
- **Remedy:** Supply explicit 64-character random hex strings in the environment or `.env` file.

### Symptom 2: Web Container Exits with `Database connection timeout`
- **Cause:** Database container has not yet passed health checks or port 5432 is blocked.
- **Remedy:** Check `docker compose logs db` for PostgreSQL initialization errors. Ensure `depends_on: { db: { condition: service_healthy } }` is active in `docker-compose.yml`.

### Symptom 3: Port 5000 or 5432 Already in Use on Host
- **Cause:** Another process (e.g. local PostgreSQL or development server) is bound to the port.
- **Remedy:** Override ports via environment variables:
  ```bash
  WEB_PORT=5050 DB_PORT=5433 docker compose -f 8_DEPLOYMENT/docker-compose.yml up -d
  ```

### Symptom 4: Render Free Instance Cold Start Delay
- **Cause:** Free tier services spin down after 15 minutes of inactivity. First request takes ~50s to spin up container.
- **Remedy:** Normal behavior on free tier; subsequent requests respond within 50 ms.
