# 📋 Project Charter: Smart Water Usage Advisor
**Document ID:** 01_Project_Charter  
**SDG Alignment:** Goal 6 — Clean Water & Sanitation  
**Project Version:** 1.0 (Phase 1 Baseline)

---

## 1. Executive Summary & Vision
The **Smart Water Usage Advisor** is an intelligent, AI-driven sustainability platform designed to democratize water intelligence across residential households, commercial facilities, and municipal utility districts. By transforming raw meter telemetry into actionable predictive analytics, proactive anomaly and leak alerts, and hyper-personalized conservation guidance, the platform directly targets a **20% to 30% reduction** in wasteful water consumption.

---

## 2. Strategic Objectives & Success Metrics
1. **Target Water Savings:** Enable users to reduce non-essential water consumption by 20% to 30% within 90 days of continuous engagement.
2. **Predictive Accuracy:** Achieve Mean Absolute Percentage Error (MAPE) < 15% (accuracy > 85%) on 7-day water demand forecasting.
3. **Anomaly & Leak Detection:** Detect continuous leaks and anomalous surges with > 95% sensitivity within 24 hours of onset.
4. **Chatbot Efficiency & Engagement:** Deliver grounded, contextual conversational advice with latency < 2.0 seconds and user satisfaction >= 4.0 / 5.0.
5. **Software Quality & Coverage:** Maintain >= 80% automated test coverage across unit, integration, and ethics validation suites.

---

## 3. Project Governance & 6-Phase Lifecycle
- **Phase 1: Research & Planning (Weeks 1–2) [Current Phase]**  
  Establish foundational research, system architecture, personas, database design, wireframes, and AI governance.
- **Phase 2: Data Preparation (Week 3)**  
  Synthesize realistic water meter datasets, implement validation pipelines, and initialize relational PostgreSQL schema.
- **Phase 3: AI Model Development (Weeks 4–6)**  
  Train consumption forecasting regressors, build statistical/ML anomaly detectors, and design RAG prompt engineering for the chatbot.
- **Phase 4: Frontend & Integration (Weeks 7–8)**  
  Implement the web dashboard, interactive charts, chatbot conversation window, and connect backend REST APIs.
- **Phase 5: Testing & Ethics (Weeks 9–10)**  
  Execute unit, integration, load, security, and algorithmic fairness audits.
- **Phase 6: Deployment & Documentation (Weeks 11–12)**  
  Containerize via Docker, configure deployment scripts, and publish final presentations and SDG 6 impact reports.

---

## 4. Scope Boundaries
- **In Scope (V1 MVP):** Web-based responsive application, simulated smart meter telemetry, predictive forecasting models, leak detection algorithms, personalized recommendations engine, contextual AI chatbot, role-based user management.
- **Out of Scope (V1 MVP):** Physical IoT hardware provisioning, direct municipal billing gateway integrations, native mobile binaries (iOS/Android), real-time acoustic pipeline hardware, multilingual natural language support.
