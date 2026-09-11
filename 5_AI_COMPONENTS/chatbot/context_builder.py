"""
Smart Water Usage Advisor - Personalized Context Builder
Location: 5_AI_COMPONENTS/chatbot/context_builder.py
Phase 3C - Week 6 Implementation

Constructs a safe, structured, and privacy-compliant user water context
combining profile, telemetry, Phase 3A forecasting outputs, Phase 3B anomaly alerts,
and active conservation goals.
"""

import os
import sys
import pandas as pd
import numpy as np
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

@dataclass
class UserWaterContext:
    """Structured, anonymized snapshot of a user's water profile and operational state."""
    user_id: int
    first_name: str
    user_type: str
    city: str
    household_size: int
    property_type: str
    has_garden: bool
    water_source: str
    preferred_language: str
    meter_id: int
    meter_profile_name: str
    
    # Recent telemetry indicators
    has_sufficient_data: bool = True
    today_consumption_liters: float = 0.0
    weekly_avg_daily_liters: float = 0.0
    baseline_daily_liters: float = 0.0
    percent_change_vs_baseline: float = 0.0
    recent_trend: str = "stable"  # "increasing", "stable", "decreasing"
    
    # Category disaggregation
    categories_breakdown: Dict[str, float] = field(default_factory=dict)
    primary_consumption_category: str = "bathroom"
    
    # Phase 3B Operational Anomaly / Leak State
    has_active_anomaly: bool = False
    anomaly_type: str = "none"        # "leak", "surge", "low", "unusual_pattern", "none"
    anomaly_severity: str = "none"    # "critical", "high", "medium", "low", "none"
    anomaly_flow_rate: float = 0.0
    estimated_excess_liters: float = 0.0
    anomaly_explanation: str = ""
    anomaly_timestamp: str = ""
    
    # Phase 3A Forecasting Information
    forecast_available: bool = False
    predicted_7day_total_liters: float = 0.0
    predicted_daily_average_liters: float = 0.0
    predicted_peak_day: str = ""
    predicted_peak_volume_liters: float = 0.0
    forecast_spike_warning: bool = False
    
    # Active Conservation Goal
    has_active_goal: bool = False
    goal_type: str = ""
    goal_target_value: float = 0.0
    goal_target_unit: str = "liters"
    goal_progress_pct: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_summary_text(self) -> str:
        """Returns a concise, human-readable summary suitable for prompt injection."""
        lines = [
            f"User: {self.first_name} ({self.user_type}, {self.household_size} occupants in a {self.property_type})",
            f"Location: {self.city} | Garden: {'Yes' if self.has_garden else 'No'}",
            f"Meter Profile: {self.meter_profile_name}",
        ]
        if not self.has_sufficient_data:
            lines.append("Telemetry Status: Insufficient recent telemetry records available.")
            return "\n".join(lines)

        lines.extend([
            f"Recent Daily Usage: {self.today_consumption_liters:.1f} L (7-day average: {self.weekly_avg_daily_liters:.1f} L/day, Baseline: {self.baseline_daily_liters:.1f} L/day)",
            f"Usage Trend: {self.recent_trend.upper()} ({self.percent_change_vs_baseline:+.1f}% vs baseline)",
            f"Top Usage Category: {self.primary_consumption_category.capitalize()}"
        ])

        if self.has_active_anomaly:
            lines.append(
                f"ACTIVE ALERT: {self.anomaly_severity.upper()} {self.anomaly_type.upper()} "
                f"({self.anomaly_flow_rate:.1f} L/hr, ~{self.estimated_excess_liters:.1f} L excess) - {self.anomaly_explanation}"
            )
        else:
            lines.append("Active Alerts: None. Normal water flow within expected parameters.")

        if self.forecast_available:
            spike_str = " (Elevated peak anticipated!)" if self.forecast_spike_warning else ""
            lines.append(
                f"7-Day Forecast: {self.predicted_7day_total_liters:.0f} L total "
                f"(Avg: {self.predicted_daily_average_liters:.1f} L/day; Peak: {self.predicted_peak_volume_liters:.1f} L on {self.predicted_peak_day}){spike_str}"
            )

        if self.has_active_goal:
            lines.append(
                f"Conservation Goal: {self.goal_target_value} {self.goal_target_unit} "
                f"({self.goal_progress_pct:.1f}% progress towards target)"
            )

        return "\n".join(lines)


# Known seed profiles for fallback when database is not connected
DEFAULT_PROFILES = {
    1: {
        "first_name": "Sarah", "user_type": "household", "city": "Bengaluru",
        "household_size": 4, "property_type": "house", "has_garden": True,
        "water_source": "municipal", "preferred_language": "en", "meter_id": 1,
        "meter_profile_name": "Residential Single-Family"
    },
    2: {
        "first_name": "Marcus", "user_type": "institution", "city": "Pune",
        "household_size": 250, "property_type": "commercial", "has_garden": True,
        "water_source": "mixed", "preferred_language": "en", "meter_id": 2,
        "meter_profile_name": "Residential Multi-Family"
    },
    3: {
        "first_name": "Elena", "user_type": "municipal", "city": "Delhi",
        "household_size": 12000, "property_type": "apartment", "has_garden": True,
        "water_source": "municipal", "preferred_language": "en", "meter_id": 3,
        "meter_profile_name": "Commercial Office Facility"
    }
}


class UserWaterContextBuilder:
    """
    Assembles structured, validated UserWaterContext objects from telemetry,
    forecasting outputs, anomaly outputs, and profile metadata.
    """

    def __init__(
        self,
        telemetry_df: Optional[pd.DataFrame] = None,
        telemetry_csv_path: str = "4_DEVELOPMENT/data/generated/water_usage_data.csv"
    ):
        self.telemetry_df = telemetry_df
        if self.telemetry_df is None and os.path.isfile(telemetry_csv_path):
            try:
                self.telemetry_df = pd.read_csv(telemetry_csv_path)
                if "timestamp" in self.telemetry_df.columns:
                    self.telemetry_df["timestamp"] = pd.to_datetime(self.telemetry_df["timestamp"])
            except Exception as e:
                print(f"Warning: Could not load telemetry from {telemetry_csv_path}: {e}")
                self.telemetry_df = None

    def build_context(
        self,
        user_id: int = 1,
        meter_id: Optional[int] = None,
        operational_anomalies_df: Optional[pd.DataFrame] = None,
        forecast_output: Optional[Dict[str, Any]] = None,
        custom_goal: Optional[Dict[str, Any]] = None,
        as_of_timestamp: Optional[str] = None
    ) -> UserWaterContext:
        """
        Builds a comprehensive UserWaterContext for a specific user and meter.
        Strictly excludes ground-truth labels and credentials.
        """
        prof = DEFAULT_PROFILES.get(user_id, {
            "first_name": f"User_{user_id}", "user_type": "household", "city": "Bengaluru",
            "household_size": 3, "property_type": "house", "has_garden": False,
            "water_source": "municipal", "preferred_language": "en", "meter_id": user_id,
            "meter_profile_name": "Standard Meter"
        })
        m_id = meter_id if meter_id is not None else prof.get("meter_id", 1)

        ctx = UserWaterContext(
            user_id=user_id,
            first_name=prof["first_name"],
            user_type=prof["user_type"],
            city=prof["city"],
            household_size=prof["household_size"],
            property_type=prof["property_type"],
            has_garden=prof["has_garden"],
            water_source=prof["water_source"],
            preferred_language=prof["preferred_language"],
            meter_id=m_id,
            meter_profile_name=prof["meter_profile_name"]
        )

        # 1. Telemetry Aggregation
        if self.telemetry_df is not None and not self.telemetry_df.empty:
            m_data = self.telemetry_df[self.telemetry_df["meter_id"] == m_id].copy()
            if not pd.api.types.is_datetime64_any_dtype(m_data["timestamp"]):
                m_data["timestamp"] = pd.to_datetime(m_data["timestamp"])

            if as_of_timestamp:
                t_cutoff = pd.to_datetime(as_of_timestamp)
                m_data = m_data[m_data["timestamp"] <= t_cutoff]

            if len(m_data) >= 24:
                m_data = m_data.sort_values(by="timestamp").reset_index(drop=True)
                
                # Daily sums
                m_data["date"] = m_data["timestamp"].dt.date
                daily_sums = m_data.groupby("date")["hourly_consumption_liters"].sum()

                if len(daily_sums) > 0:
                    today_val = float(daily_sums.iloc[-1])
                    weekly_avg = float(daily_sums.tail(7).mean()) if len(daily_sums) >= 7 else today_val
                    baseline_val = float(daily_sums.tail(30).mean()) if len(daily_sums) >= 14 else weekly_avg
                    
                    pct_change = round(((today_val - baseline_val) / max(1.0, baseline_val)) * 100.0, 1)
                    trend = "increasing" if pct_change > 10.0 else ("decreasing" if pct_change < -10.0 else "stable")

                    ctx.today_consumption_liters = round(today_val, 1)
                    ctx.weekly_avg_daily_liters = round(weekly_avg, 1)
                    ctx.baseline_daily_liters = round(baseline_val, 1)
                    ctx.percent_change_vs_baseline = pct_change
                    ctx.recent_trend = trend
                    ctx.has_sufficient_data = True

                    # Estimated category breakdown based on profile
                    if prof["property_type"] == "house":
                        ctx.categories_breakdown = {
                            "bathroom": round(today_val * 0.38, 1),
                            "kitchen": round(today_val * 0.15, 1),
                            "laundry": round(today_val * 0.12, 1),
                            "garden": round(today_val * 0.20, 1) if prof["has_garden"] else 0.0,
                            "cleaning": round(today_val * 0.10, 1),
                            "other": round(today_val * 0.05, 1)
                        }
                    else:
                        ctx.categories_breakdown = {
                            "restrooms": round(today_val * 0.45, 1),
                            "cooling_hvac": round(today_val * 0.30, 1),
                            "cleaning": round(today_val * 0.15, 1),
                            "other": round(today_val * 0.10, 1)
                        }
                    ctx.primary_consumption_category = max(ctx.categories_breakdown, key=ctx.categories_breakdown.get)
            else:
                ctx.has_sufficient_data = False
        else:
            ctx.has_sufficient_data = False

        # 2. Integrate Phase 3B Operational Anomalies
        if operational_anomalies_df is not None and not operational_anomalies_df.empty:
            anom_sub = operational_anomalies_df[operational_anomalies_df["meter_id"] == m_id]
            if as_of_timestamp:
                anom_sub = anom_sub[anom_sub["timestamp"] <= pd.to_datetime(as_of_timestamp)]

            # Check if there is an active anomaly in recent hours
            active_anoms = anom_sub[anom_sub.get("is_anomaly", False)]
            if len(active_anoms) > 0:
                latest = active_anoms.iloc[-1]
                ctx.has_active_anomaly = True
                ctx.anomaly_type = str(latest.get("anomaly_type_detected", latest.get("anomaly_type", "leak")))
                ctx.anomaly_severity = str(latest.get("severity", "high"))
                ctx.anomaly_flow_rate = float(round(latest.get("hourly_consumption_liters", 0.0), 1))
                ctx.estimated_excess_liters = float(round(latest.get("deviation_liters", 0.0), 1))
                ctx.anomaly_explanation = str(latest.get("explanation", "Unusual flow pattern detected by operational monitor."))
                ctx.anomaly_timestamp = str(latest.get("timestamp", ""))

        # 3. Integrate Phase 3A Forecasting Output
        if forecast_output:
            ctx.forecast_available = True
            ctx.predicted_7day_total_liters = float(forecast_output.get("predicted_7day_total_liters", 0.0))
            ctx.predicted_daily_average_liters = round(ctx.predicted_7day_total_liters / 7.0, 1)
            ctx.predicted_peak_day = str(forecast_output.get("predicted_peak_day", ""))
            ctx.predicted_peak_volume_liters = float(forecast_output.get("predicted_peak_volume_liters", 0.0))
            
            # Check for elevated forecast spike
            if ctx.baseline_daily_liters > 0 and ctx.predicted_peak_volume_liters > (1.35 * ctx.baseline_daily_liters):
                ctx.forecast_spike_warning = True

        # 4. Integrate Active Goal
        if custom_goal:
            ctx.has_active_goal = True
            ctx.goal_type = custom_goal.get("goal_type", "percentage_reduction")
            ctx.goal_target_value = float(custom_goal.get("target_value", 20.0))
            ctx.goal_target_unit = str(custom_goal.get("target_unit", "%"))
            ctx.goal_progress_pct = float(custom_goal.get("progress_percentage", 65.0))
        elif user_id == 1:
            # Seed goal for demo User 1
            ctx.has_active_goal = True
            ctx.goal_type = "percentage_reduction"
            ctx.goal_target_value = 20.0
            ctx.goal_target_unit = "%"
            ctx.goal_progress_pct = 65.0

        return ctx
