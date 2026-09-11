"""
Smart Water Usage Advisor - What-If Scenario Analysis Service
Phase 7 - Advanced Water Intelligence & Impact Features
Location: 4_DEVELOPMENT/backend/services/scenario_service.py

Provides deterministic what-if scenario simulations on disaggregated end-uses.
Uses existing telemetry and category data without retraining AI models.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy import text
from backend.dashboard_data_service import get_data_service
from backend.database.db_config import create_db_engine


class ScenarioAnalysisService:
    """
    Scenario analysis engine for disaggregated water use modification.
    Enables users to evaluate hypothetical behavioral or fixture changes.
    """

    VALID_CATEGORIES = ["bathroom", "kitchen", "laundry", "garden", "cleaning", "other", "all"]

    DEFAULT_CATEGORY_SHARES = {
        "bathroom": 0.40,
        "kitchen": 0.20,
        "laundry": 0.15,
        "garden": 0.15,
        "cleaning": 0.05,
        "other": 0.05
    }

    def __init__(self, data_service=None, db_engine=None):
        self.data_service = data_service or get_data_service()
        self._db_engine = db_engine

    def _get_engine(self):
        if self._db_engine is None:
            try:
                self._db_engine = create_db_engine()
            except Exception:
                self._db_engine = None
        return self._db_engine

    def run_scenario(
        self,
        user_id: int,
        scenario_name: str,
        category: str,
        percentage_change: float,
        save_to_history: bool = False
    ) -> Dict[str, Any]:
        """
        Executes a deterministic what-if scenario for a user and specified consumption category.

        Args:
            user_id: Authenticated user ID.
            scenario_name: Descriptive name for the scenario.
            category: Target category ('bathroom', 'kitchen', 'laundry', 'garden', 'cleaning', 'other', 'all').
            percentage_change: Change percentage (-100.0% to +100.0%).
            save_to_history: If True, persists record in `scenarios` table.

        Returns:
            Dictionary containing baseline, scenario result, breakdown, and explanation.
        """
        norm_cat = category.lower().strip() if category else "all"
        if norm_cat not in self.VALID_CATEGORIES:
            raise ValueError(f"Invalid category '{category}'. Allowed: {', '.join(self.VALID_CATEGORIES)}")

        if percentage_change < -100.0 or percentage_change > 200.0:
            raise ValueError("Percentage change must be between -100.0% and +200.0%.")

        profile = self.data_service.get_user_profile(user_id)
        summary = self.data_service.get_summary(user_id)

        # Baseline daily consumption
        baseline_daily = summary.get("today_usage_liters") or profile.get("regional_benchmark_lpd", 440.0)
        cost_per_kl = profile.get("cost_per_kiloliter", 45.0)

        # Get disaggregated breakdown
        category_shares = dict(self.DEFAULT_CATEGORY_SHARES)

        # Compute baseline and modified volumes by category
        baseline_categories = {}
        scenario_categories = {}

        for cat, share in category_shares.items():
            cat_vol = baseline_daily * share
            baseline_categories[cat] = round(cat_vol, 2)

            if norm_cat == "all" or norm_cat == cat:
                mod_factor = 1.0 + (percentage_change / 100.0)
                scenario_categories[cat] = round(max(0.0, cat_vol * mod_factor), 2)
            else:
                scenario_categories[cat] = round(cat_vol, 2)

        scenario_daily = sum(scenario_categories.values())
        diff_liters = baseline_daily - scenario_daily  # Positive = saved, Negative = increased
        abs_diff = abs(diff_liters)
        pct_diff = round((diff_liters / baseline_daily * 100.0), 2) if baseline_daily > 0 else 0.0

        # Estimated financial impact per 30-day billing cycle
        monthly_liters_saved = diff_liters * 30.0
        monthly_monetary_impact = round((monthly_liters_saved / 1000.0) * cost_per_kl, 2)

        direction = "reduction" if diff_liters >= 0 else "increase"
        explanation = (
            f"Scenario '{scenario_name}': Simulating a {abs(percentage_change):.1f}% {direction} in "
            f"{norm_cat.capitalize()} consumption adjusts daily usage from {baseline_daily:.1f} L to "
            f"{scenario_daily:.1f} L, with an estimated monthly impact of {abs(monthly_liters_saved):.1f} L "
            f"({profile.get('currency_symbol', '₹')}{abs(monthly_monetary_impact):.2f})."
        )

        scenario_id = None
        if save_to_history:
            scenario_id = self._save_scenario_record(
                user_id=user_id,
                scenario_name=scenario_name,
                category=norm_cat,
                percentage_change=percentage_change,
                baseline_liters=baseline_daily,
                scenario_liters=scenario_daily,
                saved_liters=diff_liters,
                savings_amount=monthly_monetary_impact,
                explanation=explanation
            )

        return {
            "scenario_id": scenario_id,
            "scenario_name": scenario_name,
            "target_category": norm_cat,
            "percentage_change": percentage_change,
            "baseline_daily_liters": round(baseline_daily, 2),
            "scenario_daily_liters": round(scenario_daily, 2),
            "difference_daily_liters": round(diff_liters, 2),
            "difference_percentage": pct_diff,
            "monthly_liters_saved": round(monthly_liters_saved, 2),
            "monthly_financial_impact": monthly_monetary_impact,
            "currency_symbol": profile.get("currency_symbol", "₹"),
            "baseline_breakdown": baseline_categories,
            "scenario_breakdown": scenario_categories,
            "explanation": explanation,
            "is_simulation": True,
            "disclaimer": (
                "What-if results are analytical simulations intended for decision support. "
                "Actual household consumption will vary based on weather, schedule, and appliance efficiency."
            )
        }

    def _save_scenario_record(
        self,
        user_id: int,
        scenario_name: str,
        category: str,
        percentage_change: float,
        baseline_liters: float,
        scenario_liters: float,
        saved_liters: float,
        savings_amount: float,
        explanation: str
    ) -> Optional[int]:
        """Saves scenario to the `scenarios` table if database is connected."""
        eng = self._get_engine()
        if not eng:
            return None

        try:
            with eng.begin() as conn:
                res = conn.execute(text("""
                    INSERT INTO scenarios (
                        user_id, scenario_name, category, percentage_change,
                        baseline_liters, scenario_liters, saved_liters,
                        estimated_savings_amount, explanation
                    ) VALUES (
                        :u_id, :s_name, :cat, :pct, :base, :scen, :saved, :amt, :exp
                    )
                """), {
                    "u_id": user_id,
                    "s_name": scenario_name,
                    "cat": category,
                    "pct": percentage_change,
                    "base": baseline_liters,
                    "scen": scenario_liters,
                    "saved": saved_liters,
                    "amt": max(0.0, savings_amount),
                    "exp": explanation
                })
                # Attempt to retrieve primary key if supported
                if hasattr(res, "lastrowid") and res.lastrowid:
                    return res.lastrowid
                return 1
        except Exception:
            # Fallback gracefully if DB is offline
            return None

    def get_scenario_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieves previously saved scenarios for the user."""
        eng = self._get_engine()
        if not eng:
            return []

        try:
            with eng.connect() as conn:
                res = conn.execute(text("""
                    SELECT scenario_id, scenario_name, category, percentage_change,
                           baseline_liters, scenario_liters, saved_liters,
                           estimated_savings_amount, explanation, created_at
                    FROM scenarios
                    WHERE user_id = :u_id
                    ORDER BY created_at DESC
                    LIMIT :lim
                """), {"u_id": user_id, "lim": limit})

                history = []
                for row in res.fetchall():
                    history.append({
                        "scenario_id": row[0],
                        "scenario_name": row[1],
                        "category": row[2],
                        "percentage_change": float(row[3]),
                        "baseline_liters": float(row[4]),
                        "scenario_liters": float(row[5]),
                        "saved_liters": float(row[6]),
                        "estimated_savings_amount": float(row[7]) if row[7] is not None else 0.0,
                        "explanation": row[8],
                        "created_at": str(row[9])
                    })
                return history
        except Exception:
            return []
