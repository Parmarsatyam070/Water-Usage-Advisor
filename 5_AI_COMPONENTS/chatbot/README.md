# AI Water Conservation Chatbot Component

**Module**: `5_AI_COMPONENTS/chatbot/`  
**Phase**: 3C — AI Model Development (Week 6)  
**Project**: Smart Water Usage Advisor (UN SDG 6: Clean Water & Sanitation)  

---

## 1. Architectural Overview

The **Smart Water Usage Advisor Chatbot** provides an evidence-grounded, empathetic, and personalized conversational assistant for residential homeowners, commercial facility managers, and municipalities.

Instead of generating generic conversational text or ungrounded claims, the chatbot combines five distinct sources of operational data and domain knowledge:

```
+---------------------+     +--------------------+     +---------------------+
| User Profile & Goal |     | 90-Day Telemetry   |     | Phase 3A Forecasts  |
| (Property, Garden)  |     | (Baseline, Trend)  |     | (7-Day Projection)  |
+----------+----------+     +---------+----------+     +----------+----------+
           |                          |                           |
           +--------------------+     |     +---------------------+
                                |     |     |
                                v     v     v
                  +-------------------------------+
                  |  UserWaterContextBuilder      |
                  +---------------+---------------+
                                  |
                                  v
+-----------------------+   +-----+-------------------------+   +----------------------+
| Curated Knowledge Base|-->| Lightweight Retriever (RAG)   |-->| Recommendation Engine|
| (16 Evidence Entries) |   +-----+-------------------------+   | (Context-Driven Recs)|
+-----------------------+         |                             +----------+-----------+
                                  |                                        |
                                  v                                        v
                    +-------------+----------------------------------------+
                    | ChatbotPromptBuilder (Persona, Grounding, Safety)    |
                    +-----------------------------+------------------------+
                                                  |
                                                  v
                    +-----------------------------+------------------------+
                    | LLM Provider Interface                               |
                    | * Default: DeterministicGroundedProvider (Offline)   |
                    | * Optional: GeminiLLMProvider (via GEMINI_API_KEY)   |
                    +-----------------------------+------------------------+
                                                  |
                                                  v
                    +-----------------------------+------------------------+
                    | Safety & Factuality Guardrails                       |
                    | (Injection defense, secret scrub, plumbing safety)   |
                    +-----------------------------+------------------------+
                                                  |
                                                  v
                    +-----------------------------+------------------------+
                    | Structured ChatbotResponse JSON                      |
                    +------------------------------------------------------+
```

---

## 2. Core Modules

| File | Purpose | Key Classes / Functions |
| :--- | :--- | :--- |
| [`knowledge_base.py`](file:///c:/Users/singh/Cisco%20Packet%20Tracer%209.0.0/saves/ai%20sustainability%20project/5_AI_COMPONENTS/chatbot/knowledge_base.py) | 16 structured, practical water-saving entries with daily liter savings estimates. | `WaterConservationKnowledgeBase`, `KnowledgeEntry` |
| [`retrieval.py`](file:///c:/Users/singh/Cisco%20Packet%20Tracer%209.0.0/saves/ai%20sustainability%20project/5_AI_COMPONENTS/chatbot/retrieval.py) | Deterministic keyword + BM25 token-matching retrieval engine with identifiable source IDs. | `LightweightKnowledgeRetriever`, `RetrievalResult` |
| [`context_builder.py`](file:///c:/Users/singh/Cisco%20Packet%20Tracer%209.0.0/saves/ai%20sustainability%20project/5_AI_COMPONENTS/chatbot/context_builder.py) | Aggregates user profile, telemetry, Phase 3A forecasts, Phase 3B anomalies, and active goals. | `UserWaterContextBuilder`, `UserWaterContext` |
| [`recommendation_engine.py`](file:///c:/Users/singh/Cisco%20Packet%20Tracer%209.0.0/saves/ai%20sustainability%20project/5_AI_COMPONENTS/chatbot/recommendation_engine.py) | Generates prioritized, context-driven recommendations tailored to actual measured usage. | `PersonalizedRecommendationEngine`, `WaterRecommendation` |
| [`prompt_builder.py`](file:///c:/Users/singh/Cisco%20Packet%20Tracer%209.0.0/saves/ai%20sustainability%20project/5_AI_COMPONENTS/chatbot/prompt_builder.py) | Assembles grounded system instructions, context summaries, knowledge snippets, and history. | `ChatbotPromptBuilder`, `PromptBundle` |
| [`response_generator.py`](file:///c:/Users/singh/Cisco%20Packet%20Tracer%209.0.0/saves/ai%20sustainability%20project/5_AI_COMPONENTS/chatbot/response_generator.py) | Extensible LLM abstraction with default deterministic provider and optional Gemini provider. | `LLMProviderInterface`, `DeterministicGroundedProvider`, `GeminiLLMProvider`, `ChatbotResponseGenerator` |
| [`safety.py`](file:///c:/Users/singh/Cisco%20Packet%20Tracer%209.0.0/saves/ai%20sustainability%20project/5_AI_COMPONENTS/chatbot/safety.py) | Guardrails for prompt injection, credential scrubbing, factuality verification, and plumbing safety. | `ChatbotSafetyGuardrails`, `SafetyCheckResult` |
| [`conversation_manager.py`](file:///c:/Users/singh/Cisco%20Packet%20Tracer%209.0.0/saves/ai%20sustainability%20project/5_AI_COMPONENTS/chatbot/conversation_manager.py) | Session state tracking and schema persistence to the `chatbot_conversations` PostgreSQL table. | `ConversationSessionManager`, `ConversationTurn` |
| [`chatbot.py`](file:///c:/Users/singh/Cisco%20Packet%20Tracer%209.0.0/saves/ai%20sustainability%20project/5_AI_COMPONENTS/chatbot/chatbot.py) | Unified facade coordinating all components through a simple `.chat()` interface. | `WaterAdvisorChatbot` |

---

## 3. LLM Provider Architecture

> **IMPORTANT PROVIDER DESIGN**:  
> "Gemini is an optional LLM provider. The Phase 3C chatbot remains fully testable and demonstrable using the deterministic grounded provider without an external API."

- **`DeterministicGroundedProvider` (Default Provider)**:
  - Synthesizes natural language answers directly from the assembled context, active alerts, forecast projections, and retrieved knowledge.
  - Deterministic, fast (<50ms), and reproducible for automated test suites.
  - Requires **zero external network access** and **zero API keys**.
  - *Note*: The deterministic provider guarantees reproducibility for designated test scenarios, not a universal guarantee of correctness.
- **`GeminiLLMProvider` (Optional Provider Only)**:
  - Dynamically activated only when `GEMINI_API_KEY` is present in the environment.
  - Safely and transparently falls back to `DeterministicGroundedProvider` if the key is missing, unauthorized, or encounters a network timeout.
  - Secrets and credentials are never hard-coded, logged, or exposed in output responses.

---

## 4. Structured Output Format

All chatbot responses strictly adhere to the structured response schema:

```json
{
  "answer": "ACTIVE LEAK DETECTED: Your meter recorded continuous nocturnal flow of 16.5 L/hr...",
  "recommendations": [
    {
      "title": "Inspect Toilet Cisterns for Silent Leaks",
      "description": "Perform a 15-minute food-coloring test in your toilet cistern...",
      "estimated_savings_liters": 396.0,
      "estimated_savings_cost": 1.39,
      "priority": "high",
      "difficulty": "easy",
      "category": "plumbing",
      "action_type": "immediate_action"
    }
  ],
  "evidence": [
    {
      "entry_id": "KB-001",
      "title": "Diagnosing and Fixing Toilet Flapper Valve Leaks",
      "category": "plumbing_troubleshooting",
      "snippet": "A leaking toilet flapper is the single most common cause...",
      "relevance_score": 1.0,
      "savings_estimate_liters_day": 350.0,
      "topic": "toilet_leaks"
    }
  ],
  "water_context": {
    "user_id": 1,
    "meter_id": 1,
    "property_type": "house",
    "household_size": 4,
    "today_consumption_liters": 422.8,
    "weekly_avg_daily_liters": 351.6,
    "baseline_daily_liters": 377.6,
    "recent_trend": "increasing",
    "has_active_anomaly": true,
    "anomaly_type": "leak",
    "anomaly_severity": "high",
    "forecast_available": false,
    "has_active_goal": true
  },
  "warnings": [],
  "confidence": 0.95,
  "provider_used": "deterministic_grounded",
  "session_id": "sess-1-3edb212a"
}
```

---

## 5. Usage Example

```python
from chatbot import WaterAdvisorChatbot

# Initialize chatbot with default deterministic provider
bot = WaterAdvisorChatbot()

# Submit user query
response = bot.chat(
    user_message="Why is my water usage so high today?",
    user_id=1,
    meter_id=1
)

print(response["answer"])
for rec in response["recommendations"]:
    print(f"- {rec['title']} (Saves: {rec['estimated_savings_liters']} L/day)")
```
