# 🗺️ System Architecture, Data Flow & User Journeys
**Directory:** 3_DESIGN/user_flow/  
**Artifacts:** High-Resolution Architecture Diagrams & Process Flows

---

## 1. Generated Diagram Assets
The following visual diagram assets have been generated in this directory:
1. [`system_architecture.png`](file:///c:/Users/singh/Cisco%20Packet%20Tracer%209.0.0/saves/ai%20sustainability%20project/3_DESIGN/user_flow/system_architecture.png) — Multi-tier web UI, Flask REST API, PostgreSQL database, and ML/LLM services.
2. [`data_flow_diagram.png`](file:///c:/Users/singh/Cisco%20Packet%20Tracer%209.0.0/saves/ai%20sustainability%20project/3_DESIGN/user_flow/data_flow_diagram.png) — Smart meter telemetry ingestion, validation, relational storage, and parallel AI analytics streams.
3. [`ai_workflow_diagram.png`](file:///c:/Users/singh/Cisco%20Packet%20Tracer%209.0.0/saves/ai%20sustainability%20project/3_DESIGN/user_flow/ai_workflow_diagram.png) — Feature engineering, time-series forecasting, statistical/ML anomaly detection, and RAG conversational flow.
4. [`user_journey_map.png`](file:///c:/Users/singh/Cisco%20Packet%20Tracer%209.0.0/saves/ai%20sustainability%20project/3_DESIGN/user_flow/user_journey_map.png) — 5-stage user journey from onboarding and daily monitoring to leak alert, AI diagnosis, and verified water savings.

---

## 2. Text Representation of System Architecture
```
+--------------------------------------------------------------------------------+
|                             USER INTERFACE LAYER                               |
|       [ Water Usage Dashboard ]   [ AI Chatbot UI ]   [ Facility Portal ]      |
+--------------------------------------------------------------------------------+
                                       |  (REST API / JSON / HTTP)
                                       v
+--------------------------------------------------------------------------------+
|                       FLASK BACKEND & CONTROLLER LAYER                         |
|   /api/usage  |  /api/forecast  |  /api/anomalies  |  /api/chat  |  /api/goals |
+--------------------------------------------------------------------------------+
             |                                 |                       |
             v                                 v                       v
+------------------------+   +-------------------------+   +---------------------+
|  PostgreSQL Database   |   |   Machine Learning      |   |   AI Chatbot (RAG)  |
|  (12 Authoritative     |   |   - Demand Forecast     |   |   - Google GenAI    |
|   Relational Tables)   |   |     (MAPE < 15%)        |   |   - Prompt Engine   |
|  Users, Meters, Usage  |   |   - Leak Detector (>95%)|   |   - Knowledge Base  |
+------------------------+   +-------------------------+   +---------------------+
```
