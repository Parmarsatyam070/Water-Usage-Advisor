"""
Smart Water Usage Advisor - Water Savings Simulator Service
Phase 7 - Advanced Water Intelligence & Impact Features
Location: 4_DEVELOPMENT/backend/services/water_savings_service.py

Provides deterministic calculation of projected water and cost savings.
All results are strictly labeled as estimates.
"""

from typing import Dict, Any, Optional


class WaterSavingsService:
    """
    Deterministic water conservation savings simulator.
    Calculates projected volumetric and monetary savings across various timeframes.
    """

    PERIOD_MULTIPLIERS = {
        "daily": 1.0,
        "weekly": 7.0,
        "monthly": 30.0,
        "annual": 365.0
    }

    @staticmethod
    def simulate_savings(
        baseline_consumption: float,
        reduction_percentage: Optional[float] = None,
        target_consumption: Optional[float] = None,
        rate_per_kiloliter: Optional[float] = None,
        period: str = "monthly",
        currency_symbol: str = "₹"
    ) -> Dict[str, Any]:
        """
        Simulates volumetric and financial savings deterministically.

        Args:
            baseline_consumption: Current consumption volume (liters) for the specified period.
            reduction_percentage: Optional target reduction percentage (0.0 to 100.0).
            target_consumption: Optional direct target volume (liters).
            rate_per_kiloliter: Optional cost per 1,000 liters.
            period: Timeframe ("daily", "weekly", "monthly", "annual").
            currency_symbol: Currency symbol for financial projections.

        Returns:
            Dictionary containing baseline, projected consumption, savings, and disclaimers.
        """
        if baseline_consumption is None or baseline_consumption < 0:
            raise ValueError("Baseline consumption must be a non-negative number.")

        normalized_period = period.lower().strip() if period else "monthly"
        if normalized_period not in WaterSavingsService.PERIOD_MULTIPLIERS:
            raise ValueError(f"Invalid period '{period}'. Allowed: daily, weekly, monthly, annual.")

        # Determine reduction percentage and projected consumption
        if reduction_percentage is not None:
            if not (0.0 <= reduction_percentage <= 100.0):
                raise ValueError("Reduction percentage must be between 0.0 and 100.0 percent.")
            effective_pct = float(reduction_percentage)
            saved_liters = baseline_consumption * (effective_pct / 100.0)
            projected_consumption = baseline_consumption - saved_liters
        elif target_consumption is not None:
            if target_consumption < 0:
                raise ValueError("Target consumption cannot be negative.")
            if baseline_consumption > 0:
                saved_liters = max(0.0, baseline_consumption - target_consumption)
                effective_pct = (saved_liters / baseline_consumption) * 100.0
                projected_consumption = target_consumption
            else:
                saved_liters = 0.0
                effective_pct = 0.0
                projected_consumption = 0.0
        else:
            raise ValueError("Either reduction_percentage or target_consumption must be provided.")

        # Annualization calculation
        multiplier = WaterSavingsService.PERIOD_MULTIPLIERS[normalized_period]
        daily_saved = saved_liters / multiplier
        annualized_liters_saved = round(daily_saved * 365.0, 2)

        # Monetary savings (rate per kiloliter = 1,000 liters)
        monetary_savings = None
        annualized_monetary_savings = None
        if rate_per_kiloliter is not None and rate_per_kiloliter > 0:
            monetary_savings = round((saved_liters / 1000.0) * rate_per_kiloliter, 2)
            annualized_monetary_savings = round((annualized_liters_saved / 1000.0) * rate_per_kiloliter, 2)

        return {
            "period": normalized_period,
            "baseline_consumption_liters": round(float(baseline_consumption), 2),
            "projected_consumption_liters": round(float(projected_consumption), 2),
            "estimated_liters_saved": round(float(saved_liters), 2),
            "estimated_percentage_reduction": round(float(effective_pct), 2),
            "estimated_monetary_savings": monetary_savings,
            "annualized_liters_saved": annualized_liters_saved,
            "annualized_monetary_savings": annualized_monetary_savings,
            "currency_symbol": currency_symbol if monetary_savings is not None else None,
            "rate_applied_per_kl": rate_per_kiloliter if monetary_savings is not None else None,
            "is_estimate": True,
            "disclaimer": (
                "Simulated savings are deterministic mathematical estimates based on user-supplied "
                "assumptions and historical patterns. They do not guarantee future utility billing reductions."
            )
        }
