"""
Smart Water Usage Advisor - Trend & Pattern Insights Service
Phase 7 - Advanced Water Intelligence & Impact Features
Location: 4_DEVELOPMENT/backend/services/water_insights_service.py

Provides transparent statistical pattern analysis:
- Weekday vs. Weekend consumption variation
- Diurnal peak distribution (morning vs. evening vs. baseflow)
- Fixture category skew detection (>45% dominant category)
- Forecast-vs-actual deviation summary

Strictly notes that correlations describe observed behavioral patterns, not proven causation.
"""

from typing import Dict, Any, List
import numpy as np
import pandas as pd
from backend.dashboard_data_service import get_data_service


class WaterInsightsService:
    """
    Statistical analyzer identifying actionable behavioral and temporal patterns.
    """

    METHODOLOGY_NOTE = (
        "Statistical patterns describe observed empirical usage variations in smart meter telemetry. "
        "They indicate correlations and behavioral tendencies rather than confirmed causal factors."
    )

    def __init__(self, data_service=None):
        self.data_service = data_service or get_data_service()

    def get_insights(self, user_id: int) -> Dict[str, Any]:
        """
        Generates statistical insights and pattern flags for the user.
        """
        profile = self.data_service.get_user_profile(user_id)
        meter_id = profile["meter_id"]
        raw_df = self.data_service._load_telemetry()
        meter_df = raw_df[raw_df["meter_id"] == meter_id].copy()

        if len(meter_df) == 0:
            return {
                "user_id": user_id,
                "insights": [],
                "methodology_note": self.METHODOLOGY_NOTE
            }

        insights = []

        # 1. Weekday vs Weekend Analysis
        meter_df["day_of_week"] = meter_df["timestamp"].dt.dayofweek
        meter_df["is_weekend"] = meter_df["day_of_week"] >= 5
        daily = meter_df.groupby(["date", "is_weekend"])["consumption_liters"].sum().reset_index()

        weekday_daily = daily[~daily["is_weekend"]]["consumption_liters"]
        weekend_daily = daily[daily["is_weekend"]]["consumption_liters"]

        weekday_avg = float(weekday_daily.mean()) if len(weekday_daily) > 0 else 0.0
        weekend_avg = float(weekend_daily.mean()) if len(weekend_daily) > 0 else 0.0

        if weekday_avg > 0:
            weekend_delta_pct = round(((weekend_avg - weekday_avg) / weekday_avg) * 100.0, 1)
        else:
            weekend_delta_pct = 0.0

        if abs(weekend_delta_pct) >= 10.0:
            direction = "higher" if weekend_delta_pct > 0 else "lower"
            insights.append({
                "insight_id": "ins_weekend_variance",
                "type": "temporal_pattern",
                "title": f"Weekend Consumption is {abs(weekend_delta_pct)}% {direction.title()}",
                "description": (
                    f"Average weekend consumption is {weekend_avg:.1f} L/day compared to {weekday_avg:.1f} L/day on weekdays. "
                    f"This typically reflects home occupancy, laundry cycles, or garden watering."
                ),
                "metrics": {
                    "weekday_avg_lpd": round(weekday_avg, 1),
                    "weekend_avg_lpd": round(weekend_avg, 1),
                    "delta_percentage": weekend_delta_pct
                },
                "significance": "medium" if abs(weekend_delta_pct) < 25 else "high"
            })

        # 2. Diurnal Peak Analysis (Morning: 06-09, Evening: 18-21, Night: 00-05, Daytime: 10-17)
        meter_df["hour"] = meter_df["timestamp"].dt.hour
        hourly_means = meter_df.groupby("hour")["consumption_liters"].mean()

        morning_mask = (meter_df["hour"] >= 6) & (meter_df["hour"] <= 9)
        evening_mask = (meter_df["hour"] >= 18) & (meter_df["hour"] <= 21)
        night_mask = (meter_df["hour"] >= 0) & (meter_df["hour"] <= 5)

        morning_avg_hourly = float(meter_df[morning_mask]["consumption_liters"].mean())
        evening_avg_hourly = float(meter_df[evening_mask]["consumption_liters"].mean())
        night_avg_hourly = float(meter_df[night_mask]["consumption_liters"].mean())

        peak_period = "Morning (06:00 - 09:00)" if morning_avg_hourly >= evening_avg_hourly else "Evening (18:00 - 21:00)"
        peak_rate = max(morning_avg_hourly, evening_avg_hourly)

        insights.append({
            "insight_id": "ins_diurnal_peak",
            "type": "diurnal_distribution",
            "title": f"Primary Diurnal Peak Occurs in the {peak_period.split()[0]}",
            "description": (
                f"Peak hourly intensity averages {peak_rate:.1f} L/hour during {peak_period}, "
                f"while baseline overnight flow averages {night_avg_hourly:.1f} L/hour."
            ),
            "metrics": {
                "morning_peak_avg_lph": round(morning_avg_hourly, 1),
                "evening_peak_avg_lph": round(evening_avg_hourly, 1),
                "overnight_baseflow_lph": round(night_avg_hourly, 1),
                "dominant_peak_window": peak_period
            },
            "significance": "low" if night_avg_hourly < 5.0 else "high"
        })

        # Overnight baseline flow warning (possible slow fixture leak)
        if night_avg_hourly >= 12.0:
            insights.append({
                "insight_id": "ins_overnight_baseflow",
                "type": "leak_risk",
                "title": "Elevated Overnight Baseflow Detected",
                "description": (
                    f"Mean overnight consumption (00:00 - 05:00) is {night_avg_hourly:.1f} L/hour. "
                    f"Continuous nighttime flow without pause strongly suggests silent toilet flapper leaks or irrigation drip."
                ),
                "metrics": {
                    "overnight_lph": round(night_avg_hourly, 1),
                    "normal_threshold_lph": 5.0
                },
                "significance": "critical"
            })

        # 3. Category Skew Analysis (>45% dominant fixture)
        consumption_dto = self.data_service.get_consumption(user_id, time_range="30d")
        disagg_pct = consumption_dto.get("disaggregated_pct", {})
        for cat, pct in disagg_pct.items():
            if pct >= 45.0:
                insights.append({
                    "insight_id": f"ins_skew_{cat}",
                    "type": "category_concentration",
                    "title": f"High Consumption Concentration in {cat.capitalize()} ({pct:.0f}%)",
                    "description": (
                        f"{cat.capitalize()} accounts for {pct:.1f}% of total household water use. "
                        f"Targeting conservation efforts on this single category will yield the highest return."
                    ),
                    "metrics": {
                        "category": cat,
                        "percentage_of_total": pct
                    },
                    "significance": "medium"
                })

        # 4. Forecast Stability Summary
        summary = self.data_service.get_summary(user_id)
        forecast_trend = float(summary.get("forecast_trend_pct", 0.0))
        insights.append({
            "insight_id": "ins_forecast_trend",
            "type": "predictive_outlook",
            "title": f"7-Day Consumption Trajectory: {forecast_trend:+.1f}% vs Historical Mean",
            "description": (
                "Forward model projections indicate expected consumption trajectory based on seasonal patterns. "
                "Projected variations help prepare for seasonal billing changes."
            ),
            "metrics": {
                "forecast_trend_pct": forecast_trend,
                "forecast_avg_lpd": summary.get("forecast_avg_liters_day", 0.0)
            },
            "significance": "low" if abs(forecast_trend) < 5 else "medium"
        })

        return {
            "user_id": user_id,
            "meter_id": meter_id,
            "total_insights_count": len(insights),
            "insights": insights,
            "methodology_note": self.METHODOLOGY_NOTE
        }
