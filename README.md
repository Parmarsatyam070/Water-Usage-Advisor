# 💧 Smart Water Usage Advisor
**AI + Sustainability Project | UN Sustainable Development Goal 6 (Clean Water & Sanitation)**

[![SDG 6](https://img.shields.io/badge/SDG-6:_Clean_Water_%26_Sanitation-00AED9.svg)](https://sdgs.un.org/goals/goal6)
[![Project Status: Phase 1 Active](https://img.shields.io/badge/Status-Phase_1:_Research_%26_Planning-orange.svg)](#six-phase-development-roadmap)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 📖 Project Overview

### The Problem
Water scarcity and inefficient consumption affect communities and municipalities worldwide. Millions of liters are lost annually through silent plumbing leaks, unoptimized irrigation, and lack of real-time visibility into usage behaviors. Most consumers and facility operators only see water consumption retrospectively when receiving a monthly utility bill—long after costly leaks or wasteful habits occur.

### The Solution
The **Smart Water Usage Advisor** is a web-based, AI-powered decision-support system designed to empower households, facility managers, and municipalities. It ingests simulated and smart meter telemetry to:
1. Provide intuitive real-time consumption dashboards with category breakdowns.
2. Deliver early **leak and anomaly detection** (>95% target detection rate) before catastrophic water loss occurs.
3. Generate **predictive consumption forecasts** using machine learning (target MAPE <15%).
4. Offer an **AI Water Conservation Chatbot** providing hyper-personalized, context-grounded conservation tips and bill explanations (<2s response time).
5. Support a 20–30% measurable reduction in water consumption in alignment with UN SDG 6.

---

## 🎯 Target Users

1. **Households / Residential Users:** Everyday homeowners and renters seeking to lower utility bills, detect hidden leaks, and understand water footprint.
2. **Institutions & Commercial Facility Managers:** Operators of university campuses, residential complexes, and office buildings managing multi-meter plumbing systems.
3. **Municipalities & Water Utilities:** District planners monitoring localized demand patterns, conservation goal progress, and distribution efficiency.

---

## 🚀 Key Features (Scope)

| Feature | Description | Target Performance |
| :--- | :--- | :--- |
| **Water Usage Dashboard** | Interactive telemetry tracking today's volume, weekly/monthly trends, and category breakdown. | Responsive UI, live aggregation |
| **AI Conservation Chatbot** | Conversational advisor grounded in user profile data, fixtures, and local conservation best practices. | Latency <2s, context-aware |
| **Predictive Analytics** | Time-series forecasting for upcoming 7–30 day water requirements. | Accuracy >85% / MAPE <15% |
| **Anomaly & Leak Detection** | Multi-tiered statistical & ML detection flags continuous night-flow leaks and abnormal consumption spikes. | Sensitivity >95% |
| **Personalized Recommendations** | Heuristic & similarity-based conservation actions with estimated volume and cost savings. | 20–30% water-saving potential |
| **User & Profile Management** | Multi-role support, occupancy modeling, fixture inventories, and conservation goal tracking. | Role-based data separation |
| **Responsible AI & Security** | Differential privacy, non-judgmental prompt framing, explainable model predictions, and audit logs. | Bias-audited, OWASP compliant |

> **V1 Scope Note:** Physical IoT hardware installation, direct municipal utility billing integration, and native mobile apps are out-of-scope for the MVP. The system utilizes simulated smart-meter telemetry.

---

## 🛠️ Technology Stack

- **Backend / Web Framework:** Python 3.10+, Flask REST API (Modular application architecture)
- **Database:** PostgreSQL (Authoritative 12-table relational schema)
- **Machine Learning:** `scikit-learn`, `pandas`, `numpy`, `statsmodels`
- **AI & Natural Language Processing:** Google GenAI / LLM API with Retrieval-Augmented Generation (RAG) knowledge base
- **Frontend:** Responsive HTML5, Vanilla CSS3 (custom sustainable design tokens), JavaScript (Fetch API & Charting)
- **Containerization & Deployment:** Docker, Docker Compose
- **Testing & Quality:** `pytest`, `flake8`, fairness & bias auditing test suites

---

## 🗺️ Six-Phase Development Roadmap

| Phase | Title | Duration | Focus / Key Deliverables | Status |
| :---: | :--- | :---: | :--- | :---: |
| **Phase 1** | **Research & Planning** | Weeks 1–2 | Problem definition, user research, personas, system architecture, wireframes, AI planning, database design docs. | **IN PROGRESS (Current)** |
| **Phase 2** | **Data Preparation** | Week 3 | Realistic synthetic meter telemetry generation, cleaning pipelines, feature engineering, PostgreSQL schema initialization. | Planned |
| **Phase 3** | **AI Model Development** | Weeks 4–6 | Predictive forecasting, anomaly/leak detector, recommendation engine, chatbot prompt engineering & RAG evaluation. | Planned |
| **Phase 4** | **Frontend & Integration** | Weeks 7–8 | Interactive dashboard UI, charts, chatbot conversation window, recommendation cards, REST API integration. | Planned |
| **Phase 5** | **Testing & Ethics** | Weeks 9–10 | Unit & integration tests, user validation, performance load tests, responsible AI & bias mitigation audits. | Planned |
| **Phase 6** | **Deployment & Documentation** | Weeks 11–12 | Docker containerization, cloud deployment configurations, monitoring, final presentation, impact report. | Planned |

---

## 📍 Current Phase 1 Status

Phase 1 (Research & Planning) establishes the core scientific and architectural foundation:
- [x] Workspace cleaned and canonical directory tree initialized.
- [x] Problem Statement & SDG 6 Alignment formulated (`1_DOCUMENTATION/02_Problem_Statement.md`).
- [x] User Research Framework & 3 Core Personas drafted (`1_DOCUMENTATION/03_User_Research.md`, `3_DESIGN/personas/`).
- [x] Peer-reviewed Literature Review template established (`1_DOCUMENTATION/04_Literature_Review.md`).
- [x] Responsible AI & Ethics Framework documented (`1_DOCUMENTATION/05_Responsible_AI_Framework.md`).
- [x] Technical Architecture, Data Flows, and User Journeys designed (`3_DESIGN/user_flow/`).
- [x] Authoritative 12-Table Database Schema documented (`3_DESIGN/design_documents/Database_Schema.md`).
- [x] UI/UX Wireframes for Dashboard, Chatbot, and Recommendations designed (`3_DESIGN/wireframes/`).
- [x] AI Chatbot conversation flows, prompt templates, and RAG knowledge base structured (`5_AI_COMPONENTS/`).
- [x] Phase 1 Verification Test Suite established (`6_TESTING/test_cases.md`).

---

## 🏁 How to Start the Project (Development Setup)

### Prerequisites
- Python 3.10+
- Git
- PostgreSQL 14+ (for Phase 2+)

### Initial Setup
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd smart-water-advisor
   ```

2. **Activate the Virtual Environment:**
   - On Windows (PowerShell):
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - On Linux / macOS:
     ```bash
     source .venv/bin/activate
     ```

3. **Configure Environment Variables:**
   ```bash
   cp .env.example .env
   # Edit .env with local development credentials (never commit .env to git)
   ```

4. **Review Phase 1 Documentation:**
   Explore [`1_DOCUMENTATION/`](1_DOCUMENTATION/) and [`3_DESIGN/`](3_DESIGN/) to review project architecture, database schemas, and AI designs before code execution begins in Phase 2.

---

## 📄 License & Contribution
Distributed under the MIT License. See [`LICENSE`](LICENSE) and [`CONTRIBUTING.md`](CONTRIBUTING.md) for contribution guidelines.
