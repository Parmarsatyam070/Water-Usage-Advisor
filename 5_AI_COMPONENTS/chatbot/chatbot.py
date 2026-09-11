"""
Smart Water Usage Advisor - Main Water Advisor Chatbot Facade
Location: 5_AI_COMPONENTS/chatbot/chatbot.py
Phase 3C - Week 6 Implementation

Unifies knowledge retrieval, context construction, personalized recommendations,
safety guardrails, LLM response generation, and multi-turn session management
into a single conversational interface.
"""

import os
import pandas as pd
from typing import Dict, Any, List, Optional

try:
    from .knowledge_base import WaterConservationKnowledgeBase
    from .retrieval import LightweightKnowledgeRetriever, RetrievalResult
    from .context_builder import UserWaterContextBuilder, UserWaterContext
    from .recommendation_engine import PersonalizedRecommendationEngine, WaterRecommendation
    from .prompt_builder import ChatbotPromptBuilder, PromptBundle
    from .response_generator import (
        LLMProviderInterface,
        DeterministicGroundedProvider,
        GeminiLLMProvider,
        ChatbotResponseGenerator,
        ChatbotResponse
    )
    from .safety import ChatbotSafetyGuardrails, SafetyCheckResult
    from .conversation_manager import ConversationSessionManager, ConversationTurn
except (ImportError, ValueError):
    from knowledge_base import WaterConservationKnowledgeBase
    from retrieval import LightweightKnowledgeRetriever, RetrievalResult
    from context_builder import UserWaterContextBuilder, UserWaterContext
    from recommendation_engine import PersonalizedRecommendationEngine, WaterRecommendation
    from prompt_builder import ChatbotPromptBuilder, PromptBundle
    from response_generator import (
        LLMProviderInterface,
        DeterministicGroundedProvider,
        GeminiLLMProvider,
        ChatbotResponseGenerator,
        ChatbotResponse
    )
    from safety import ChatbotSafetyGuardrails, SafetyCheckResult
    from conversation_manager import ConversationSessionManager, ConversationTurn

class WaterAdvisorChatbot:
    """
    Main conversational agent for the Smart Water Usage Advisor.
    Coordinates the full RAG and personalization pipeline.
    """

    def __init__(
        self,
        knowledge_json_path: Optional[str] = None,
        telemetry_df: Optional[pd.DataFrame] = None,
        llm_provider: Optional[LLMProviderInterface] = None,
        enable_gemini_if_available: bool = False
    ):
        # 1. Initialize Curated Knowledge Base
        self.kb = WaterConservationKnowledgeBase(json_path=knowledge_json_path)

        # 2. Initialize Lightweight Retriever
        self.retriever = LightweightKnowledgeRetriever(self.kb)

        # 3. Initialize Context Builder
        self.context_builder = UserWaterContextBuilder(telemetry_df=telemetry_df)

        # 4. Initialize Recommendation Engine
        self.recommendation_engine = PersonalizedRecommendationEngine()

        # 5. Initialize Prompt Builder
        self.prompt_builder = ChatbotPromptBuilder()

        # 6. Initialize Response Generator
        # Default is DeterministicGroundedProvider (reproducible, offline, fast)
        if llm_provider is not None:
            active_provider = llm_provider
        elif enable_gemini_if_available and os.getenv("GEMINI_API_KEY"):
            active_provider = GeminiLLMProvider()
        else:
            active_provider = DeterministicGroundedProvider()

        self.response_generator = ChatbotResponseGenerator(provider=active_provider)

        # 7. Initialize Conversation Session Manager
        self.session_manager = ConversationSessionManager()

    def chat(
        self,
        user_message: str,
        user_id: int = 1,
        meter_id: Optional[int] = None,
        session_id: Optional[str] = None,
        operational_anomalies_df: Optional[pd.DataFrame] = None,
        forecast_output: Optional[Dict[str, Any]] = None,
        custom_goal: Optional[Dict[str, Any]] = None,
        as_of_timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processes a user query end-to-end and returns a structured response dictionary.
        """
        # 1. Step 1: Input Safety Evaluation
        safety_result: SafetyCheckResult = ChatbotSafetyGuardrails.evaluate_input(user_message)
        if not safety_result.is_safe:
            # Immediate safe refusal without leaking system context
            return {
                "answer": safety_result.refusal_message,
                "recommendations": [],
                "evidence": [],
                "water_context": {"user_id": user_id, "status": "query_rejected"},
                "warnings": safety_result.warnings or [],
                "confidence": 1.0,
                "provider_used": "safety_guardrail"
            }

        sanitized_query = safety_result.sanitized_query

        # 2. Step 2: Ensure Valid Session
        active_session_id = session_id or self.session_manager.create_session(user_id=user_id)
        history = self.session_manager.get_history_for_prompt(active_session_id)

        # 3. Step 3: Lightweight Knowledge Retrieval (RAG)
        retrieved_docs = self.retriever.retrieve(sanitized_query, top_k=3)

        # 4. Step 4: Build Structured User Water Context
        user_context = self.context_builder.build_context(
            user_id=user_id,
            meter_id=meter_id,
            operational_anomalies_df=operational_anomalies_df,
            forecast_output=forecast_output,
            custom_goal=custom_goal,
            as_of_timestamp=as_of_timestamp
        )

        # 5. Step 5: Generate Personalized Recommendations
        recommendations = self.recommendation_engine.generate_recommendations(
            context=user_context,
            max_recommendations=3
        )

        # 6. Step 6: Assemble Grounded Prompt Bundle
        prompt_bundle = self.prompt_builder.build_prompt_bundle(
            user_query=sanitized_query,
            context=user_context,
            retrieved_knowledge=retrieved_docs,
            conversation_history=history
        )

        # 7. Step 7: Synthesize Response
        response: ChatbotResponse = self.response_generator.generate_response(
            prompt_bundle=prompt_bundle,
            context=user_context,
            recommendations=recommendations,
            retrieved_knowledge=retrieved_docs
        )

        # Add any safety warnings detected during input
        if safety_result.warnings:
            for w in safety_result.warnings:
                if w not in response.warnings:
                    response.warnings.append(w)

        # 8. Step 8: Record Interaction Turn in Session
        self.session_manager.record_turn(
            session_id=active_session_id,
            user_message=user_message,
            chatbot_response=response.answer,
            user_id=user_id,
            intent_detected=self._detect_intent(sanitized_query),
            confidence_score=response.confidence
        )

        res_dict = response.to_dict()
        res_dict["session_id"] = active_session_id
        return res_dict

    def _detect_intent(self, query: str) -> str:
        """Classifies intent into one of the 7 Phase 1 standardized domain intents."""
        q = query.lower()
        if any(w in q for w in ["leak", "burst", "alert", "running toilet", "night flow"]):
            return "leak/anomaly_question"
        if any(w in q for w in ["bill", "expensive", "cost", "jump", "charge"]):
            return "high_bill_explanation"
        if any(w in q for w in ["forecast", "predict", "next week", "upcoming", "future"]):
            return "prediction_question"
        if any(w in q for w in ["goal", "target", "progress", "budget"]):
            return "goal_tracking"
        if any(w in q for w in ["how much", "usage", "consumption", "breakdown", "used"]):
            return "usage_analysis"
        if any(w in q for w in ["tip", "save", "reduce", "conservation", "shower", "aerator"]):
            return "conservation_tips"
        return "general_water_question"
