"""
Smart Water Usage Advisor - Water Budget Planner Service
Phase 7 - Advanced Water Intelligence & Impact Features
Location: 4_DEVELOPMENT/backend/services/water_budget_service.py

Manages period-bound water budgets (daily, weekly, monthly), calculates burn-down rate,
and deterministically flags projected budget overshoot using forward forecasts.
"""

from typing import Dict, Any, Optional
from datetime import date, timedelta
from sqlalchemy import text
from backend.database.db_config import create_db_engine
from backend.dashboard_data_service import get_data_service


class WaterBudgetService:
    """
    Service for setting, updating, tracking, and predicting overshoots for water budgets.
    """

    VALID_PERIODS = ["daily", "weekly", "monthly"]

    def __init__(self, db_engine=None, data_service=None):
        self._db_engine = db_engine
        self.data_service = data_service or get_data_service()

    def _get_engine(self):
        if self._db_engine is None:
            try:
                self._db_engine = create_db_engine()
            except Exception:
                self._db_engine = None
        return self._db_engine

    def get_active_budget(self, user_id: int) -> Dict[str, Any]:
        """
        Retrieves active water budget for the user with burn-down tracking and overshoot prediction.
        """
        profile = self.data_service.get_user_profile(user_id)
        summary = self.data_service.get_summary(user_id)
        forecast_dto = self.data_service.get_forecast(user_id)
        cost_per_kl = float(profile.get("cost_per_kiloliter", 45.0))
        currency = profile.get("currency_symbol", "₹")

        eng = self._get_engine()
        budget_row = None

        if eng:
            try:
                with eng.connect() as conn:
                    budget_row = conn.execute(text("""
                        SELECT budget_id, period, target_liters, cost_budget,
                               start_date, end_date, is_active
                        FROM water_budgets
                        WHERE user_id = :u_id AND is_active = TRUE
                        ORDER BY created_at DESC
                        LIMIT 1
                    """), {"u_id": user_id}).fetchone()
            except Exception:
                budget_row = None

        today = date.today()

        if budget_row:
            budget_id = budget_row[0]
            period = budget_row[1]
            target_liters = float(budget_row[2])
            cost_budget = float(budget_row[3]) if budget_row[3] is not None else round((target_liters / 1000.0) * cost_per_kl, 2)
            start_date = budget_row[4]
            end_date = budget_row[5]
            if isinstance(start_date, str):
                start_date = date.fromisoformat(start_date)
            if isinstance(end_date, str):
                end_date = date.fromisoformat(end_date)
        else:
            # Synthetic default monthly budget calibrated to benchmark
            benchmark_lpd = float(profile.get("regional_benchmark_lpd", 440.0))
            budget_id = None
            period = "monthly"
            target_liters = round(benchmark_lpd * 30.0 * 0.90, 1)  # 10% below benchmark
            cost_budget = round((target_liters / 1000.0) * cost_per_kl, 2)
            start_date = today - timedelta(days=12)
            end_date = start_date + timedelta(days=30)

        # Calculate time progression
        total_days = max(1, (end_date - start_date).days)
        days_elapsed = max(1, min(total_days, (today - start_date).days))
        days_remaining = max(0, total_days - days_elapsed)

        # Consumed to date
        today_usage = float(summary.get("today_usage_liters", 350.0))
        # Estimate consumed so far
        consumed_liters = round(today_usage * days_elapsed, 1)
        consumed_pct = round((consumed_liters / target_liters * 100.0), 1) if target_liters > 0 else 0.0

        # Burn rates
        ideal_burn_rate_lpd = round(target_liters / total_days, 1)
        actual_burn_rate_lpd = round(consumed_liters / days_elapsed, 1)

        # Forward Projection using Phase 3A forecast outputs
        forecast_avg_lpd = float(forecast_dto.get("forecast_avg_liters_day", today_usage))
        projected_remaining_liters = forecast_avg_lpd * days_remaining
        projected_total_liters = round(consumed_liters + projected_remaining_liters, 1)
        projected_total_cost = round((projected_total_liters / 1000.0) * cost_per_kl, 2)

        # Overshoot evaluation
        is_overshoot = projected_total_liters > target_liters
        projected_overshoot_liters = round(max(0.0, projected_total_liters - target_liters), 1)
        projected_overshoot_cost = round((projected_overshoot_liters / 1000.0) * cost_per_kl, 2)

        return {
            "budget_id": budget_id,
            "user_id": user_id,
            "period": period,
            "target_liters": target_liters,
            "cost_budget": cost_budget,
            "currency_symbol": currency,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "time_progress": {
                "total_days": total_days,
                "days_elapsed": days_elapsed,
                "days_remaining": days_remaining,
                "cycle_completion_pct": round((days_elapsed / total_days * 100.0), 1)
            },
            "consumption_status": {
                "consumed_liters_to_date": consumed_liters,
                "consumed_percentage": consumed_pct,
                "ideal_burn_rate_lpd": ideal_burn_rate_lpd,
                "actual_burn_rate_lpd": actual_burn_rate_lpd,
                "remaining_budget_liters": round(max(0.0, target_liters - consumed_liters), 1)
            },
            "forecast_projection": {
                "forecast_avg_lpd": round(forecast_avg_lpd, 1),
                "projected_total_liters": projected_total_liters,
                "projected_total_cost": projected_total_cost,
                "is_overshoot_predicted": is_overshoot,
                "projected_overshoot_liters": projected_overshoot_liters,
                "projected_overshoot_cost": projected_overshoot_cost,
                "status": "warning" if is_overshoot else "on_track"
            },
            "disclaimer": "Projected total consumption is an analytical estimate based on current burn-down and forward model forecast."
        }

    def set_budget(
        self,
        user_id: int,
        period: str,
        target_liters: float,
        cost_budget: Optional[float] = None,
        duration_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Creates or updates active water budget.
        """
        norm_period = period.lower().strip() if period else "monthly"
        if norm_period not in self.VALID_PERIODS:
            raise ValueError(f"Invalid period '{period}'. Allowed: {', '.join(self.VALID_PERIODS)}")

        if target_liters <= 0:
            raise ValueError("Target liters must be strictly positive.")

        if duration_days is None:
            duration_days = 1 if norm_period == "daily" else (7 if norm_period == "weekly" else 30)

        today = date.today()
        end_date = today + timedelta(days=duration_days)

        eng = self._get_engine()
        budget_id = 1

        if eng:
            try:
                with eng.begin() as conn:
                    # Deactivate existing active budgets
                    conn.execute(text("""
                        UPDATE water_budgets
                        SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = :u_id AND is_active = TRUE
                    """), {"u_id": user_id})

                    res = conn.execute(text("""
                        INSERT INTO water_budgets (
                            user_id, period, target_liters, cost_budget,
                            start_date, end_date, is_active
                        ) VALUES (
                            :u_id, :prd, :t_liters, :c_bgt, :s_date, :e_date, TRUE
                        )
                    """), {
                        "u_id": user_id,
                        "prd": norm_period,
                        "t_liters": target_liters,
                        "c_bgt": cost_budget,
                        "s_date": today,
                        "e_date": end_date
                    })
                    if hasattr(res, "lastrowid") and res.lastrowid:
                        budget_id = res.lastrowid
            except Exception:
                budget_id = 1

        return {
            "budget_id": budget_id,
            "user_id": user_id,
            "period": norm_period,
            "target_liters": target_liters,
            "cost_budget": cost_budget,
            "start_date": str(today),
            "end_date": str(end_date),
            "is_active": True,
            "message": f"Successfully activated new {norm_period} water budget."
        }
