"""
Smart Water Usage Advisor - Sustainability Score Service
Phase 7 - Advanced Water Intelligence & Impact Features
Location: 4_DEVELOPMENT/backend/services/sustainability_score_service.py

Calculates transparent, deterministic 0-100 Water Usage Sustainability Score.
All calculations adhere to strict normalization and ethical decision-support disclaimers.
"""

from typing import Dict, Any, Optional
import numpy as np
from backend.dashboard_data_service import get_data_service


class SustainabilityScoreService:
    """
    Computes a composite, transparent 0-100 water sustainability score based on:
    - Consumption Efficiency vs Documented Benchmark (30%)
    - Anomaly & Leak Incident Penalties (25%)
    - Conservation Goal Achievement (25%)
    - Usage Trend Direction & Slope (20%)
    """

    METHODOLOGY_DISCLOSURE = (
        "The score is a transparent deterministic decision-support metric, "
        "not a scientifically validated environmental certification."
    )

    BENCHMARK_PROVENANCE = (
        "Project-configured benchmark / documented assumption "
        "(established during Phase 4 system integration to calibrate synthetic consumer personas)."
    )

    def __init__(self, data_service=None):
        self.data_service = data_service or get_data_service()

    def calculate_score(self, user_id: int) -> Dict[str, Any]:
        """
        Calculates normalized sustainability score and component breakdown for a user.

        Args:
            user_id: Target user ID.

        Returns:
            Dictionary containing total score, letter grade, component scores, and disclosures.
        """
        profile = self.data_service.get_user_profile(user_id)
        summary = self.data_service.get_summary(user_id)
        anomalies_dto = self.data_service.get_anomalies(user_id)
        goals_dto = self.data_service.get_goals(user_id)

        # 1. Consumption Efficiency Component (30% weight)
        benchmark_lpd = float(profile.get("regional_benchmark_lpd", 440.0))
        # Use average daily usage from summary or profile
        current_lpd = float(summary.get("today_usage_liters", benchmark_lpd))

        if benchmark_lpd > 0:
            excess_ratio = max(0.0, (current_lpd - benchmark_lpd) / benchmark_lpd)
            s_eff = float(np.clip(100.0 - (excess_ratio * 100.0), 0.0, 100.0))
        else:
            s_eff = 100.0

        # 2. Anomaly & Leak Status Component (25% weight)
        # Severity-class penalties applied ONCE per class to prevent duplicate alert skew
        incidents = anomalies_dto.get("incidents", [])
        active_incidents = [inc for inc in incidents if inc.get("is_active", True)]

        has_critical = any(
            inc.get("severity") == "critical" or "burst" in inc.get("anomaly_type", "").lower()
            for inc in active_incidents
        )
        has_high = any(inc.get("severity") == "high" for inc in active_incidents)
        has_medium = any(inc.get("severity") == "medium" for inc in active_incidents)

        critical_penalty = 25.0 if has_critical else 0.0
        high_penalty = 15.0 if has_high else 0.0
        medium_penalty = 5.0 if has_medium else 0.0

        s_anom = float(np.clip(100.0 - critical_penalty - high_penalty - medium_penalty, 0.0, 100.0))

        # 3. Goal Performance Component (25% weight)
        target_pct = profile.get("conservation_goal_pct", 0.0)
        achieved_pct = float(goals_dto.get("achieved_progress_pct", 0.0))

        if target_pct > 0:
            s_goal = float(np.clip(achieved_pct, 0.0, 100.0))
        else:
            s_goal = 70.0  # Documented neutral baseline when no goal is set

        # 4. Usage Trend Component (20% weight)
        # Compare 7-day forecast/recent trend vs historical average
        trend_delta_pct = float(summary.get("forecast_trend_pct", 0.0))

        if trend_delta_pct <= -5.0:
            # Significant reduction (> 5% reduction)
            s_trend = 100.0
        elif abs(trend_delta_pct) < 5.0:
            # Stable consumption (within +/- 5%)
            s_trend = 75.0
        else:
            # Increasing consumption (> 5% growth)
            growth_pct = trend_delta_pct - 5.0
            s_trend = float(max(0.0, 75.0 - (growth_pct * 2.0)))

        # Composite Score Calculation (strictly normalized [0, 100])
        total_score = (
            0.30 * s_eff +
            0.25 * s_anom +
            0.25 * s_goal +
            0.20 * s_trend
        )
        total_score = round(float(np.clip(total_score, 0.0, 100.0)), 1)

        # Letter Grade
        if total_score >= 90.0:
            grade = "A"
            rating = "Exemplary Efficiency"
        elif total_score >= 75.0:
            grade = "B"
            rating = "Good Performance"
        elif total_score >= 60.0:
            grade = "C"
            rating = "Moderate Consumption"
        elif total_score >= 45.0:
            grade = "D"
            rating = "Elevated Inefficiency"
        else:
            grade = "F"
            rating = "Critical Action Required"

        return {
            "user_id": user_id,
            "meter_id": profile.get("meter_id", user_id),
            "sustainability_score": total_score,
            "grade": grade,
            "rating": rating,
            "components": {
                "efficiency": {
                    "score": round(s_eff, 1),
                    "weight": 0.30,
                    "benchmark_lpd": benchmark_lpd,
                    "current_usage_lpd": round(current_lpd, 1),
                    "benchmark_provenance": self.BENCHMARK_PROVENANCE
                },
                "anomaly_status": {
                    "score": round(s_anom, 1),
                    "weight": 0.25,
                    "active_critical": has_critical,
                    "active_high": has_high,
                    "active_medium": has_medium,
                    "penalties_applied": {
                        "critical": critical_penalty,
                        "high": high_penalty,
                        "medium": medium_penalty
                    }
                },
                "goal_progress": {
                    "score": round(s_goal, 1),
                    "weight": 0.25,
                    "target_reduction_pct": target_pct,
                    "achieved_progress_pct": achieved_pct,
                    "is_default_baseline": target_pct <= 0
                },
                "usage_trend": {
                    "score": round(s_trend, 1),
                    "weight": 0.20,
                    "trend_delta_pct": round(trend_delta_pct, 1),
                    "trend_direction": "decreasing" if trend_delta_pct <= -5 else ("stable" if abs(trend_delta_pct) < 5 else "increasing")
                }
            },
            "methodology_disclosure": self.METHODOLOGY_DISCLOSURE,
            "is_estimate": True
        }
