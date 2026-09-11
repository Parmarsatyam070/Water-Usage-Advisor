"""
Smart Water Usage Advisor - Grounded Prompt Builder
Location: 5_AI_COMPONENTS/chatbot/prompt_builder.py
Phase 3C - Week 6 Implementation

Assembles structured, grounded prompts combining system instructions,
operational user water context, retrieved knowledge snippets, and dialogue history.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
try:
    from .context_builder import UserWaterContext
    from .retrieval import RetrievalResult
except (ImportError, ValueError):
    from context_builder import UserWaterContext
    from retrieval import RetrievalResult

SYSTEM_PROMPT_CORE = """You are the Smart Water Usage Advisor, an intelligent AI conservation assistant supporting UN Sustainable Development Goal 6 (Clean Water & Sanitation). Your purpose is to help residential homeowners, facility managers, and municipalities understand water consumption patterns, diagnose anomalies and leaks early, forecast future usage, and implement effective water-saving habits.

RULES AND CONSTRAINTS:
1. GROUNDED FACTUALITY: Only refer to data provided in the USER_CONTEXT block (user profile, meter readings, active alerts, forecast numbers). Never invent or hallucinate water consumption numbers, meter IDs, dates, or leaks.
2. HONESTY ABOUT UNCERTAINTY: If the data does not provide a definitive answer, clearly acknowledge uncertainty (e.g., "The telemetry indicates continuous low flow between 02:00 and 04:00 AM, which often suggests a toilet flapper leak or dripping faucet, but an on-site inspection is necessary to confirm.").
3. SUPPORTIVE & NON-JUDGMENTAL TONE: Never use shaming or accusatory language. Frame feedback in terms of opportunity, cost savings, and sustainability impact.
4. ACTIONABLE GUIDANCE: Provide step-by-step, low-cost or zero-cost diagnostic tests and practical conservation recommendations.
5. CONCISE & READABLE: Keep answers focused and under 150 words. Use bullet points for steps.
6. PLUMBING SAFETY: Do not provide dangerous plumbing instructions. For major leaks, pipe bursts, high water pressure, or structural plumbing, always recommend contacting a qualified licensed plumbing professional. Never advise tampering with municipal supply mains.
7. CLEAR DISTINCTION: Clearly distinguish measured telemetry facts from general recommendations and statistical forecasts."""

@dataclass
class PromptBundle:
    """Complete assembled prompt bundle for response generation."""
    system_prompt: str
    user_context_str: str
    knowledge_str: str
    history_str: str
    user_query: str
    full_prompt: str


class ChatbotPromptBuilder:
    """
    Builds structured, grounded prompts adhering to the Phase 1 conversational design.
    """

    def __init__(self, system_prompt: str = SYSTEM_PROMPT_CORE):
        self.system_prompt = system_prompt

    def build_prompt_bundle(
        self,
        user_query: str,
        context: UserWaterContext,
        retrieved_knowledge: List[RetrievalResult],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> PromptBundle:
        """
        Synthesizes a complete grounded prompt bundle.
        """
        # 1. Format User Context
        context_str = context.to_summary_text()

        # 2. Format Retrieved Knowledge
        if retrieved_knowledge:
            kb_lines = []
            for r in retrieved_knowledge:
                kb_lines.append(f"[{r.entry_id}] {r.title}: {r.snippet} (Est. Savings: {r.savings_estimate_liters_day:.0f} L/day)")
            knowledge_str = "\n".join(kb_lines)
        else:
            knowledge_str = "No specific knowledge base documents retrieved for this query."

        # 3. Format Conversation History (last 3 turns)
        if conversation_history:
            hist_lines = []
            for turn in conversation_history[-3:]:
                u_msg = turn.get("user", "")
                a_msg = turn.get("assistant", "")
                if u_msg:
                    hist_lines.append(f"User: {u_msg}")
                if a_msg:
                    hist_lines.append(f"Assistant: {a_msg}")
            history_str = "\n".join(hist_lines)
        else:
            history_str = "None (first turn in session)."

        # 4. Assemble Full Prompt
        full_prompt = (
            f"[SYSTEM INSTRUCTION]\n{self.system_prompt}\n\n"
            f"[USER CONTEXT]\n{context_str}\n\n"
            f"[RETRIEVED KNOWLEDGE BASE SNIPPETS]\n{knowledge_str}\n\n"
            f"[CONVERSATION HISTORY]\n{history_str}\n\n"
            f"[USER QUERY]\n{user_query}\n\n"
            f"[ASSISTANT RESPONSE]\n"
        )

        return PromptBundle(
            system_prompt=self.system_prompt,
            user_context_str=context_str,
            knowledge_str=knowledge_str,
            history_str=history_str,
            user_query=user_query,
            full_prompt=full_prompt
        )
