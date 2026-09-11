"""
Smart Water Usage Advisor - Personalized Recommendation Engine
Location: 5_AI_COMPONENTS/chatbot/recommendation_engine.py
Phase 3C - Week 6 Implementation

Generates context-driven, evidence-grounded water conservation recommendations
based on actual user profile, recent trends, operational leak detection alerts,
forecast spikes, and conservation goals.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
try:
    from .context_builder import UserWaterContext
except (ImportError, ValueError):
    from context_builder import UserWaterContext

WATER_COST_PER_LITER = 0.0035  # Standard municipal water tariff benchmark ($/Liter)

@dataclass
class WaterRecommendation:
    """Actionable, personalized water conservation recommendation."""
    title: str
    description: str
    estimated_savings_liters: float
    estimated_savings_cost: float
    priority: str          # "critical", "high", "medium", "low"
    difficulty: str        # "easy", "medium", "hard"
    category: str          # "plumbing", "bathroom", "kitchen", "outdoor", "laundry", "general"
    action_type: str       # "immediate_action", "fixture_upgrade", "habit_change", "preventative"
    source_kb_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PersonalizedRecommendationEngine:
    """
    Expert rule engine synthesizing personalized water-saving recommendations
    directly from the user's operational telemetry and state.
    """

    def generate_recommendations(
        self,
        context: UserWaterContext,
        max_recommendations: int = 3
    ) -> List[WaterRecommendation]:
        """
        Generates prioritized recommendations tailored to the user's specific context.
        Enforces strict truthfulness: never invents leaks or ungrounded claims.
        """
        recs: List[WaterRecommendation] = []

        # 0. Case: Insufficient Telemetry Data
        if not context.has_sufficient_data:
            recs.append(WaterRecommendation(
                title="Establish Smart Meter Telemetry Baseline",
                description="Your smart meter has fewer than 24 hours of recorded data. Allow your meter to run normally for 3-7 days so the system can compute your baseline and identify personalized savings opportunities.",
                estimated_savings_liters=0.0,
                estimated_savings_cost=0.0,
                priority="low",
                difficulty="easy",
                category="general",
                action_type="habit_change"
            ))
            return recs

        # 1. Critical Case: Active Surge (Pipe Burst / Major Breach)
        if context.has_active_anomaly and context.anomaly_type == "surge":
            recs.append(WaterRecommendation(
                title="Emergency: Shut Off Main Water Supply",
                description=f"A critical surge of {context.anomaly_flow_rate:.0f} L/hr was detected. Immediately shut off your property's main water isolation valve to prevent flooding, and contact a licensed plumbing professional.",
                estimated_savings_liters=round(context.anomaly_flow_rate * 24, 0),
                estimated_savings_cost=round(context.anomaly_flow_rate * 24 * WATER_COST_PER_LITER, 2),
                priority="critical",
                difficulty="hard",
                category="plumbing",
                action_type="immediate_action",
                source_kb_id="KB-009"
            ))

        # 2. Urgent Case: Active Continuous Leak (Toilet Flapper / Fixture)
        elif context.has_active_anomaly and context.anomaly_type == "leak":
            recs.append(WaterRecommendation(
                title="Inspect Toilet Cisterns for Silent Leaks",
                description=f"Continuous nocturnal flow of {context.anomaly_flow_rate:.1f} L/hr detected. Perform a 15-minute food-coloring test in your toilet tank. If dye appears in the bowl without flushing, replace the rubber flapper valve.",
                estimated_savings_liters=round(context.anomaly_flow_rate * 24, 0),
                estimated_savings_cost=round(context.anomaly_flow_rate * 24 * WATER_COST_PER_LITER, 2),
                priority="high",
                difficulty="easy",
                category="plumbing",
                action_type="immediate_action",
                source_kb_id="KB-001"
            ))

        # 3. Warning Case: Unusual Nocturnal Pattern / Irrigation
        elif context.has_active_anomaly and context.anomaly_type == "unusual_pattern":
            recs.append(WaterRecommendation(
                title="Audit Off-Hours Irrigation & Equipment",
                description=f"Unusual nocturnal consumption of {context.anomaly_flow_rate:.1f} L/hr was detected during off-peak hours. Check automatic sprinkler solenoids or cooling loop timers for stuck valves or misprogrammed schedules.",
                estimated_savings_liters=round(context.estimated_excess_liters, 0),
                estimated_savings_cost=round(context.estimated_excess_liters * WATER_COST_PER_LITER, 2),
                priority="high",
                difficulty="medium",
                category="outdoor",
                action_type="immediate_action",
                source_kb_id="KB-003"
            ))

        # 4. Forecast Spike Mitigation
        if context.forecast_available and context.forecast_spike_warning:
            recs.append(WaterRecommendation(
                title=f"Prepare for Projected Peak on {context.predicted_peak_day}",
                description=f"Forecast indicates elevated consumption reaching {context.predicted_peak_volume_liters:.0f} L on {context.predicted_peak_day}. Pre-emptively defer outdoor lawn watering and combine washing machine loads to mitigate high peak charges.",
                estimated_savings_liters=round(context.predicted_peak_volume_liters - context.baseline_daily_liters, 0),
                estimated_savings_cost=round((context.predicted_peak_volume_liters - context.baseline_daily_liters) * WATER_COST_PER_LITER, 2),
                priority="medium",
                difficulty="easy",
                category="general",
                action_type="preventative",
                source_kb_id="KB-011"
            ))

        # 5. Increasing Usage Trend -> Category Specific Action
        if context.recent_trend == "increasing" and not context.has_active_anomaly:
            if context.primary_consumption_category == "bathroom":
                recs.append(WaterRecommendation(
                    title="Install Low-Flow Aerated Showerheads",
                    description="Bathroom usage represents your largest water share. Replacing standard 9.5 LPM showerheads with 6.5 LPM WaterSense aerated models saves 60-80 liters daily for a 4-person household.",
                    estimated_savings_liters=75.0,
                    estimated_savings_cost=round(75.0 * 30 * WATER_COST_PER_LITER, 2),
                    priority="medium",
                    difficulty="easy",
                    category="bathroom",
                    action_type="fixture_upgrade",
                    source_kb_id="KB-002"
                ))
            elif context.has_garden:
                recs.append(WaterRecommendation(
                    title="Shift Irrigation to Early Morning",
                    description="Water gardens between 4:00 AM and 7:00 AM to prevent 30-40% evaporative loss under mid-day heat. Adding 5 cm of organic mulch preserves soil moisture for days.",
                    estimated_savings_liters=120.0,
                    estimated_savings_cost=round(120.0 * 30 * WATER_COST_PER_LITER, 2),
                    priority="medium",
                    difficulty="easy",
                    category="outdoor",
                    action_type="habit_change",
                    source_kb_id="KB-003"
                ))
            else:
                recs.append(WaterRecommendation(
                    title="Run Dishwasher and Laundry Only on Full Loads",
                    description="Running kitchen and laundry appliances only when fully loaded saves approximately 40 to 60 liters per run compared to partial load cycles.",
                    estimated_savings_liters=50.0,
                    estimated_savings_cost=round(50.0 * 30 * WATER_COST_PER_LITER, 2),
                    priority="medium",
                    difficulty="easy",
                    category="kitchen",
                    action_type="habit_change",
                    source_kb_id="KB-007"
                ))

        # 6. Active Conservation Goal Alignment
        if context.has_active_goal and len(recs) < max_recommendations:
            gap_pct = 100.0 - context.goal_progress_pct
            recs.append(WaterRecommendation(
                title=f"Close the {gap_pct:.0f}% Gap to Your Conservation Target",
                description=f"Your active target is a {context.goal_target_value:.0f}{context.goal_target_unit} reduction. You have achieved {context.goal_progress_pct:.0f}% progress. Adopting 5-minute shower timers and fixing dripping taps will reach your target this billing cycle.",
                estimated_savings_liters=round(context.weekly_avg_daily_liters * 0.15, 0),
                estimated_savings_cost=round(context.weekly_avg_daily_liters * 0.15 * 30 * WATER_COST_PER_LITER, 2),
                priority="medium",
                difficulty="easy",
                category="general",
                action_type="habit_change",
                source_kb_id="KB-014"
            ))

        # 7. Baseline General Recommendation (if fewer than max)
        if len(recs) < max_recommendations and not context.has_active_anomaly:
            recs.append(WaterRecommendation(
                title="Screw on Multi-Mesh Sink Aerators",
                description="Inexpensive aerators reduce kitchen and bathroom tap flow from 8.3 LPM to 4.5 LPM without reducing rinsing pressure, saving 20-30 liters daily.",
                estimated_savings_liters=25.0,
                estimated_savings_cost=round(25.0 * 30 * WATER_COST_PER_LITER, 2),
                priority="low",
                difficulty="easy",
                category="domestic_efficiency",
                action_type="fixture_upgrade",
                source_kb_id="KB-005"
            ))

        return recs[:max_recommendations]
