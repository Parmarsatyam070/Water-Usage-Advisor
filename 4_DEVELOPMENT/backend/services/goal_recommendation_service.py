"""
Smart Water Usage Advisor - Smart Goal Recommendation Service
Phase 7 - Advanced Water Intelligence & Impact Features
Location: 4_DEVELOPMENT/backend/services/goal_recommendation_service.py

Generates 3 tailored, achievable water conservation goal recommendations
based on historical usage patterns, forecast trends, and household profile.
Enforces sanitary safety threshold (minimum 50 L/capita/day per WHO guidelines).
Provides adoption mechanism into the authoritative goals table.
"""

from typing import Dict, Any, List, Optional
from datetime import date, timedelta
from sqlalchemy import text
from backend.database.db_config import create_db_engine
from backend.dashboard_data_service import get_data_service


class GoalRecommendationService:
    """
    Synthesizes intelligent goal recommendations (Starter, Balanced, Ambitious)
    and allows seamless adoption into the database.
    """

    # WHO minimum recommended water requirement per capita per day for basic health & sanitation
    WHO_MINIMUM_LPD_PER_CAPITA = 50.0

    def __init__(self, db_engine=None, data_service=None):
        self._db_engine = db_engine
        self.data_service = data_service or get_data_service()
        self._in_memory_goals = {}

    def _get_engine(self):
        if self._db_engine is None:
            try:
                self._db_engine = create_db_engine()
            except Exception:
                self._db_engine = None
        return self._db_engine

    def generate_recommendations(self, user_id: int) -> Dict[str, Any]:
        """
        Generates 3 tailored, achievable goals based on current usage and profile.
        """
        profile = self.data_service.get_user_profile(user_id)
        summary = self.data_service.get_summary(user_id)

        daily_usage = float(summary.get("today_usage_liters") or profile.get("regional_benchmark_lpd", 440.0))
        household_size = max(1, int(profile.get("household_size", 4)))
        safe_floor_lpd = household_size * self.WHO_MINIMUM_LPD_PER_CAPITA
        cost_per_kl = float(profile.get("cost_per_kiloliter", 45.0))
        currency = profile.get("currency_symbol", "₹")

        # 1. Quick Win Goal (5-10% reduction)
        starter_pct = 8.0
        starter_target = max(safe_floor_lpd, round(daily_usage * (1.0 - starter_pct / 100.0), 1))
        starter_savings_lpd = round(daily_usage - starter_target, 1)
        starter_monthly_fin = round((starter_savings_lpd * 30.0 / 1000.0) * cost_per_kl, 2)

        # 2. Balanced Goal (15% reduction)
        balanced_pct = 15.0
        balanced_target = max(safe_floor_lpd, round(daily_usage * (1.0 - balanced_pct / 100.0), 1))
        balanced_savings_lpd = round(daily_usage - balanced_target, 1)
        balanced_monthly_fin = round((balanced_savings_lpd * 30.0 / 1000.0) * cost_per_kl, 2)

        # 3. Sustainability Champion Goal (25% reduction or capped at safe floor)
        ambitious_pct = 25.0
        ambitious_target = max(safe_floor_lpd, round(daily_usage * (1.0 - ambitious_pct / 100.0), 1))
        ambitious_savings_lpd = round(daily_usage - ambitious_target, 1)
        ambitious_monthly_fin = round((ambitious_savings_lpd * 30.0 / 1000.0) * cost_per_kl, 2)

        recommendations = [
            {
                "recommendation_id": "rec_starter",
                "tier": "starter",
                "title": "Smart Starter: Daily Consumption Cap",
                "description": f"Cap daily household consumption at {starter_target} L/day (~{starter_pct:.0f}% reduction).",
                "goal_type": "daily_limit",
                "target_value": starter_target,
                "target_unit": "liters",
                "duration_days": 30,
                "difficulty": "Easy",
                "estimated_monthly_savings_liters": round(starter_savings_lpd * 30.0, 1),
                "estimated_monthly_financial_savings": starter_monthly_fin,
                "currency_symbol": currency,
                "primary_focus": "Bathroom aeration and short shower awareness"
            },
            {
                "recommendation_id": "rec_balanced",
                "tier": "balanced",
                "title": "Balanced Steward: 15% Monthly Reduction",
                "description": f"Achieve an overall 15% reduction targeting {balanced_target} L/day.",
                "goal_type": "percentage_reduction",
                "target_value": balanced_pct,
                "target_unit": "percent",
                "duration_days": 60,
                "difficulty": "Moderate",
                "estimated_monthly_savings_liters": round(balanced_savings_lpd * 30.0, 1),
                "estimated_monthly_financial_savings": balanced_monthly_fin,
                "currency_symbol": currency,
                "primary_focus": "Eliminating off-peak continuous drip and garden optimization"
            },
            {
                "recommendation_id": "rec_ambitious",
                "tier": "ambitious",
                "title": "SDG Champion: Advanced Conservation Target",
                "description": f"Target ambitious conservation of {ambitious_target} L/day (~{ambitious_pct:.0f}% reduction).",
                "goal_type": "daily_limit",
                "target_value": ambitious_target,
                "target_unit": "liters",
                "duration_days": 90,
                "difficulty": "Ambitious",
                "estimated_monthly_savings_liters": round(ambitious_savings_lpd * 30.0, 1),
                "estimated_monthly_financial_savings": ambitious_monthly_fin,
                "currency_symbol": currency,
                "primary_focus": "Greywater recycling and smart sensor valve integration"
            }
        ]

        return {
            "user_id": user_id,
            "baseline_daily_liters": round(daily_usage, 1),
            "household_occupants": household_size,
            "sanitary_floor_lpd": safe_floor_lpd,
            "sanitary_floor_disclosure": (
                f"WHO baseline guideline: Minimum {self.WHO_MINIMUM_LPD_PER_CAPITA} L/capita/day "
                f"({safe_floor_lpd} L/day total) is preserved to ensure family hygiene and health."
            ),
            "recommendations": recommendations
        }

    def adopt_goal(
        self,
        user_id: int,
        goal_type: str,
        target_value: float,
        target_unit: str = "liters",
        duration_days: int = 30
    ) -> Dict[str, Any]:
        """
        Adopts a recommended goal and writes it to the `goals` table.
        """
        valid_types = [
            "daily_limit", "weekly_target", "savings_amount", "percentage_reduction",
            "shower_aerator", "shower_reduction", "smart_irrigation", "leak_repair", "custom"
        ]
        if goal_type not in valid_types:
            raise ValueError(f"Invalid goal_type '{goal_type}'. Allowed: {', '.join(valid_types)}")

        if target_value <= 0:
            raise ValueError("Target value must be strictly positive.")

        today = date.today()
        end_date = today + timedelta(days=max(7, duration_days))

        eng = self._get_engine()
        goal_id = None

        if eng:
            try:
                with eng.begin() as conn:
                    # Deactivate previous active goals of this type
                    conn.execute(text("""
                        UPDATE goals
                        SET status = 'cancelled', updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = :u_id AND status = 'active'
                    """), {"u_id": user_id})

                    # Insert new active goal
                    if eng.dialect.name == "postgresql":
                        res = conn.execute(text("""
                            INSERT INTO goals (
                                user_id, goal_type, target_value, target_unit,
                                start_date, end_date, status, progress_percentage
                            ) VALUES (
                                :u_id, :g_type, :val, :unit, :s_date, :e_date, 'active', 0.0
                            ) RETURNING goal_id
                        """), {
                            "u_id": user_id,
                            "g_type": goal_type,
                            "val": target_value,
                            "unit": target_unit,
                            "s_date": today,
                            "e_date": end_date
                        })
                        row = res.fetchone()
                        goal_id = row[0] if row else None
                    else:
                        res = conn.execute(text("""
                            INSERT INTO goals (
                                user_id, goal_type, target_value, target_unit,
                                start_date, end_date, status, progress_percentage
                            ) VALUES (
                                :u_id, :g_type, :val, :unit, :s_date, :e_date, 'active', 0.0
                            )
                        """), {
                            "u_id": user_id,
                            "g_type": goal_type,
                            "val": target_value,
                            "unit": target_unit,
                            "s_date": today,
                            "e_date": end_date
                        })
                        if hasattr(res, "lastrowid") and res.lastrowid:
                            goal_id = res.lastrowid
                        else:
                            goal_id = None
            except Exception:
                # Graceful fallback if database is offline
                goal_id = None

        if not goal_id:
            user_goals = self._in_memory_goals.setdefault(user_id, [])
            goal_id = len(user_goals) + 1
            user_goals.append({
                "goal_id": goal_id,
                "user_id": user_id,
                "goal_type": goal_type,
                "target_value": target_value,
                "target_unit": target_unit,
                "start_date": str(today),
                "end_date": str(end_date),
                "status": "active",
                "progress_percentage": 0.0
            })

        return {
            "goal_id": goal_id,
            "user_id": user_id,
            "goal_type": goal_type,
            "target_value": target_value,
            "target_unit": target_unit,
            "start_date": str(today),
            "end_date": str(end_date),
            "status": "active",
            "progress_percentage": 0.0,
            "message": f"Successfully adopted '{goal_type}' goal."
        }
