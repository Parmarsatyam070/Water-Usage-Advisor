"""
Smart Water Usage Advisor - Provider-Independent Response Generator
Location: 5_AI_COMPONENTS/chatbot/response_generator.py
Phase 3C - Week 6 Implementation

Provides an extensible, provider-independent LLM response generator:
- LLMProviderInterface: abstract protocol for response synthesis
- DeterministicGroundedProvider: default, reproducible, offline provider
- GeminiLLMProvider: optional cloud provider (falls back safely if unconfigured)
- ChatbotResponse: structured JSON schema output
"""

import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

try:
    from .context_builder import UserWaterContext
    from .recommendation_engine import WaterRecommendation
    from .retrieval import RetrievalResult
    from .prompt_builder import PromptBundle
    from .safety import ChatbotSafetyGuardrails
except (ImportError, ValueError):
    from context_builder import UserWaterContext
    from recommendation_engine import WaterRecommendation
    from retrieval import RetrievalResult
    from prompt_builder import PromptBundle
    from safety import ChatbotSafetyGuardrails

@dataclass
class ChatbotResponse:
    """Structured, user-facing chatbot response payload."""
    answer: str
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    water_context: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    confidence: float = 0.95
    provider_used: str = "deterministic_grounded"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LLMProviderInterface(ABC):
    """Abstract interface for LLM response generation providers."""

    @abstractmethod
    def generate(
        self,
        prompt_bundle: PromptBundle,
        context: UserWaterContext,
        recommendations: List[WaterRecommendation],
        retrieved_knowledge: List[RetrievalResult]
    ) -> str:
        """Synthesizes natural language answer from prompt bundle and context."""
        pass


class DeterministicGroundedProvider(LLMProviderInterface):
    """
    Default grounded response generator.
    Synthesizes natural language responses directly from operational telemetry,
    active alerts, forecast numbers, and retrieved knowledge without external API calls.
    Deterministic, fast (<50ms), and reproducible for automated test suites.
    """

    def generate(
        self,
        prompt_bundle: PromptBundle,
        context: UserWaterContext,
        recommendations: List[WaterRecommendation],
        retrieved_knowledge: List[RetrievalResult]
    ) -> str:
        query = prompt_bundle.user_query.lower()
        
        # 1. Handle Insufficient Data Case
        if not context.has_sufficient_data:
            return (
                f"Hello {context.first_name}. Your smart meter ({context.meter_profile_name}) currently has "
                f"fewer than 24 hours of recorded telemetry. As a result, baseline comparisons and personalized "
                f"analytics cannot yet be reliably computed. Please allow your meter to operate for 3 to 7 days "
                f"to establish your baseline profile."
            )

        # 2. Case: Leak / Anomaly Inquiries
        if any(w in query for w in ["leak", "burst", "alert", "running", "overnight", "night flow"]):
            if context.has_active_anomaly:
                if context.anomaly_type == "surge":
                    return (
                        f"CRITICAL ALERT: Your smart meter detected an extreme consumption surge of "
                        f"{context.anomaly_flow_rate:.0f} L/hr (approximately {context.estimated_excess_liters:.0f} L above expected baseline). "
                        f"This signature strongly indicates a ruptured pipe or major line failure. "
                        f"Action: Immediately shut off your main water supply valve and contact a licensed professional plumber."
                    )
                elif context.anomaly_type == "leak":
                    return (
                        f"ACTIVE LEAK DETECTED: Your meter recorded continuous nocturnal flow of "
                        f"{context.anomaly_flow_rate:.1f} L/hr during deep-sleep hours (normal night flow is {context.baseline_daily_liters/24:.1f} L/hr). "
                        f"This persistent non-zero flow is the classic signature of a leaking toilet flapper or dripping fixture. "
                        f"Diagnosis: We recommend placing 5 drops of food coloring in your toilet cistern; if color appears in the bowl without flushing within 15 minutes, replace the flapper."
                    )
                else:
                    return (
                        f"ACTIVE ALERT: An unusual {context.anomaly_type} event was detected on your meter "
                        f"({context.anomaly_flow_rate:.1f} L/hr, severity: {context.anomaly_severity}). "
                        f"Explanation: {context.anomaly_explanation}"
                    )
            else:
                return (
                    f"Good news, {context.first_name}. No active leaks or anomalies are currently detected on your meter. "
                    f"Your nocturnal flow drops to normal baseline levels during sleep hours, and your recent daily usage "
                    f"({context.today_consumption_liters:.1f} L) is within expected operating limits."
                )

        # 3. Case: High Bill / Increased Consumption Inquiries
        if any(w in query for w in ["high bill", "bill jump", "expensive", "why is my usage high", "why is my bill"]):
            if context.has_active_anomaly:
                return (
                    f"Your recent usage is elevated primarily due to an active {context.anomaly_type} anomaly detected on your meter. "
                    f"The meter registered continuous flow of {context.anomaly_flow_rate:.1f} L/hr, resulting in an estimated "
                    f"{context.estimated_excess_liters:.0f} liters of excess consumption. Resolving this issue will restore your bill to normal levels."
                )
            elif context.recent_trend == "increasing":
                top_cat = context.primary_consumption_category
                return (
                    f"Your water consumption is currently trending {context.percent_change_vs_baseline:+.1f}% higher than your 30-day baseline "
                    f"({context.today_consumption_liters:.1f} L vs. baseline of {context.baseline_daily_liters:.1f} L/day). "
                    f"The largest share of consumption is in {top_cat} (~{context.categories_breakdown.get(top_cat, 0):.0f} L). "
                    f"Implementing targeted reductions in this area will help lower your upcoming utility bill."
                )
            else:
                return (
                    f"Your recent consumption of {context.today_consumption_liters:.1f} L is stable compared to your 30-day baseline "
                    f"of {context.baseline_daily_liters:.1f} L/day ({context.percent_change_vs_baseline:+.1f}% variation). "
                    f"If your bill increased, check whether municipal water rates or seasonal sewerage charges changed recently."
                )

        # 4. Case: Predictive Forecast Inquiries
        if any(w in query for w in ["forecast", "predict", "next week", "upcoming", "future", "tomorrow"]):
            if context.forecast_available:
                warning_note = (
                    f" Notice: A projected peak of {context.predicted_peak_volume_liters:.0f} L is anticipated on {context.predicted_peak_day}. "
                    f"Consider shifting non-essential outdoor watering away from this day."
                    if context.forecast_spike_warning else ""
                )
                return (
                    f"According to our Phase 3A predictive forecasting model, your household is projected to consume "
                    f"{context.predicted_7day_total_liters:.0f} liters over the next 7 days (daily average: {context.predicted_daily_average_liters:.1f} L/day). "
                    f"Your expected peak day is {context.predicted_peak_day} with approximately {context.predicted_peak_volume_liters:.0f} liters.{warning_note}"
                )
            else:
                return (
                    f"Predictive forecasts are currently being generated for your meter. Based on your historical 7-day average, "
                    f"your expected daily consumption is approximately {context.weekly_avg_daily_liters:.1f} L/day."
                )

        # 5. Case: Goal Tracking Inquiries
        if any(w in query for w in ["goal", "target", "progress", "budget", "track"]):
            if context.has_active_goal:
                gap = 100.0 - context.goal_progress_pct
                return (
                    f"You have an active conservation goal of a {context.goal_target_value:.0f}{context.goal_target_unit} reduction. "
                    f"Your current progress is {context.goal_progress_pct:.1f}% towards this target. "
                    f"With a {gap:.1f}% remaining gap, maintaining your 7-day average of {context.weekly_avg_daily_liters:.1f} L/day "
                    f"and applying targeted shower or tap aerators will help you meet your target this billing cycle."
                )
            else:
                return (
                    f"You do not currently have an active conservation goal set. Setting a realistic 15% to 20% reduction goal "
                    f"would target approximately {context.baseline_daily_liters * 0.82:.0f} L/day based on your current baseline."
                )

        # 6. Case: Usage Breakdown / Current Status
        if any(w in query for w in ["how much", "usage", "breakdown", "consumption", "yesterday", "today", "use"]):
            cats = ", ".join([f"{k}: {v:.0f} L" for k, v in context.categories_breakdown.items()])
            return (
                f"Your recent recorded consumption is {context.today_consumption_liters:.1f} liters (7-day average: {context.weekly_avg_daily_liters:.1f} L/day). "
                f"Estimated category breakdown: {cats}. Your largest consuming category is {context.primary_consumption_category}."
            )

        # 7. Default: General Conservation Advice Grounded in Retrieved Snippets
        if retrieved_knowledge:
            top_kb = retrieved_knowledge[0]
            sec_kb = retrieved_knowledge[1] if len(retrieved_knowledge) > 1 else None
            sec_note = f" Additionally, {sec_kb.title.lower()}: {sec_kb.snippet}" if sec_kb else ""
            return (
                f"Regarding your question: {top_kb.title} — {top_kb.snippet}{sec_note} "
                f"For your {context.property_type} ({context.household_size} occupants), adopting this practice can save approximately "
                f"{top_kb.savings_estimate_liters_day:.0f} liters per day."
            )

        # Fallback default
        return (
            f"Hello {context.first_name}. Your smart meter shows a recent daily consumption of {context.today_consumption_liters:.1f} L "
            f"(weekly average: {context.weekly_avg_daily_liters:.1f} L/day). "
            f"To save water, consider checking fixtures for silent leaks and installing low-flow aerators on taps and showerheads."
        )


class GeminiLLMProvider(LLMProviderInterface):
    """
    Optional Gemini API provider.
    Reads GEMINI_API_KEY from environment.
    Falls back safely to DeterministicGroundedProvider if unconfigured or on any API/network failure.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.fallback_provider = DeterministicGroundedProvider()
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        if not self.api_key:
            return
        try:
            # Check for google-genai SDK
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
        except Exception:
            self.client = None

    def generate(
        self,
        prompt_bundle: PromptBundle,
        context: UserWaterContext,
        recommendations: List[WaterRecommendation],
        retrieved_knowledge: List[RetrievalResult]
    ) -> str:
        # Fallback immediately if client not initialized
        if not self.client or not self.api_key:
            return self.fallback_provider.generate(
                prompt_bundle, context, recommendations, retrieved_knowledge
            )

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt_bundle.full_prompt
            )
            if response and response.text:
                return response.text.strip()
            return self.fallback_provider.generate(
                prompt_bundle, context, recommendations, retrieved_knowledge
            )
        except Exception as e:
            # Safe silent fallback without leaking credentials
            return self.fallback_provider.generate(
                prompt_bundle, context, recommendations, retrieved_knowledge
            )


class ChatbotResponseGenerator:
    """
    Orchestrates response generation, safety evaluation, and structured JSON output creation.
    """

    def __init__(self, provider: Optional[LLMProviderInterface] = None):
        # Default to DeterministicGroundedProvider for reproducible offline execution
        self.provider = provider or DeterministicGroundedProvider()

    def generate_response(
        self,
        prompt_bundle: PromptBundle,
        context: UserWaterContext,
        recommendations: List[WaterRecommendation],
        retrieved_knowledge: List[RetrievalResult]
    ) -> ChatbotResponse:
        """
        Generates a validated, structured ChatbotResponse.
        """
        # 1. Synthesize raw text from provider
        raw_answer = self.provider.generate(
            prompt_bundle=prompt_bundle,
            context=context,
            recommendations=recommendations,
            retrieved_knowledge=retrieved_knowledge
        )

        # 2. Apply safety and factuality guardrails
        verified_answer, safety_warnings = ChatbotSafetyGuardrails.verify_factuality(
            response_text=raw_answer,
            context=context
        )

        # 3. Format recommendations for output
        recs_data = [r.to_dict() for r in recommendations]

        # 4. Format evidence with source attribution
        evidence_data = [r.to_dict() for r in retrieved_knowledge]

        # 5. Format sanitized water context
        water_ctx_data = {
            "user_id": context.user_id,
            "meter_id": context.meter_id,
            "property_type": context.property_type,
            "household_size": context.household_size,
            "today_consumption_liters": context.today_consumption_liters,
            "weekly_avg_daily_liters": context.weekly_avg_daily_liters,
            "baseline_daily_liters": context.baseline_daily_liters,
            "recent_trend": context.recent_trend,
            "has_active_anomaly": context.has_active_anomaly,
            "anomaly_type": context.anomaly_type,
            "anomaly_severity": context.anomaly_severity,
            "forecast_available": context.forecast_available,
            "has_active_goal": context.has_active_goal
        }

        # 6. Determine provider name
        provider_name = (
            "gemini_api" if isinstance(self.provider, GeminiLLMProvider) and self.provider.client
            else "deterministic_grounded"
        )

        return ChatbotResponse(
            answer=verified_answer,
            recommendations=recs_data,
            evidence=evidence_data,
            water_context=water_ctx_data,
            warnings=safety_warnings,
            confidence=0.95 if context.has_sufficient_data else 0.65,
            provider_used=provider_name
        )
