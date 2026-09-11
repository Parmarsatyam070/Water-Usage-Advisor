"""
Smart Water Usage Advisor - Responsible AI & Chatbot Safety Guardrails
Location: 5_AI_COMPONENTS/chatbot/safety.py
Phase 3C - Week 6 Implementation

Provides safety guardrails:
- Prompt injection detection and defense
- Secret and credential scrubbing (API keys, passwords, connection strings)
- Telemetry factuality verification (preventing hallucinated consumption and false leaks)
- Plumbing hazard prevention and professional plumber referral
- Insufficient data transparency
"""

import re
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional, Tuple
try:
    from .context_builder import UserWaterContext
except (ImportError, ValueError):
    from context_builder import UserWaterContext

# Known prompt injection signatures
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+(instructions|prompts|rules)",
    r"(reveal|print|show|output|display|tell)\s+(me\s+)?(your\s+|the\s+)?(hidden\s+)?(system\s+prompt|instructions|prompt)",
    r"(what\s+is|show\s+me)\s+(your\s+)?(hidden\s+)?system\s+prompt",
    r"system\s+prompt|hidden\s+prompt",
    r"you\s+are\s+now\s+(an?\s+)?unrestricted",
    r"dan\s+mode|jailbreak",
    r"(reveal|print|show|give|tell)\s+.*(api[_\s]?key|secret|password|credential)",
    r"drop\s+table|delete\s+from|insert\s+into|select\s+\*\s+from\s+users",
    r"bypass\s+safety|override\s+rules|disregard\s+guidelines"
]

# Sensitive patterns to scrub from outputs
SECRET_PATTERNS = [
    r"AIza[0-9A-Za-z-_]{35}",                     # Google API Key
    r"sk-[0-9A-Za-z]{32,}",                       # OpenAI-style key
    r"postgres(?:ql)?://[^\s\"']+",              # Database URLs
    r"password\s*[:=]\s*['\"]?[^\s\"',]+",       # Passwords
    r"secret[_\s]?key\s*[:=]\s*['\"]?[^\s\"',]+"  # Secret keys
]

# High-risk plumbing situations requiring licensed professional referral
DANGEROUS_PLUMBING_KEYWORDS = [
    "cut the pipe", "weld", "soldering live", "gas water heater",
    "electric shock", "water heater explosion", "tamper with municipal meter",
    "bypass backflow", "sewer main repair"
]

@dataclass
class SafetyCheckResult:
    """Outcome of safety evaluations."""
    is_safe: bool
    is_injection_attempt: bool = False
    violates_plumbing_safety: bool = False
    refusal_message: Optional[str] = None
    sanitized_query: str = ""
    warnings: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ChatbotSafetyGuardrails:
    """
    Responsible AI evaluation engine for water conservation chatbot inputs and outputs.
    """

    @classmethod
    def evaluate_input(cls, user_query: str) -> SafetyCheckResult:
        """
        Inspects incoming user queries for injection attacks, secret probing,
        or dangerous plumbing requests.
        """
        query_clean = user_query.strip()
        warnings: List[str] = []

        if not query_clean:
            return SafetyCheckResult(
                is_safe=False,
                refusal_message="Please provide a valid question regarding your water consumption, billing, or conservation.",
                sanitized_query="",
                warnings=["empty_query"]
            )

        # 1. Check for prompt injection attempts
        for pattern in PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, query_clean, re.IGNORECASE):
                return SafetyCheckResult(
                    is_safe=False,
                    is_injection_attempt=True,
                    refusal_message=(
                        "I am the Smart Water Usage Advisor, focused exclusively on water conservation, "
                        "usage analytics, and leak guidance. I cannot modify my system instructions or reveal internal configurations."
                    ),
                    sanitized_query=query_clean,
                    warnings=["prompt_injection_detected"]
                )

        # 2. Check for dangerous plumbing DIY requests
        for kw in DANGEROUS_PLUMBING_KEYWORDS:
            if kw in query_clean.lower():
                warnings.append("high_risk_plumbing_topic")

        # 3. Scrub secrets from query before passing downstream
        sanitized = cls.scrub_secrets(query_clean)

        return SafetyCheckResult(
            is_safe=True,
            sanitized_query=sanitized,
            warnings=warnings
        )

    @classmethod
    def scrub_secrets(cls, text: str) -> str:
        """Removes API keys, passwords, and connection strings from any text string."""
        cleaned = text
        for pattern in SECRET_PATTERNS:
            cleaned = re.sub(pattern, "[REDACTED_CREDENTIAL]", cleaned, flags=re.IGNORECASE)
        return cleaned

    @classmethod
    def verify_factuality(
        cls,
        response_text: str,
        context: UserWaterContext
    ) -> Tuple[str, List[str]]:
        """
        Validates output text against ground truth facts in the user's water context:
        - If no anomaly exists, ensures response doesn't falsely state a leak was detected.
        - If insufficient data exists, ensures response states so.
        - Scrubs any accidental credential leak.
        """
        verified_text = cls.scrub_secrets(response_text)
        warnings: List[str] = []

        # Guard against false leak assertions
        if not context.has_active_anomaly:
            false_leak_phrases = [
                "your meter detected a leak",
                "you currently have an active leak",
                "we found a critical leak",
                "an active leak alert has been triggered"
            ]
            for phrase in false_leak_phrases:
                if phrase in verified_text.lower():
                    # Replace false claim with accurate context
                    verified_text = re.sub(
                        phrase,
                        "no active leaks are currently detected on your meter",
                        verified_text,
                        flags=re.IGNORECASE
                    )
                    warnings.append("false_leak_claim_suppressed")

        # Guard against ungrounded certainty if data is insufficient
        if not context.has_sufficient_data:
            if "insufficient" not in verified_text.lower() and "not enough" not in verified_text.lower():
                verified_text = (
                    "Note: Your smart meter currently has limited telemetry history. "
                    + verified_text
                )
                warnings.append("insufficient_data_disclaimer_added")

        return verified_text, warnings
