# Phase 6 Implementation Plan: Deployment, Documentation & Final Presentation

**Project:** Smart Water Usage Advisor (UN Sustainable Development Goal 6: Clean Water & Sanitation)  
**Lifecycle Stage:** Phase 6 — Deployment, Documentation & Final Presentation (Weeks 11–12)  
**Document Version:** 4.0 (Master Planning Document — Final Corrected Baseline)  
**Status:** PLANNING ONLY — PENDING USER APPROVAL  

---

## 1. Executive Summary

Phase 6 represents the **final lifecycle stage** of the Smart Water Usage Advisor project. Having successfully designed, validated, and integrated all core analytical subsystems (Phase 1 research, Phase 2 data and database schema, Phase 3A predictive forecasting, Phase 3B anomaly and leak detection, Phase 3C conversational RAG chatbot, Phase 4 interactive web UI, and Phase 5 REST API with JWT security and Responsible AI governance), Phase 6 transitions the system into a **reproducible, production-style deployment package and final project deliverable**.

### Primary Objectives of Phase 6:
1. **Production Containerization & Process Serving:** Package the integrated application using Docker, Docker Compose, and Gunicorn WSGI process management with non-root security and a reproducible local multi-container environment with no runtime dependency on external CDNs or third-party application services.
2. **Authoritative PostgreSQL Deployment:** Deploy containerized PostgreSQL reusing the existing authoritative 12-table schema (`4_DEVELOPMENT/backend/database/init_schema.sql`), persistent storage volumes, automated readiness probes, and isolated networking.
3. **Clean Dependency Separation:** Isolate Linux-only deployment dependencies (Gunicorn) in a dedicated deployment requirements file (`8_DEPLOYMENT/requirements-deploy.txt`), preserving a clean Windows development environment in root `requirements.txt`.
4. **Fail-Closed Security & Secrets Management:** Strictly distinguish build-time from runtime secrets; enforce fail-closed configuration in production; maintain BOLA/IDOR protection; verify zero secret leakage in image layers and container logs.
5. **Comprehensive Verification & Regression Testing:** Preserve passing status across all **130 currently verified tests (84 upstream baseline regression tests plus 46 Phase 5 integration/security/governance tests)**, and introduce new deployment smoke tests. The final Phase 6 test count will be measured empirically after implementation.
6. **Separated Local & Public Deployment Targets:** Validate the stack locally via Docker Compose (reproducible local multi-container environment with no runtime dependency on external CDNs or third-party application services), followed by public cloud deployment on Render.com (Docker Web Service + Managed PostgreSQL built from the same repository Dockerfile).
7. **Technical & Operational Documentation:** Deliver a complete operational deployment guide, REST API OpenAPI specifications, and a final capstone academic project report in `1_DOCUMENTATION/`.
8. **Academic Presentation & Demonstration Materials:** Produce a professional slide deck script, executive summary, and an 11-step interactive demonstration script in `9_PRESENTATION/` for evaluation committees.
9. **Clean Final Release Packaging:** Package clean, reproducible project deliverables with zero uncommitted junk, zero exposed secrets, and complete licensing compliance.

---

## 2. Current Project State & Empirical Baseline

The repository has been inspected and verified against the active working tree:

### Verified Subsystem Status (Phases 1–5):
- **10-Folder Canonical Structure:** All 10 canonical directories (`1_DOCUMENTATION` through `10_APPENDICES`) exist in the project root.
- **Phase 2 (Data & Database):** Authoritative PostgreSQL schema with 12 normalized tables defined in `4_DEVELOPMENT/backend/database/init_schema.sql`; 6,480 hourly synthetic telemetry records (90 days across 3 distinct consumer personas: Single-Family, Multi-Family, Commercial) in `4_DEVELOPMENT/data/generated/water_usage_data.csv`; automated database initialization (`init_database.py`) and seeding (`seed_database.py`).
- **Phase 3A (Predictive Demand Forecaster):** Global Random Forest Regressor serialized at `5_AI_COMPONENTS/predictive_models/models/forecasting_model.joblib`; official Seasonal Naive 7-day benchmark achieving MAPE = 9.85%; validated forecast uncertainty bounds derived from validation residual quantiles; zero future target leakage.
- **Phase 3B (Anomaly & Leak Detector):** 4-layer hybrid detection engine (Diurnal MAD baselines, Scale-Normalized Isolation Forest at `5_AI_COMPONENTS/anomaly_detection/models/isolation_forest.joblib`, domain physical leak rules, severity arbitration); verified 100% empirical leak recall on synthetic test sets without using ground-truth labels as input features.
- **Phase 3C (AI Water Conservation Chatbot):** Evidence-grounded conversational decision support engine combining telemetry context, 3A forecast, 3B anomalies, and 16 curated knowledge entries; decoupled `DeterministicGroundedProvider` (reproducible, local) and optional `GeminiLLMProvider`; safety filters for prompt injection, secret scrubbing, and licensed plumber referral disclaimers.
- **Phase 4 (Dashboard & Web UI):** Responsive single-page dashboard in vanilla HTML5/CSS3/ES6 JavaScript; local vendored Chart.js v4.4.1 UMD bundle (`4_DEVELOPMENT/frontend/js/vendor/chart.umd.js`) with no external runtime CDN dependency; multi-persona switcher (Sarah Jenkins, Marcus Vance, Elena Rostova).
- **Phase 5 (System Integration & Responsible AI):** Application factory pattern (`backend.app:create_app()`); 7 modular Blueprints (`/api/auth`, `/api/dashboard`, `/api/v1/telemetry`, `/api/v1/forecast`, `/api/v1/anomalies`, `/api/v1/chat`, `/api/health`); RFC 7519 standard JWT authentication and bcrypt password hashing; `@meter_access_required` BOLA/IDOR protection; 4 Responsible AI governance documents in `7_ETHICS_COMPLIANCE/` (Audit report, dual Mitchell et al. model cards, Gebru et al. telemetry datasheet).
- **Automated Test Baseline:**
  ```text
  130 currently verified tests consist of:
    84 upstream baseline regression tests
  + 46 Phase 5 integration/security/governance tests
  = 130 currently verified tests.
  ```
  All 130 currently verified tests pass with 100% success rate in 13.84s. Zero regressions.
- **Empirical Performance Benchmark (20 Concurrent Requests):** Measured throughput of **119.5 requests/second**, **0.0% error rate** (acceptance target $\le 5.0\%$ passed), median concurrent latency of **52.74 ms**, and p95 concurrent latency of **142.76 ms**.
- **Git State:** Branch `main` is clean, tracked by `origin/main` at commit `cb1e436`.

---

## 3. Phase 5 → Phase 6 Transition & Scope Boundaries

| Dimension | Phase 5 (Current Integrated System) | Phase 6 (Target Deployment & Release Package) |
| :--- | :--- | :--- |
| **Serving Process** | Python `app.run()` development server on port 5000 | Production **Gunicorn WSGI** process manager with configurable worker concurrency |
| **Packaging** | Local virtual environment (`.venv`) | Reproducible **Docker container** (`python:3.11-slim`) with non-root execution |
| **Multi-Service Orchestration** | Manual / script execution | **Docker Compose** orchestrating Flask/Gunicorn + PostgreSQL with health checks |
| **Database Execution** | Local PostgreSQL with SQLite/in-memory cache fallback | Authoritative containerized **PostgreSQL** with persistent named volume storage |
| **Documentation** | Phased walkthroughs & technical decision records | Consolidated **Deployment Guide**, **API Reference (OpenAPI)**, & **Final Project Report** |
| **Presentation** | Raw technical notes and test logs | Formal **Presentation Slides**, **Executive Summary**, & **Live Demonstration Script** |
| **Release Deliverables** | Untracked development artifacts | Clean, packaged repository archive with comprehensive license and setup docs |

### Strict Preservation Rules During Transition:
- **Zero AI Model Retraining:** Model weights (`forecasting_model.joblib`, `isolation_forest.joblib`) remain 100% frozen.
- **Zero Schema Alterations:** The authoritative 12-table schema (`4_DEVELOPMENT/backend/database/init_schema.sql`) remains untouched.
- **Zero Frontend Refactoring:** Vanilla HTML/CSS/JS frontend files remain unchanged.
- **Zero Test Degradation:** All 130 currently verified tests must continue to pass without alteration.
- **README Status Rule:** Update README roadmap to "Phase 6 Active" during implementation. Mark "Phase 6 Complete" only after all Phase 6 acceptance criteria, deployment verification, final testing, documentation, and presentation deliverables have actually been completed.
- **Phase Boundary:** Phase 6 is the final project phase. There is **no Phase 7**.

---

## 4. Deployment Architecture

The deployment architecture employs an isolated, containerized stack designed for consistency, academic reproducibility, and low operational overhead:

```
                                  Client Layer
      [ Browser Client (Desktop/Mobile) / Evaluation Committee / Testing Harness ]
                                       │
                                       │ HTTP / HTTPS (Port 5000)
                                       ▼
                        Docker Container: web (Flask + Gunicorn)
       ┌────────────────────────────────────────────────────────────────────────┐
       │ Gunicorn WSGI Server (Configurable Workers & Threads)                  │
       │   │                                                                    │
       │   ▼                                                                    │
       │ Authoritative WSGI Entry Point: 8_DEPLOYMENT/wsgi.py                   │
       │   │                                                                    │
       │   ▼                                                                    │
       │ Flask Application Factory (backend.app:create_app)                     │
       │   │                                                                    │
       │   ├─ Static Asset Host: / ──> Serves 4_DEVELOPMENT/frontend/           │
       │   │                           (index.html, styles.css, app.js,         │
       │   │                            locally vendored Chart.js v4.4.1)       │
       │   │                                                                    │
       │   ├─ Middleware & Security Layer                                       │
       │   │  ├─ JSON Error Handlers (400, 401, 403, 404, 405, 500, 503)       │
       │   │  ├─ @auth_required (RFC 7519 HMAC-SHA256 JWT validation)          │
       │   │  └─ @meter_access_required (BOLA/IDOR Object Isolation)           │
       │   │                                                                    │
       │   └─ 7 Modular API Blueprints:                                         │
       │      ├─ /api/auth          (POST /login, GET /me, GET /demo-token)    │
       │      ├─ /api/dashboard     (summary, consumption, forecast, etc.)      │
       │      ├─ /api/v1/telemetry  (readings, daily summaries)                 │
       │      ├─ /api/v1/forecast   (7-day multi-step + uncertainty bounds)     │
       │      ├─ /api/v1/anomalies  (incidents, anomaly scores)                 │
       │      ├─ /api/v1/chat       (RAG grounded advisor + safety guardrails)  │
       │      └─ /api/health        (operational telemetry, component health)   │
       │                                                                        │
       │   ▼                                                                    │
       │ Service Layer & AI Facade                                              │
       │   ├─ AuthService (Bcrypt & PyJWT)                                      │
       │   ├─ DashboardDataService (DTO Aggregation & Cache Degradation)        │
       │   └─ ml_models Facade:                                                 │
       │      ├─ Phase 3A Forecaster (Loaded from predictive_models/models/)    │
       │      ├─ Phase 3B Detector (Loaded from anomaly_detection/models/)      │
       │      └─ Phase 3C Chatbot (Loaded from chatbot/ + KB)                   │
       └───────────────────────────────┬────────────────────────────────────────┘
                                       │
                                       │ Internal TCP (Port 5432)
                                       │ (Isolated Bridge Network: water_net)
                                       ▼
                       Docker Container: db (PostgreSQL)
       ┌────────────────────────────────────────────────────────────────────────┐
       │ PostgreSQL Engine                                                      │
       │   ├─ Database: smart_water_advisor_db                                  │
       │   ├─ Schema: 12 Authoritative Tables (4_DEVELOPMENT/backend/database/  │
       │   │                                   init_schema.sql)                 │
       │   ├─ Seed Data: 3 Personas, 3 Meters, 6,480 Telemetry Readings         │
       │   └─ Persistent Storage: Named Volume (pgdata)                         │
       └────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Deployment Target Evaluation & Clarified Render Deployment Model

### Comparative Evaluation of Deployment Targets:

| Target Option | Architecture & Services | Advantages | Limitations & Operational Details | Evaluation & Role |
| :--- | :--- | :--- | :--- | :---: |
| **Option 1: Local Docker Compose** | Multi-container Docker stack (Flask/Gunicorn + PostgreSQL) | Reproducible local multi-container environment with no runtime dependency on external CDNs or third-party application services; zero hosting cost; sub-millisecond local latency | Requires Docker Desktop on host machine; not publicly accessible over internet | **PRIMARY TARGET (Academic & Evaluation Committee Demonstration)** |
| **Option 2: Render.com** | Managed Docker Web Service + Managed PostgreSQL | Built directly from repository `8_DEPLOYMENT/Dockerfile`; automated SSL/TLS certificates; git-push deployment; native secret injection | Free tier spins down after 15 min inactivity (~50s cold start); free PostgreSQL instance expires after 30 days | **SECONDARY TARGET (Public Cloud Live Demonstration)** |
| **Option 3: Railway.app** | Container PaaS + PostgreSQL service plugin | Instant deployment, integrated metrics, persistent volume support | $5 trial credit limit requires credit card; variable pricing | **Viable Alternative** |
| **Option 4: Fly.io** | Global container deployment via `fly launch` | Low latency, global edge routing | Credit card verification required; volume management has manual setup overhead | **Viable Alternative** |
| **Option 5: Google Cloud (Cloud Run + Cloud SQL)** | Serverless container execution + Managed Cloud SQL | High scalability, Google Cloud alignment, zero idle container CPU cost | Cloud SQL has no permanent free tier ($10+/mo); IAM, VPC connector, and setup complexity | **Production Alternative** |
| **Option 6: AWS (Lightsail / ECS)** | Container service + Managed RDS | Industry standard infrastructure | Significant billing setup and IAM configuration overhead for academic project | **Complex Alternative** |

### Clarified Render Deployment Model:

To eliminate ambiguity, Render deployment will follow this planned approach:

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

**Authoritative Specification:**
- **"Render will build the application from the same repository Dockerfile used for local container verification."**
- No external container registry (e.g., Docker Hub, GitHub Container Registry) is introduced unless a demonstrated operational need arises during implementation.
- Both local and public targets build and run from the identical container definition (`8_DEPLOYMENT/Dockerfile`).

### Explicit Distinction Between Local and Public Deployment:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ LOCAL DEPLOYMENT                                                             │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Execution: docker build -t smart-water-advisor:latest                      │
│ • Orchestration: docker compose -f 8_DEPLOYMENT/docker-compose.yml up        │
│ • Database: Local containerized PostgreSQL 15 on named volume (pgdata)       │
│ • Networking: Isolated internal bridge network (water_net)                   │
│ • Verification: http://localhost:5000/ via automated test harness and probe │
│ • Environment: Local .env / docker-compose environment variables             │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ PUBLIC CLOUD DEPLOYMENT                                                      │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Execution: Render Docker Web Service triggered from GitHub repository      │
│ • Orchestration: Managed container execution built via 8_DEPLOYMENT/Dockerfile│
│ • Database: Render Managed PostgreSQL instance                               │
│ • Networking: Public HTTPS with automatic TLS certificate termination        │
│ • Verification: https://<app-name>.onrender.com via verify_deployment.py    │
│ • Environment: Injected via Render Dashboard (production secrets)            │
└──────────────────────────────────────────────────────────────────────────────┘
```

*Rule:* Do not claim Render deployment is complete during planning. Verification must be performed empirically after actual implementation.

---

## 6. WSGI Entry Point Strategy (Resolution of WSGI Duplication)

### Repository Inspection Finding:
Inspection of `4_DEVELOPMENT/backend/` confirms that **no `wsgi.py` file currently exists** in the repository. The existing Phase 5 application factory is located at `4_DEVELOPMENT/backend/app.py:create_app()`.

### Authoritative Strategy Selection: **Dedicated Deployment Wrapper (`8_DEPLOYMENT/wsgi.py`)**:
To maintain clean separation between core application source code and deployment process management, **exactly ONE authoritative WSGI entry point** will be created at:

`8_DEPLOYMENT/wsgi.py`

#### Architectural Specification:
- **Role:** The single, authoritative WSGI entry point for production process managers (Gunicorn, Docker container).
- **Import Pathway:** Imports the application factory from `4_DEVELOPMENT.backend.app`:
  ```python
  import os
  import sys

  BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
  if BASE_DIR not in sys.path:
      sys.path.insert(0, BASE_DIR)

  DEV_DIR = os.path.join(BASE_DIR, "4_DEVELOPMENT")
  if DEV_DIR not in sys.path:
      sys.path.insert(0, DEV_DIR)

  from backend.app import create_app
  app = create_app()
  ```
- **Zero Code Duplication:** It contains zero route definitions, zero middleware logic, and zero error handlers; it strictly instantiates the single canonical Flask application instance via the existing application factory `create_app()`.
- **Authoritative Status:** `8_DEPLOYMENT/wsgi.py` is the sole WSGI entrypoint. No second `wsgi.py` will be created in `4_DEVELOPMENT/backend/`.

---

## 7. Gunicorn Strategy & Configuration

The WSGI production server configuration will be created at `8_DEPLOYMENT/gunicorn.conf.py`.

### Environment-Configurable Parameters & Sensible Defaults:

```python
import os

bind = os.getenv("GUNICORN_BIND", "0.0.0.0:5000")
workers = int(os.getenv("GUNICORN_WORKERS", "2"))
threads = int(os.getenv("GUNICORN_THREADS", "2"))
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "gthread")
timeout = int(os.getenv("GUNICORN_TIMEOUT", "60"))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", "5"))
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", "30"))
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
accesslog = "-"
errorlog = "-"
preload_app = False
```

### Initial Defaults Methodology:
- **Initial Baseline Defaults:** 2 workers, 2 threads each ($2 \times 2 = 4$ concurrent request capacity).
- **Rationale:** 
  1. Each Gunicorn worker process loads scikit-learn model weights into memory. On typical 1–2 core containers with 512 MB to 1 GB RAM, 2 workers with 2 threads provides concurrency without risking container Out-Of-Memory (OOM) termination.
  2. The `gthread` worker class handles I/O-bound database queries and static file serving concurrently while keeping memory usage constrained.
  3. Timeout defaults to 60s to accommodate cold model deserialization on resource-constrained platforms, while warm requests execute in $< 50$ ms.
- **Dynamic Tuning Principle:** The chosen values are sensible initial defaults, **not universally optimal**. Final tuning depends on:
  - Deployment CPU and memory allocation.
  - Measured concurrency and request volume.
  - Application latency and memory profiles under load.

---

## 8. Gunicorn & Docker Dependency Strategy

### Inspection of Existing Repository Requirements:
Inspection of root `requirements.txt` reveals 12 cleanly defined application runtime dependencies:
```text
SQLAlchemy>=2.0.0
psycopg2-binary>=2.9.9
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
joblib>=1.3.0
python-dotenv>=1.0.0
bcrypt>=4.0.0
PyJWT>=2.8.0
Flask>=3.0.0
Flask-Cors>=4.0.0
pytest>=7.0.0
```

### Evaluation of Windows vs. Linux Dependency Strategy:
- **Core Challenge:** Development is conducted on Windows (`win32_x64`), whereas Gunicorn is a UNIX-only WSGI process manager relying on POSIX system calls (`fcntl`). Adding `gunicorn>=21.2.0` directly to root `requirements.txt` causes installation errors or build failures on Windows developer workstations.
- **Cleanest Strategy Selection:** A deployment-specific requirements file at **`8_DEPLOYMENT/requirements-deploy.txt`**.
- **Distinction of Dependency Scopes:**
  - **Development Dependencies:** Defined in root `requirements.txt`. Contains all application packages, database drivers, ML libraries, and pytest. Runs seamlessly on Windows.
  - **Deployment Dependencies:** Defined in `8_DEPLOYMENT/requirements-deploy.txt`. Contains:
    ```text
    -r ../requirements.txt
    gunicorn>=21.2.0
    ```
    Contains Gunicorn and references the existing application dependencies required by the container.
- **Why This Strategy Is Chosen:**
  1. Gunicorn becomes available inside the Linux deployment container without unnecessarily complicating Windows development.
  2. The root `requirements.txt` remains the single authoritative source for application code and unit testing.
  3. No unrelated packages or build utilities are added.

### Docker Image Build Strategy:
1. **Base Image:** `python:3.11-slim` (Debian Bookworm base).
2. **Prebuilt Binary Wheels:** Prioritize binary wheel installation for all numeric and database dependencies (`scikit-learn>=1.3.0`, `numpy>=1.24.0`, `pandas>=2.0.0`, `psycopg2-binary>=2.9.9`, `bcrypt>=4.0.0`).
3. **No Unnecessary Build Tools:** Do NOT install `build-essential`, `gcc`, or `g++` inside the Dockerfile unless an actual dependency proves incompatible with prebuilt wheels during Phase 6 implementation verification.
4. **Minimal System Utilities:** Only install `curl` for container healthcheck execution (`apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*`).
5. **Layer Caching & Size Optimization:** Copy requirements first to leverage Docker layer caching; clean package manager caches; target a final image size under 450 MB.
6. **Dependency Compatibility Verification:** Empirical verification via `pip check` will be performed during Phase 6 implementation.

### Dockerfile Specification (`8_DEPLOYMENT/Dockerfile`):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

# Install minimal healthcheck utility
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies via deployment requirements
COPY requirements.txt ./
COPY 8_DEPLOYMENT/requirements-deploy.txt ./8_DEPLOYMENT/
RUN pip install --no-cache-dir -r 8_DEPLOYMENT/requirements-deploy.txt

# Copy application source tree
COPY . /app/

# Configure non-root execution
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/sh appuser && \
    chown -R appuser:appgroup /app

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

CMD ["gunicorn", "--config", "8_DEPLOYMENT/gunicorn.conf.py", "8_DEPLOYMENT.wsgi:app"]
```

### Docker Ignore Specification (`8_DEPLOYMENT/.dockerignore`):
Excludes development caches, virtual environments, scratch files, and secrets:
```text
.git
.venv
.pytest_cache
__pycache__
*.pyc
*.pyo
*.pyd
.env
.env.*
scratch/
smart_water_advisor_*.db
test_*.db
*.log
```

---

## 9. Secret Management: Build Time vs. Runtime

### Strict Separation:

#### BUILD TIME (Zero Secrets Allowed):
- **Never COPY `.env`:** The `.dockerignore` file strictly prevents `.env` or any local environment files from entering the Docker build context.
- **No Embedded Credentials:** No JWT secrets, no database passwords, and no Gemini API keys are baked into Dockerfile instructions, build arguments, or image layers.
- **Verification Step:** Phase 6 implementation includes a dedicated inspection step using `docker history` to verify zero sensitive strings exist in image layers.

#### RUNTIME (Injected Configuration):
All sensitive configuration is injected strictly at container launch via environment variables:
- `JWT_SECRET_KEY`: Cryptographically random 64-character hex string (generated via `python -c "import secrets; print(secrets.token_hex(32))"`).
- `SECRET_KEY`: Independent cryptographically random 64-character hex string.
- `DATABASE_URL`: Full PostgreSQL connection string injected by orchestrator or host.
- `GEMINI_API_KEY`: Optional; if omitted, the system operates via the deterministic grounded provider.
- `CORS_ALLOWED_ORIGINS`: Comma-separated list of permitted origins; wildcards (`*`) are prohibited in production.

### Operational Secret Rules:
1. `.env` remains strictly Git-ignored.
2. `.env.example` contains descriptive placeholders only.
3. Production configuration fails closed: `4_DEVELOPMENT/backend/config.py` raises `ValueError` on startup if `JWT_SECRET_KEY` or `SECRET_KEY` is missing or uses default dev-fallback strings.
4. Secrets must never appear in application logs, database error messages, or API JSON responses.
5. Secrets must never be exposed to frontend JavaScript.
6. A Phase 6 verification step will inspect runtime logs and API responses to verify zero secret leakage without printing or exposing actual secret values.

---

## 10. PostgreSQL Deployment, Initialization & Persistence

### Authoritative Operational Database Status:
PostgreSQL remains the **authoritative operational database** of the Smart Water Usage Advisor. SQLite is strictly a local unit-test fallback and is **never used as a production database**.

### Authoritative Schema Location:
Repository inspection confirms that the authoritative PostgreSQL schema defining all 12 normalized tables is located at:

**`4_DEVELOPMENT/backend/database/init_schema.sql`**

No duplicate schema file will be created.

### Database Deployment Architecture & Persistence Rules:
1. **Existing authoritative 12-table PostgreSQL schema remains unchanged:** The DDL in `4_DEVELOPMENT/backend/database/init_schema.sql` is preserved verbatim.
2. **Docker Compose maps the existing schema file into PostgreSQL initialization only if appropriate:** In `docker-compose.yml`, `4_DEVELOPMENT/backend/database/init_schema.sql` is mounted to `/docker-entrypoint-initdb.d/01_init_schema.sql:ro`.
3. **PostgreSQL initialization scripts under `/docker-entrypoint-initdb.d/` execute on a fresh database volume:** The official PostgreSQL entrypoint runs scripts in `/docker-entrypoint-initdb.d/` only when the data directory (`/var/lib/postgresql/data`) is completely empty.
4. **Reused volumes retain existing database state:** When an existing named Docker volume (`pgdata`) is attached, PostgreSQL detects the existing database cluster, bypasses `/docker-entrypoint-initdb.d/`, and starts normally. All previously committed records are retained.
5. **Schema initialization must not silently overwrite an existing database:** Because entrypoint scripts execute only on fresh volumes and tables use `CREATE TABLE IF NOT EXISTS`, existing database clusters are never overwritten.
6. **Any seed process must use the existing project seeding mechanism where appropriate:** Initial data ingestion will utilize `4_DEVELOPMENT/backend/database/seed_database.py` (which checks for existing records before inserting to maintain idempotency) rather than creating an unvetted SQL seed script.

### Readiness, Synchronization & Error Visibility:
- In `docker-compose.yml`, the database service includes an automated healthcheck:
  ```yaml
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U postgres -d smart_water_advisor_db"]
    interval: 10s
    timeout: 5s
    retries: 5
  ```
- The application service (`web`) specifies `depends_on: { db: { condition: service_healthy } }`, ensuring Flask/Gunicorn does not start until PostgreSQL is accepting connections.
- Database startup errors are logged directly to container stderr. If PostgreSQL fails to initialize, the healthcheck probe fails and prevents the `web` container from launching, surfacing the failure immediately.

### PostgreSQL Version Compatibility Verification:
- The proposed container image is `postgres:15-alpine`.
- **Planning Rule:** Compatibility with PostgreSQL 15 is **NOT assumed or claimed in advance**. Phase 6 implementation must empirically verify:
  - 12-table DDL syntax compatibility in `4_DEVELOPMENT/backend/database/init_schema.sql`.
  - SQLAlchemy 2.0+ engine and connection pool behavior.
  - `psycopg2-binary` driver handshake and SSL mode compatibility.
  - Execution of `seed_database.py` and integration tests (`test_database_schema.py`, `test_database_seeding.py`).
- If compatibility testing reveals any issue with PostgreSQL 15, the findings will be documented and a compatible version (e.g., PostgreSQL 14 or 16) will be pinned instead, without altering the authoritative 12-table schema.

---

## 11. Deployment Verification Script (`8_DEPLOYMENT/verify_deployment.py`)

### Dependency Decision:
The deployment verification script will be implemented **strictly using Python's built-in standard library**:
- `urllib.request` and `urllib.error` for HTTP requests.
- `json` for payload encoding and response parsing.
- `sys` and `argparse` for CLI execution.

**Zero External Dependencies:** The `requests` package will NOT be added to `requirements.txt` or `requirements-deploy.txt` solely for deployment verification.

### Verification Capabilities:
1. **Health Probe:** Queries `GET /api/health` and verifies HTTP 200 and `"status": "healthy"`.
2. **Static Asset Verification:** Queries `GET /` and verifies HTTP 200 with valid HTML structure.
3. **Vendored Chart.js:** Queries `GET /js/vendor/chart.umd.js` and verifies HTTP 200 with valid JavaScript.
4. **Authentication:** Submits `POST /api/auth/login` and receives valid JWT token.
5. **Protected Dashboard Access:** Queries `GET /api/dashboard/summary` with Bearer token.
6. **BOLA/IDOR Enforcement:** Attempts cross-tenant query and asserts `HTTP 403 Forbidden`.
7. **Forecasting Endpoint:** Queries `GET /api/v1/forecast/meters/1` and verifies 7-day array with uncertainty bounds.
8. **Chatbot Endpoint:** Queries `POST /api/v1/chat` and verifies grounded response with plumbing disclaimer.

---

## 12. Windows Development vs. Container Regression Testing

### Environment Distinction:
Phase 6 explicitly separates:
1. **Existing Development-Machine Regression Testing:** Executed on the local host Windows environment via `.venv\Scripts\pytest 6_TESTING/ -v`.
2. **Linux / Container Deployment Verification:** Executed inside the containerized Linux environment via container smoke tests and automated HTTP probes.

### Test Count Terminology & Formula:
```text
130 currently verified tests consist of:
  84 upstream baseline regression tests
+ 46 Phase 5 integration/security/governance tests
= 130 currently verified tests.
```

- **Phase 6 Scope:** Phase 6 introduces additional deployment smoke tests ([`test_deployment_smoke.py`](file:///c:/Users/singh/Cisco%20Packet%20Tracer%209.0.0/saves/ai%20sustainability%20project/6_TESTING/integration_tests/test_deployment_smoke.py)).
- **Empirical Measurement Rule:** The final Phase 6 test count will be measured empirically after implementation. The final total will not be hardcoded or fabricated in advance.
- **Container Environment Verification:** Where practical, verify that the application and relevant test suite also function correctly inside the Linux-based container environment.
- **Host-Only Documentation:** If some existing tests are intentionally host-only or require external infrastructure (e.g. Windows path separators or local SQLite test databases), document the reason rather than silently skipping them.
- **Test Integrity:** Never delete or weaken tests.

### Deployment Smoke Tests (`6_TESTING/integration_tests/test_deployment_smoke.py`):
Automated test module validating deployment configuration contracts:
1. `test_wsgi_entrypoint_loads`: Verifies `8_DEPLOYMENT/wsgi.py` instantiates Flask application without error.
2. `test_gunicorn_configuration_syntax`: Validates `gunicorn.conf.py` parses cleanly and respects environment variables.
3. `test_health_endpoint_contract`: Asserts `/api/health` returns operational status, component checks, and timestamp.
4. `test_production_config_enforcement`: Asserts application raises `ValueError` if `JWT_SECRET_KEY` is missing in production.
5. `test_static_frontend_served_at_root`: Asserts `GET /` returns HTML content containing dashboard DOM nodes.
6. `test_offline_chart_js_accessible`: Asserts `GET /js/vendor/chart.umd.js` returns HTTP 200.
7. `test_database_connectivity_or_graceful_degradation`: Asserts database queries succeed or return labeled degraded cache.

---

## 13. AI Model Deployment & Integrity Protection

- **Phase 3A Forecaster:** `5_AI_COMPONENTS/predictive_models/models/forecasting_model.joblib` (434 KB) loaded by `ml_models.py`. Validated Seasonal Naive 7-day benchmark fallback preserved. Validated forecast uncertainty bounds strictly preserved.
- **Phase 3B Detector:** `5_AI_COMPONENTS/anomaly_detection/models/isolation_forest.joblib` (1.23 MB) and `diurnal_baselines.csv` loaded by detector pipeline. Calibrated deterministic fallback preserved.
- **Phase 3C Chatbot:** Knowledge base (16 topics) and `DeterministicGroundedProvider` preserved. Optional Gemini provider activated only when `GEMINI_API_KEY` is supplied at runtime.
- **Strict Integrity Rules:**
  - Zero model retraining.
  - Zero anomaly threshold recalibration.
  - Zero modification to validated performance metrics.
  - Ground-truth anomaly labels strictly isolated from detector input features.

---

## 14. Responsible AI Finalization

Phase 6 ensures that all Responsible AI principles defined in `7_ETHICS_COMPLIANCE/` are visibly preserved across production interfaces, API responses, and presentation materials:

1. **Synthetic Telemetry Transparency:** Clear disclosure that data represents mathematical simulation calibrated against municipal benchmarks (zero real consumer PII).
2. **Forecast Uncertainty Terminology:** All projections framed with *"validated forecast uncertainty bounds"* rather than unvalidated "95% confidence intervals".
3. **Anomaly Uncertainty:** No claims of "100% leak detection guarantee" or "zero false alarms".
4. **Human Oversight & Agency:** Strictly decision support; zero automated valve shutoff or actuator control.
5. **Certified Plumbing Safety:** High-severity burst and continuous leak alerts mandate licensed plumber referral disclaimers.
6. **Estimated Potential Savings:** Quantified volumetric (L/day) and financial ($/mo) savings are explicitly designated as estimates.
7. **Knowledge Grounding:** Chatbot responses cite verified municipal water conservation topics; lack of context triggers transparent limitation disclaimers.

---

## 15. Final Documentation Plan (`1_DOCUMENTATION/`)

1. **`phase_6_implementation_plan.md`** (This corrected master plan).
2. **`phase_6_walkthrough.md`**: Post-implementation report recording actual Docker build logs, smoke test results, empirical test counts, and release milestones.
3. **`deployment_guide.md`**: Comprehensive operations manual covering:
   - System prerequisites (Docker, Docker Compose, Python 3.11).
   - Local Docker Compose launch (`docker compose -f 8_DEPLOYMENT/docker-compose.yml up --build`).
   - Standalone Python execution (`run_production_api.py`).
   - PostgreSQL volume initialization, persistence, and backup/restore.
   - Step-by-step cloud deployment to Render.com (Web Service + Managed PostgreSQL).
   - Environment variable reference table and secure secret generation commands.
   - Operational troubleshooting and common error resolutions.
4. **`api_reference.md`**: Full REST API specification covering all 7 blueprints, route paths, HTTP methods, headers, parameters, JSON schemas, status codes, and curl examples.
5. **`final_project_report.md`**: Comprehensive 12-week capstone academic project report synthesizing research, architecture, data pipelines, AI models, frontend UX, security, ethical compliance, and empirical benchmarks.
6. **`README.md`**: Updated repository root overview with quickstart guides, architecture badges, test summary, and deployment instructions.

---

## 16. Final Presentation Plan (`9_PRESENTATION/`)

1. **Presentation Slide Deck Script (`9_PRESENTATION/presentation_slides.md`):**
   - 16-slide academic presentation script structured for a 15–20 minute evaluation committee presentation covering UN SDG 6, architecture, data pipeline, forecasting, anomaly detection, chatbot, security, Responsible AI, and deployment.
2. **Live Demonstration Script (`9_PRESENTATION/live_demo_script.md`):**
   - 11-step interactive demonstration script:
     1. System launch via Docker Compose with healthcheck passing.
     2. Landing page display at `http://localhost:5000/`.
     3. Persona login (Sarah Jenkins).
     4. 24-hour KPI overview and SDG 6 efficiency rating.
     5. Diurnal curve and 30-day historical analytics.
     6. 7-day forecast with validated uncertainty bounds.
     7. Continuous leak alert and estimated water loss.
     8. Ranked conservation actions with estimated financial savings.
     9. Chatbot query, verified knowledge citation, and plumbing safety notice.
     10. Persona switch and BOLA/IDOR 403 Forbidden verification.
     11. Operational telemetry query to `/api/health`.
3. **Executive Summary (`9_PRESENTATION/project_executive_summary.md`):**
   - Concise 2-page brief summarizing project goals, technical architecture, sustainability impact, and empirical achievements.

---

## 17. Final Project Packaging

1. **Repository Cleanliness:** No temporary files, test databases (`*.db`), or scratch scripts committed.
2. **Exclusions Enforced:**
   - Git ignores: `.venv/`, `.git/`, `.env`, `scratch/`, `__pycache__/`, `*.db`.
   - Docker ignores: test caches, scratch folders, virtual environments.
3. **Deliverable Structure:**
   - `1_DOCUMENTATION/`: Complete design, walkthrough, deployment, API, and capstone reports.
   - `2_RESEARCH_DATA/`: Research papers, data plan, and case studies.
   - `3_DESIGN/`: Wireframes, conversation flows, and architecture diagrams.
   - `4_DEVELOPMENT/`: Backend code, frontend assets, database initialization/seeding scripts, synthetic telemetry generator.
   - `5_AI_COMPONENTS/`: Pre-trained models (`forecasting_model.joblib`, `isolation_forest.joblib`), chatbot logic, knowledge base.
   - `6_TESTING/`: Unit tests, integration tests, performance metrics, and deployment smoke tests.
   - `7_ETHICS_COMPLIANCE/`: Responsible AI audit, model cards, and dataset datasheet.
   - `8_DEPLOYMENT/`: Dockerfile, docker-compose.yml, gunicorn.conf.py, wsgi.py, requirements-deploy.txt, verify_deployment.py.
   - `9_PRESENTATION/`: Presentation slides, demo script, and executive summary.
   - `10_APPENDICES/`: Academic references, standards mapping, and glossary.

---

## 18. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation Strategy |
| :--- | :---: | :---: | :--- |
| **Docker Build Failure (missing binary wheel)** | High | Low | Base image pinned to `python:3.11-slim`; prebuilt wheels prioritized; build tools added only if verified necessary. |
| **PostgreSQL Container Startup Delay** | Med | Med | Docker Compose configured with `pg_isready` healthcheck; `web` container blocked until `db` is healthy. |
| **Missing Production Secrets** | High | Low | `config.py` enforces fail-closed validation; `docker-compose.yml` provides documented defaults with override instructions. |
| **Model Serialization Incompatibility** | High | Low | Python version in container matches development environment (3.11/3.14); automated fallback to Seasonal Naive baseline if deserialization fails. |
| **Database Network Isolation Failure** | Med | Low | Containers communicate over dedicated internal bridge network (`water_net`); PostgreSQL port only bound if explicitly mapped. |
| **Container Memory Exhaustion (OOM)** | High | Low | Gunicorn configured with configurable defaults (2 workers, 2 threads); preloading disabled to prevent duplicate heap allocations. |
| **BOLA/IDOR Security Bypass** | High | Low | Middleware `@meter_access_required` strictly binds meter access to authenticated token `sub`. |
| **Static Asset 404 in Container** | Med | Low | Flask static route explicitly configured with absolute container paths resolving to `/app/4_DEVELOPMENT/frontend`. |
| **Gemini LLM API Outage or Rate Limit** | Med | Med | Decoupled architecture defaults to `DeterministicGroundedProvider`; zero runtime dependency on external LLM availability. |
| **Accidental Secret Commit to Git** | Critical| Low | `.gitignore` and `.dockerignore` exclude `.env`; automated verification checks verify clean git status before release. |
| **Test Regression During Containerization**| High | Low | Full 130 currently verified tests executed prior to container packaging; dedicated smoke tests verify container contracts. |
| **Host Port Conflict (Port 5000 or 5432)** | Low | Med | Port mappings parameterized in `docker-compose.yml` via environment variables (`${WEB_PORT:-5000}`). |
| **Chart.js CDN Failure** | Med | Zero | Chart.js is vendored locally in `4_DEVELOPMENT/frontend/js/vendor/chart.umd.js` with no runtime CDN dependency. |
| **PostgreSQL Volume Permission Error** | Med | Low | Official `postgres:15-alpine` handles data directory ownership automatically on mounted named volumes. |
| **Incomplete Demonstration Setup** | Med | Low | Standalone demonstration script provided with automated seed data reset command. |
| **Git Force Push / Branch Corruption** | Critical| Zero | Git commits and pushes strictly restricted to explicit user commands; force push prohibited. |

---

## 19. Final Implementation Order (21 Sequential Steps)

The implementation of Phase 6 will proceed in a strict, dependency-aware sequence:

1. **Deployment readiness audit:** Verify all upstream model artifacts, frontend assets, database scripts, and test suites are present and clean.
2. **Environment/secret configuration:** Verify `.env.example` template; establish build-time vs. runtime secret boundaries.
3. **Resolve deployment dependency strategy:** Create `8_DEPLOYMENT/requirements-deploy.txt` with Gunicorn; keep root `requirements.txt` clean and Windows-compatible.
4. **Dockerfile:** Create `8_DEPLOYMENT/Dockerfile` using `python:3.11-slim` with non-root security and prebuilt wheels.
5. **PostgreSQL container configuration:** Configure PostgreSQL container specification, persistent volume mount, and `init_schema.sql` hook.
6. **Docker Compose:** Create `8_DEPLOYMENT/docker-compose.yml` orchestrating `web` and `db` services with health dependency.
7. **WSGI/Gunicorn:** Create authoritative `8_DEPLOYMENT/wsgi.py` and configurable `8_DEPLOYMENT/gunicorn.conf.py`.
8. **Local Docker build:** Execute `docker build` and verify layer history has zero embedded secrets.
9. **Local Docker startup:** Execute `docker compose up` and verify both services reach healthy states.
10. **Database initialization verification:** Empirically verify PostgreSQL 15 schema compatibility, table creation, and volume persistence.
11. **Deployment smoke tests:** Create and run `6_TESTING/integration_tests/test_deployment_smoke.py`.
12. **Regression testing:** Execute `.venv\Scripts\pytest 6_TESTING/ -v` confirming all 130 currently verified tests plus new smoke tests pass.
13. **Security verification:** Audit container logs, headers, BOLA protection, and fail-closed secret handling.
14. **Render deployment configuration:** Create Render deployment configuration using the same repository Dockerfile.
15. **Render deployment:** Deploy to Render.com with user-provided production environment variables.
16. **Public deployment smoke testing:** Execute `8_DEPLOYMENT/verify_deployment.py` against the live public HTTPS Render URL.
17. **Performance/health verification:** Query `/api/health` on both local and public targets, verifying latency and operational status.
18. **Final documentation:** Author `deployment_guide.md`, `api_reference.md`, and `final_project_report.md` in `1_DOCUMENTATION/`.
19. **Final presentation:** Author `presentation_slides.md`, `live_demo_script.md`, and `project_executive_summary.md` in `9_PRESENTATION/`.
20. **Release packaging:** Update `README.md` (roadmap to Phase 6 Active, then Phase 6 Complete), author `phase_6_walkthrough.md`, and clean working tree.
21. **Final acceptance verification:** Conduct final review against all Local, Public, and Quality acceptance criteria.

---

## 20. Final Phase 6 Acceptance Criteria

Phase 6 can only be declared **COMPLETE** after actual empirical verification across both deployment targets and overall quality criteria:

### A. LOCAL DOCKER ACCEPTANCE

Require actual verification of:
1. Docker image builds
2. Docker Compose starts
3. PostgreSQL becomes healthy
4. Database schema initializes correctly on a fresh volume
5. Existing data persists on volume reuse
6. Gunicorn starts
7. Flask application starts
8. Frontend loads
9. `/api/health` works
10. Authentication works
11. BOLA/IDOR protection works
12. Forecasting works
13. Anomaly detection works
14. Chatbot works
15. Deployment smoke tests pass
16. Existing regression tests pass

### B. PUBLIC DEPLOYMENT ACCEPTANCE

Require actual verification of:
1. Render service deploys successfully
2. HTTPS URL is reachable
3. Production environment variables are configured
4. PostgreSQL connection works
5. Database is initialized correctly
6. Gunicorn is running
7. Frontend loads
8. `/api/health` works
9. Authentication works
10. Dashboard works
11. Forecasting works
12. Anomaly detection works
13. Chatbot works
14. BOLA/IDOR remains protected
15. Responsible AI disclosures remain visible
16. Public deployment smoke test passes

> [!IMPORTANT]
> **Public Deployment Completion Rule**:
> If public deployment is not actually completed and verified, Phase 6 must not be declared complete.
> Never fabricate public deployment results.

### C. QUALITY & DELIVERABLE ACCEPTANCE

- [ ] **130 Currently Verified Tests Preserved:** All 130 currently verified tests continue to pass without modification.
- [ ] **Additional Phase 6 Tests Pass:** Additional deployment smoke tests pass; final total test count measured empirically.
- [ ] **No Secrets Exposed:** Image layer history and runtime logs inspected; zero secrets leaked.
- [ ] **No Phase 7 Created:** Scope remains strictly bounded to Phase 6.
- [ ] **Final Documentation Complete:** Deployment Guide, API Reference, and Final Capstone Report authored in `1_DOCUMENTATION/`.
- [ ] **Final Presentation Complete:** Slide deck script, demo script, and executive summary authored in `9_PRESENTATION/`.
- [ ] **Release Package Clean:** Working tree clean; `.gitignore` and `.dockerignore` enforced.

---

## 21. Phase Boundary Confirmation

- **Final Lifecycle Phase:** Phase 6 is the final phase of the Smart Water Usage Advisor project. There is **no Phase 7**.
- **No Early Execution:** During planning, zero deployment files, containers, or code modifications are made.
- **Git Protection:** No git commits will be made during planning. Commits during implementation require explicit user authorization.
- **README Status Rule:** README roadmap will state "Phase 6 Active" during implementation, and "Phase 6 Complete" only after actual acceptance verification.

---

## 22. Final Required Files Manifest

Based on thorough inspection of the repository, the following file manifest will govern Phase 6 execution:

### FILES TO CREATE in Phase 6:

**Deployment:**
- `8_DEPLOYMENT/Dockerfile` (Production container definition)
- `8_DEPLOYMENT/docker-compose.yml` (Multi-container stack definition)
- `8_DEPLOYMENT/.dockerignore` (Build context exclusion rules)
- `8_DEPLOYMENT/gunicorn.conf.py` (WSGI server configuration)
- `8_DEPLOYMENT/wsgi.py` (ONE authoritative single WSGI application entry point)
- `8_DEPLOYMENT/requirements-deploy.txt` (Deployment-specific requirements file containing Gunicorn)
- `8_DEPLOYMENT/verify_deployment.py` (Standard-library HTTP deployment smoke verification script)

**Testing:**
- `6_TESTING/integration_tests/test_deployment_smoke.py` (Deployment smoke tests)

**Documentation:**
- `1_DOCUMENTATION/phase_6_walkthrough.md` (Final phase walkthrough)
- `1_DOCUMENTATION/deployment_guide.md` (Operations manual for Docker, Compose, and Cloud)
- `1_DOCUMENTATION/api_reference.md` (Complete OpenAPI/REST specification)
- `1_DOCUMENTATION/final_project_report.md` (Comprehensive academic capstone report)

**Presentation:**
- `9_PRESENTATION/presentation_slides.md` (16-slide academic presentation script)
- `9_PRESENTATION/live_demo_script.md` (11-step interactive demonstration script)
- `9_PRESENTATION/project_executive_summary.md` (2-page capstone executive summary)

### FILES TO MODIFY in Phase 6:
- `README.md` (Update roadmap to Phase 6 Active during implementation, then Phase 6 Complete after acceptance)
- `requirements.txt` (ONLY if actually required; currently remains clean and unmodified for Windows development)

### FILES THAT MUST REMAIN UNCHANGED (Integrity Protection):
- `4_DEVELOPMENT/backend/app.py`
- `4_DEVELOPMENT/backend/config.py`
- `4_DEVELOPMENT/backend/dashboard_data_service.py`
- `4_DEVELOPMENT/backend/services/auth_service.py`
- `4_DEVELOPMENT/backend/api/` (All 7 blueprints + middleware)
- `4_DEVELOPMENT/backend/database/` (`init_schema.sql`, `init_database.py`, `seed_database.py`, `db_config.py`)
- `4_DEVELOPMENT/frontend/` (`index.html`, `css/styles.css`, `js/app.js`, `js/components/*.js`, `js/vendor/chart.umd.js`)
- `4_DEVELOPMENT/ml_models.py`
- `5_AI_COMPONENTS/predictive_models/models/forecasting_model.joblib`
- `5_AI_COMPONENTS/anomaly_detection/models/isolation_forest.joblib`
- `5_AI_COMPONENTS/chatbot/` (All chatbot modules and knowledge base)
- `6_TESTING/unit_tests/` (All 7 unit test files)
- `6_TESTING/integration_tests/` (Existing 6 integration test files)
- `7_ETHICS_COMPLIANCE/` (All 4 governance artifacts)

---

## 23. Verification Commands

The following commands will be used to verify the Phase 6 implementation:

```bash
# 1. Full Regression Test Harness (All 130 currently verified tests + new smoke tests)
.venv\Scripts\python.exe -m pytest 6_TESTING/ -v

# 2. Dependency Audit
.venv\Scripts\python.exe -m pip check

# 3. Local Standalone API Run
.venv\Scripts\python.exe run_production_api.py --port 5000

# 4. Docker Build Verification
docker build -t smart-water-advisor:latest -f 8_DEPLOYMENT/Dockerfile .

# 5. Inspect Docker Image Layer History for Zero Secrets
docker history --no-trunc smart-water-advisor:latest

# 6. Docker Compose Stack Launch
docker compose -f 8_DEPLOYMENT/docker-compose.yml up -d

# 7. Deployment Smoke Verification Script (Standard Library HTTP - Local)
.venv\Scripts\python.exe 8_DEPLOYMENT/verify_deployment.py --url http://localhost:5000

# 8. Deployment Smoke Verification Script (Standard Library HTTP - Public Render URL)
.venv\Scripts\python.exe 8_DEPLOYMENT/verify_deployment.py --url https://your-app-name.onrender.com

# 9. Docker Compose Stack Teardown
docker compose -f 8_DEPLOYMENT/docker-compose.yml down

# 10. Working Tree Cleanliness Check
git status
```

---

## 24. Final Readiness Checklist

- [x] Repository inspected across all 10 canonical directories.
- [x] Verified 130 currently verified tests (84 upstream baseline + 46 Phase 5 tests) passing on main branch.
- [x] Removed exaggerated claims of "100% reproducible offline" and ungrounded guarantees.
- [x] Confirmed reuse of existing authoritative schema `4_DEVELOPMENT/backend/database/init_schema.sql` (12 tables).
- [x] Resolved Gunicorn dependency strategy using `8_DEPLOYMENT/requirements-deploy.txt` to preserve Windows compatibility.
- [x] Clarified Render deployment model using the same repository Dockerfile.
- [x] Separated Local Docker and Public Deployment Acceptance into explicit independent sections with all 16 criteria each.
- [x] Distinguished Windows host regression testing from Linux container verification.
- [x] Scoped `verify_deployment.py` strictly to Python standard library.
- [x] Detailed PostgreSQL volume persistence on reuse vs. fresh initialization.
- [x] Required empirical verification of PostgreSQL 15 compatibility.
- [x] Corrected test count terminology to "130 currently verified tests".
- [x] Updated 21-step implementation order and file manifest.
- [x] Zero code, container, or configuration modifications made during planning.
- [x] Zero Git commits created during planning.

---

### PHASE 6 STATUS

PLANNING ONLY — PENDING USER APPROVAL

Do NOT implement anything.

Do NOT create Docker/Gunicorn files.

Do NOT deploy to Render.

Do NOT install dependencies.

Do NOT make a Git commit.

STOP after updating the plan.
