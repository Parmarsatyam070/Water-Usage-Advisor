# ⚙️ Technical Architecture & Trade-Off Decisions
**Document ID:** 07_Technical_Decisions  
**Status:** Approved Phase 1 Architecture Plan  
**Governance:** Explicitly demarcates SOURCE REQUIREMENTS from IMPLEMENTATION DECISIONS.

---

## 1. Summary Matrix of Architectural Decisions

| Decision Area | Selected Technology / Approach | Classification | Rationale & Trade-Offs |
| :--- | :--- | :--- | :--- |
| **Application Framework** | **Flask (Python REST API + Service Architecture)** | **IMPLEMENTATION DECISION** *(Source allows Flask or Streamlit)* | Flask enables clean decoupled REST APIs, native support for relational PostgreSQL schemas, custom responsive HTML5/CSS3 frontend, and straightforward background ML task execution. Streamlit was evaluated but is less suited for granular multi-tenant RBAC and custom conversational UX. |
| **Primary Database** | **PostgreSQL (with SQLite local fallback for test mock)** | **SOURCE REQUIREMENT** | Source documentation specifies a 12-table PostgreSQL relational database. PostgreSQL provides robust time-series indexing, JSONB support for alert metadata, and strict relational integrity. |
| **Database Schema** | **Authoritative 12-Table Schema (`02_DATABASE_SCHEMA.md`)** | **SOURCE REQUIREMENT** | Canonical tables: `users`, `user_profiles`, `meters`, `water_usage_data`, `predictions`, `anomalies`, `alerts`, `consumption_categories`, `recommendations`, `goals`, `feedback`, `chatbot_conversations`. |
| **Frontend Strategy** | **Responsive HTML5 / Vanilla CSS3 / JavaScript (Fetch API)** | **IMPLEMENTATION DECISION** | Delivers a fast, lightweight, dependency-free dashboard with zero complex build-tool overhead (no Node.js/Webpack bloat), ensuring immediate out-of-the-box browser execution with responsive layouts and modern charting. |
| **Machine Learning Stack** | **`scikit-learn` + `pandas` + `numpy`** | **SOURCE REQUIREMENT** | Industry-standard Python scientific stack for time-series feature engineering (lags, rolling statistics, day-of-week encoding), Random Forest / Gradient Boosting regression, and Isolation Forest anomaly detection. |
| **AI / LLM Integration** | **Google GenAI SDK (`google-genai`) with Fallback RAG Engine** | **IMPLEMENTATION DECISION** | Leverages Gemini 2.5 Flash / Pro models for fast conversational inference (<2s target latency) grounded in local user context and `rag_knowledge_base.json`, with a deterministic rule-based fallback when offline. |
| **Testing Strategy** | **`pytest` + Coverage Suite** | **SOURCE REQUIREMENT** | Multi-layer test suite covering unit tests, API integration tests, ML model accuracy checks (MAPE < 15%), and algorithmic fairness/bias audits. Target coverage: >= 80%. |
| **Containerization** | **Docker & Docker Compose** | **SOURCE REQUIREMENT** | Containerized multi-service setup (Flask web app container + PostgreSQL 15 container) ensuring reproducible local development and cloud portability. |

---

## 2. In-Depth Comparative Evaluations

### 2.1 Backend Framework: Flask vs. Streamlit
- **Context:** The project specification states: *"Flask or Streamlit for backend/application"*.
- **Evaluation:**
  - *Streamlit:* Exceptional for rapid 1-day prototyping, but couples the UI state directly to Python script reruns. Implementing multi-page user authentication, granular REST endpoints for external meters, and custom responsive CSS layouts in Streamlit introduces significant technical debt.
  - *Flask:* Provides a production-grade, modular WSGI framework. It allows clean separation between routes (`/api/usage`, `/api/forecast`, `/api/chat`), database models, and view templates. It also facilitates straightforward asynchronous background processing for anomaly detection.
- **Decision:** **Adopt Flask** as the primary application and API server.

### 2.2 Database Management: PostgreSQL vs. SQLite
- **Context:** The project specification mandates PostgreSQL for the authoritative 12-table relational database.
- **Evaluation:**
  - *PostgreSQL (Production & Integration):* Essential for handling concurrent time-series writes from multiple meters, foreign key cascades, and complex date-truncation queries.
  - *SQLite (Local Unit Testing):* An in-memory SQLite configuration will be maintained strictly within `6_TESTING/` to allow rapid automated testing without external database dependencies.
- **Decision:** **PostgreSQL** is the authoritative database target; in-memory SQLite is permitted only for isolated unit test runs.

### 2.3 Conversational AI & LLM Provider
- **Context:** Chatbot response target is `< 2.0 seconds` with zero hallucinations and contextual grounding.
- **Evaluation:**
  - Using open ungrounded LLMs risks inaccurate utility advice.
  - Architecture requires **Retrieval-Augmented Generation (RAG)**: user profile data (e.g., household occupancy, recent water spike data) and verified conservation manuals (`rag_knowledge_base.json`) are injected into structured system prompt templates.
- **Decision:** Integrate the **Google GenAI SDK** with prompt engineering templates and local RAG retrieval, backed by a deterministic rule-based fallback for network resilience.

### 2.4 Deployment & Containerization Strategy
- **Context:** Phase 6 requires containerized deployment.
- **Decision:** Provide a `Dockerfile` for the Flask application and a `docker-compose.yml` that orchestrates both the application service and a persisted PostgreSQL database volume.
