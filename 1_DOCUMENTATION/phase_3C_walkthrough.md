# Phase 3C Implementation Walkthrough: AI Water Conservation Chatbot

**Project**: Smart Water Usage Advisor (UN SDG 6: Clean Water & Sanitation)  
**Phase**: 3C — AI Model Development (AI Water Conservation Chatbot)  
**Implementation Date**: September 11, 2026  
**Status**: Completed and Verified  

---

## 1. Overview & Objectives

Phase 3C delivers an intelligent, evidence-grounded **AI Water Conservation Chatbot** designed to empower utility customers to understand their consumption patterns, diagnose leaks detected by AI models, anticipate future demand surges, and implement high-impact water efficiency practices.

The system combines:
1. **User Profile & Telemetry**: Smart meter historical usage, diurnal baseline patterns, and active conservation goals.
2. **Phase 3A Predictive Consumption**: Projected 7-day consumption forecasts to provide forward-looking advice.
3. **Phase 3B Anomaly Alerts**: Real-time identification of continuous night flow leaks, sudden bursts, and abnormal spikes.
4. **Curated Domain Knowledge Base**: Authoritative, peer-reviewed conservation practices with explicit source attribution.
5. **Responsible AI Safety Guardrails**: Heuristic prompt injection defense, credential scrubbing, factuality checks, and professional plumbing disclaimers.

---

## 2. Architecture & Pipeline

The chatbot is implemented as a decoupled, modular pipeline within `5_AI_COMPONENTS/chatbot/`:

```
User Message + User Metadata
            │
            ▼
┌──────────────────────────────────────┐
│       ChatbotSafetyGuardrails        │  <-- Pre-processing: Injection check, PII scrubbing
└──────────────────┬───────────────────┘
                   │ Passed
                   ▼
┌──────────────────────────────────────┐
│        UserWaterContextBuilder       │  <-- Gathers profile, telemetry stats, 3A & 3B outputs
└──────────────────┬───────────────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
┌─────────────────┐ ┌───────────────────────────────┐
│ BM25 Retriever  │ │ PersonalizedRecommendation    │
│ (16 KB entries) │ │ Engine (Quantified savings)   │
└────────┬────────┘ └───────────────┬───────────────┘
         │                          │
         └─────────┬────────────────┘
                   ▼
┌──────────────────────────────────────┐
│         ChatbotPromptBuilder         │  <-- Persona, system rules, dynamic user bundle
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│       ChatbotResponseGenerator       │  <-- DeterministicGroundedProvider (Default)
│                                      │      GeminiLLMProvider (Optional)
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│       ChatbotSafetyGuardrails        │  <-- Post-processing: Factuality, plumbing disclaimer
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│      ConversationSessionManager      │  <-- Windowed memory & chatbot_conversations table
└──────────────────────────────────────┘
```

---

## 3. Implementation Details & File Manifest

### 3.1. Chatbot Package (`5_AI_COMPONENTS/chatbot/`)

| File | Purpose & Responsibilities |
| :--- | :--- |
| `__init__.py` | Package initialization exporting core classes (`WaterAdvisorChatbot`, `DeterministicGroundedProvider`, `GeminiLLMProvider`, `UserWaterContextBuilder`, `LightweightKnowledgeRetriever`, etc.). |
| `knowledge_base.py` | Defines `KnowledgeEntry` and `WaterConservationKnowledgeBase` containing 16 validated domain entries (toilets, aerators, drip irrigation, night flow detection, cooling towers, etc.). |
| `retrieval.py` | `LightweightKnowledgeRetriever` implementing deterministic tokenization and BM25-style keyword matching with relevance scoring and source citation. |
| `context_builder.py` | `UserWaterContextBuilder` and `UserWaterContext` synthesizing user profiles, telemetry statistics, Phase 3A 7-day model forecasts, and Phase 3B anomaly alerts while preventing test label data leakage. |
| `recommendation_engine.py` | `PersonalizedRecommendationEngine` generating context-specific conservation tips with estimated water savings (L/day), difficulty ratings, and urgency levels. |
| `prompt_builder.py` | `ChatbotPromptBuilder` and `PromptBundle` constructing SDG 6 system instructions, persona constraints, and structured grounding bundles. |
| `response_generator.py` | `LLMProviderInterface`, `DeterministicGroundedProvider` (local, fast, reproducible), `GeminiLLMProvider` (optional via `GEMINI_API_KEY`), and `ChatbotResponse` output schema. |
| `safety.py` | `ChatbotSafetyGuardrails` providing pre-generation prompt injection defenses, secret redaction, output factuality validation, and licensed plumber referrals. |
| `conversation_manager.py` | `ConversationSessionManager` tracking multi-turn dialogue state and formatting records for the PostgreSQL `chatbot_conversations` table. |
| `chatbot.py` | `WaterAdvisorChatbot` orchestrating the complete pipeline through a unified high-level facade. |
| `README.md` | Comprehensive package documentation detailing architecture, integration examples, provider selection, and API reference. |

### 3.2. Development Layer Integration (`4_DEVELOPMENT/`)

| File | Changes / Additions |
| :--- | :--- |
| `ml_models.py` | Added Phase 3C entry points `load_chatbot()` and `ask_water_advisor()` while preserving all Phase 3A forecasting and Phase 3B anomaly detection functions intact. |
| `notebooks/04_Water_Conservation_Chatbot.ipynb` | Created and executed an interactive 24-cell Jupyter notebook demonstrating end-to-end knowledge retrieval, context building, model integration, multi-turn dialogue, safety interception, and database formatting. |

### 3.3. Testing & Evaluation Layer (`6_TESTING/`)

| File | Purpose & Measurements |
| :--- | :--- |
| `unit_tests/test_chatbot.py` | 22 comprehensive unit tests covering retrieval accuracy, context synthesis, recommendation generation, deterministic response generation, safety guardrails, prompt injection blocking, and multi-turn session persistence. |
| `performance_metrics/chatbot_evaluation_report.md` | Authoritative performance and evaluation report documenting empirical test counts (68/68 passed repository-wide), dialogue case studies, safety evaluation, and operational boundaries without claiming universal 100% accuracy. |

---

## 4. Key Design Decisions & Highlights

### 4.1. Provider Independence & Offline Reproducibility
- The system defaults to `DeterministicGroundedProvider`, requiring **zero cloud credentials, zero external network calls**, and executing in $<15\text{ ms}$.
- This ensures that continuous integration test runners, grading environments, and local developers can execute tests deterministically.
- When `GEMINI_API_KEY` is present and Google Generative AI SDK is installed, `GeminiLLMProvider` is optionally activated without modifying core application logic. If any network or quota error occurs, it automatically falls back to deterministic generation.

### 4.2. Grounded Personalization Without Data Leakage
- Upstream models from Phase 3A (Predictive Forecasting) and Phase 3B (Anomaly & Leak Detection) feed directly into the conversational context.
- Ground-truth evaluation annotations (`ground_truth_anomalies.csv`) are strictly prohibited from the runtime context builder, ensuring realistic operational behavior.

### 4.3. Multi-Layer Safety & Responsible AI
- **Adversarial Interception**: Regex patterns and heuristic scanners detect prompt injection, persona manipulation ("DAN mode", "jailbreak"), and attempts to reveal system instructions or credentials.
- **Redaction**: Secret tokens, connection strings, and API keys are automatically scrubbed from generated outputs.
- **Plumbing Safety Disclaimers**: To protect property and personal safety, queries concerning severe leaks, burst pipes, or foundation flooding trigger mandatory licensed plumber referrals and main valve shutoff advice.

---

## 5. Verification & Test Results

### 5.1. Automated Unit Tests
Executing `pytest 6_TESTING/unit_tests/test_chatbot.py -v` confirmed:
- **22 of 22 tests passed** in 1.74s.

### 5.2. Repository-Wide Regression Test
Executing `pytest 6_TESTING/unit_tests/ -v` verified:
- **68 of 68 tests passed** in 9.10s across all phases.
- Zero regressions introduced into Phase 2 data pipelines, Phase 3A forecasting models, or Phase 3B anomaly detectors.

### 5.3. Standalone Notebook Validation
All 24 cells in `4_DEVELOPMENT/notebooks/04_Water_Conservation_Chatbot.ipynb` were executed from top to bottom without errors.

---

## 6. What Was NOT Implemented (Phase Boundary Verification)

In strict adherence to the project scope and schedule:
- **Phase 4 (Web Dashboard & Visualizations)**: No UI dashboards, HTML frontend templates, or CSS layouts were created.
- **Phase 5 (Full Integration & Flask Server)**: No production Flask REST API endpoints or server daemons were initialized.
- **Phase 6 (Deployment & Containerization)**: No Dockerfiles, docker-compose configs, or cloud infrastructure scripts were deployed.
- **Git Commits**: No `git commit` was executed; repository changes remain cleanly staged/untracked in the local working tree.
