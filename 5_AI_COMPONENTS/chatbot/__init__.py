"""
Smart Water Usage Advisor - AI Water Conservation Chatbot Package
Location: 5_AI_COMPONENTS/chatbot/__init__.py
Phase 3C - Week 6 Implementation
"""

from .knowledge_base import WaterConservationKnowledgeBase, KnowledgeEntry
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
from .chatbot import WaterAdvisorChatbot

__all__ = [
    "WaterConservationKnowledgeBase",
    "KnowledgeEntry",
    "LightweightKnowledgeRetriever",
    "RetrievalResult",
    "UserWaterContextBuilder",
    "UserWaterContext",
    "PersonalizedRecommendationEngine",
    "WaterRecommendation",
    "ChatbotPromptBuilder",
    "PromptBundle",
    "LLMProviderInterface",
    "DeterministicGroundedProvider",
    "GeminiLLMProvider",
    "ChatbotResponseGenerator",
    "ChatbotResponse",
    "ChatbotSafetyGuardrails",
    "SafetyCheckResult",
    "ConversationSessionManager",
    "ConversationTurn",
    "WaterAdvisorChatbot"
]
