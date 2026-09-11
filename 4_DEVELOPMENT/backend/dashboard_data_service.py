"""
Smart Water Usage Advisor - Dashboard Data Service
Location: 4_DEVELOPMENT/backend/dashboard_data_service.py

Provides the central data access and synthesis layer for Phase 4 Dashboard & Web UI.
Bridges:
- Database (PostgreSQL / SQLite via db_config.py) & Synthetic Telemetry CSV
- Phase 3A Predictive Consumption Forecasting (Random Forest & Seasonal Naive)
- Phase 3B Anomaly & Leak Detection (Diurnal Baselines, Isolation Forest, Rules)
- Phase 3C AI Water Conservation Chatbot & Personalized Recommendation Engine

Returns structured, sanitized Data Transfer Objects (DTOs) for:
1. Summary / KPI Overview
2. Consumption Analytics (Hourly Diurnal, 30-Day Daily, Fixture Disaggregation)
3. 7-Day Forward Forecast
4. Anomaly & Leak Incident Center
5. Personalized Conservation Action Center
6. Conservation Goal & SDG 6 Progress
7. Chatbot Interaction

Enforces strict user isolation: User 1 never accesses Meter 2/3 data.
Never exposes database passwords, internal connection strings, or system prompt templates.
"""

import os
import sys
import json
from datetime import datetime, timedelta, date
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd

# Add root and module directories to sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

DEV_DIR = os.path.join(BASE_DIR, "4_DEVELOPMENT")
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

import ml_models

# Static User Profiles Mapping
USER_PROFILES = {
    1: {
        "user_id": 1,
        "meter_id": 1,
        "name": "Sarah Jenkins",
        "email": "sarah.jenkins@example.com",
        "user_type": "household",
        "property_type": "Single-Family House",
        "city": "Bengaluru",
        "country": "India",
        "household_size": 4,
        "property_area_sqm": 140.0,
        "has_garden": True,
        "has_pool": False,
        "water_source": "Municipal Water Supply",
        "conservation_goal_pct": 25.0,
        "regional_benchmark_lpd": 440.0,
        "currency_symbol": "₹",
        "cost_per_kiloliter": 45.0  # ₹45 per 1,000 liters
    },
    2: {
        "user_id": 2,
        "meter_id": 2,
        "name": "Marcus Vance",
        "email": "marcus.vance@campus.edu",
        "user_type": "institution",
        "property_type": "Multi-Family Residential (3 Units)",
        "city": "Pune",
        "country": "India",
        "household_size": 12,
        "property_area_sqm": 450.0,
        "has_garden": True,
        "has_pool": False,
        "water_source": "Mixed (Municipal + Groundwater)",
        "conservation_goal_pct": 20.0,
        "regional_benchmark_lpd": 1100.0,
        "currency_symbol": "₹",
        "cost_per_kiloliter": 55.0
    },
    3: {
        "user_id": 3,
        "meter_id": 3,
        "name": "Elena Rostova",
        "email": "elena.rostova@metro.gov",
        "user_type": "municipal",
        "property_type": "Commercial Office Complex",
        "city": "Delhi",
        "country": "India",
        "household_size": 85,
        "property_area_sqm": 2800.0,
        "has_garden": False,
        "has_pool": False,
        "water_source": "Municipal Commercial Supply",
        "conservation_goal_pct": 15.0,
        "regional_benchmark_lpd": 1800.0,
        "currency_symbol": "₹",
        "cost_per_kiloliter": 65.0
    }
}


class DashboardDataService:
    """
    Central Data Service providing aggregated DTO payloads for the Phase 4 UI.
    Maintains an in-memory cached model and telemetry cache for rapid browser interactions.
    """

    def __init__(self, telemetry_csv_path: Optional[str] = None):
        if telemetry_csv_path is None:
            telemetry_csv_path = os.path.join(BASE_DIR, "4_DEVELOPMENT", "data", "generated", "water_usage_data.csv")
            if not os.path.isfile(telemetry_csv_path):
                alt_path = os.path.join(BASE_DIR, "2_RESEARCH_DATA", "synthetic_water_usage.csv")
                if os.path.isfile(alt_path):
                    telemetry_csv_path = alt_path

        self.telemetry_csv_path = telemetry_csv_path
        self._raw_telemetry: Optional[pd.DataFrame] = None
        self._daily_telemetry: Optional[pd.DataFrame] = None
        self._anomaly_cache: Dict[int, pd.DataFrame] = {}
        self._forecast_cache: Dict[int, Dict[str, Any]] = {}
        self._forecaster = None
        self._detector = None
        self._chatbot = None

    def _load_telemetry(self) -> pd.DataFrame:
        """Loads and pre-caches the authoritative hourly smart meter telemetry."""
        if self._raw_telemetry is None:
            if not os.path.isfile(self.telemetry_csv_path):
                raise FileNotFoundError(f"Authoritative telemetry CSV not found at: {self.telemetry_csv_path}")
            df = pd.read_csv(self.telemetry_csv_path)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df["date"] = df["timestamp"].dt.date
            # Harmonize consumption column
            if "hourly_consumption_liters" in df.columns and "consumption_liters" not in df.columns:
                df["consumption_liters"] = df["hourly_consumption_liters"]
            elif "consumption_liters" in df.columns and "hourly_consumption_liters" not in df.columns:
                df["hourly_consumption_liters"] = df["consumption_liters"]

            self._raw_telemetry = df

            # Pre-aggregate to daily
            daily = df.groupby(["meter_id", "date"]).agg(
                daily_consumption_liters=("consumption_liters", "sum"),
                temperature_celsius=("temperature_celsius", "mean") if "temperature_celsius" in df.columns else ("meter_id", lambda x: 25.0)
            ).reset_index()
            daily["user_id"] = daily["meter_id"]
            self._daily_telemetry = daily

        return self._raw_telemetry

    def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """Returns safe user metadata or defaults to User 1 if not found."""
        return USER_PROFILES.get(user_id, USER_PROFILES[1])

    def get_summary(self, user_id: int) -> Dict[str, Any]:
        """
        Synthesizes Section A: KPI Summary Cards.
        - Today's Usage (Liters & delta % vs same day last week)
        - 7-Day Forecast Average (Liters/day & trend)
        - Monthly Financial & Volumetric Savings
        - Conservation Goal Progress (%)
        """
        profile = self.get_user_profile(user_id)
        meter_id = profile["meter_id"]
        df = self._load_telemetry()
        meter_daily = self._daily_telemetry[self._daily_telemetry["meter_id"] == meter_id].sort_values("date")

        if len(meter_daily) == 0:
            return {
                "user": profile,
                "today_usage_liters": 0.0,
                "today_delta_pct": 0.0,
                "forecast_avg_liters_day": 0.0,
                "forecast_trend_pct": 0.0,
                "monthly_water_saved_liters": 0.0,
                "monthly_financial_saved": 0.0,
                "active_alert_count": 0,
                "goal_progress_pct": 0.0,
                "goal_target_pct": profile["conservation_goal_pct"],
                "currency_symbol": profile["currency_symbol"]
            }

        # Today's usage is latest available daily record
        today_usage = float(meter_daily["daily_consumption_liters"].iloc[-1])
        # Compare with 7 days prior for weekly seasonal delta
        past_week_usage = float(meter_daily["daily_consumption_liters"].iloc[-8]) if len(meter_daily) >= 8 else today_usage
        today_delta_pct = round(((today_usage - past_week_usage) / past_week_usage * 100.0), 1) if past_week_usage > 0 else 0.0

        # Forecast Average from Phase 3A
        forecast_dto = self.get_forecast(user_id)
        forecast_avg = forecast_dto.get("forecast_avg_liters_day", today_usage)
        historical_30d_avg = float(meter_daily["daily_consumption_liters"].tail(30).mean())
        forecast_trend_pct = round(((forecast_avg - historical_30d_avg) / historical_30d_avg * 100.0), 1) if historical_30d_avg > 0 else 0.0

        # Baseline comparison & Savings
        benchmark_lpd = profile["regional_benchmark_lpd"]
        current_lpd = float(meter_daily["daily_consumption_liters"].tail(7).mean())
        daily_diff = max(0.0, benchmark_lpd - current_lpd)
        monthly_water_saved = round(daily_diff * 30.0, 1)
        cost_per_l = profile["cost_per_kiloliter"] / 1000.0
        monthly_financial_saved = round(monthly_water_saved * cost_per_l, 2)

        # Active Alerts count from Phase 3B
        anomalies_dto = self.get_anomalies(user_id)
        active_alert_count = anomalies_dto.get("active_alert_count", 0)

        # Goal Progress
        target_pct = profile["conservation_goal_pct"]
        # Calculated reduction from baseline
        achieved_reduction_pct = min(100.0, max(0.0, round((daily_diff / benchmark_lpd * 100.0), 1)))
        goal_progress_pct = min(100.0, round((achieved_reduction_pct / target_pct * 100.0), 1)) if target_pct > 0 else 0.0

        return {
            "user": profile,
            "today_usage_liters": round(today_usage, 1),
            "today_delta_pct": today_delta_pct,
            "forecast_avg_liters_day": round(forecast_avg, 1),
            "forecast_trend_pct": forecast_trend_pct,
            "monthly_water_saved_liters": monthly_water_saved,
            "monthly_financial_saved": monthly_financial_saved,
            "active_alert_count": active_alert_count,
            "goal_progress_pct": goal_progress_pct,
            "goal_target_pct": target_pct,
            "currency_symbol": profile["currency_symbol"]
        }

    def get_consumption(self, user_id: int, time_range: str = "30d") -> Dict[str, Any]:
        """
        Synthesizes Section B: Consumption Analytics.
        - 24-Hour Diurnal Hourly Curve (Median vs Current Day)
        - 30-Day Daily Consumption History (with 7-day rolling average)
        - Peak Usage Hours
        - Disaggregated Fixture Breakdown (Showers, Toilets, Outdoor, Kitchen, Laundry)
        - Regional Benchmark Comparison
        """
        profile = self.get_user_profile(user_id)
        meter_id = profile["meter_id"]
        raw_df = self._load_telemetry()
        meter_hourly = raw_df[raw_df["meter_id"] == meter_id].copy()

        # 1. 24-Hour Diurnal Profile
        meter_hourly["hour"] = meter_hourly["timestamp"].dt.hour
        diurnal_stats = meter_hourly.groupby("hour")["consumption_liters"].agg(
            median_liters="median",
            mean_liters="mean",
            max_liters="max"
        ).reset_index()

        # Recent 24h reading
        latest_24h = meter_hourly.sort_values("timestamp").tail(24)
        diurnal_hours = [f"{h:02d}:00" for h in range(24)]
        diurnal_baseline = [round(float(v), 2) for v in diurnal_stats["median_liters"].values]
        recent_24h_map = {row["hour"]: round(float(row["consumption_liters"]), 2) for _, row in latest_24h.iterrows()}
        diurnal_recent = [recent_24h_map.get(h, diurnal_baseline[h]) for h in range(24)]

        # Peak hours determination
        peak_morning_hour = int(diurnal_stats.iloc[6:10]["mean_liters"].idxmax()) if len(diurnal_stats) >= 10 else 8
        peak_evening_hour = int(diurnal_stats.iloc[18:22]["mean_liters"].idxmax()) if len(diurnal_stats) >= 22 else 19

        # 2. Daily Time-Series (Last 30 Days)
        meter_daily = self._daily_telemetry[self._daily_telemetry["meter_id"] == meter_id].sort_values("date").tail(30).copy()
        meter_daily["moving_avg_7d"] = meter_daily["daily_consumption_liters"].rolling(7, min_periods=1).mean()

        daily_labels = [str(d) for d in meter_daily["date"].values]
        daily_values = [round(float(v), 1) for v in meter_daily["daily_consumption_liters"].values]
        moving_avg_values = [round(float(v), 1) for v in meter_daily["moving_avg_7d"].values]

        # 3. Disaggregated End-Use Estimates
        # Profile-informed physical breakdown percentages
        if profile["user_type"] == "household":
            disaggregation = {
                "Showers & Baths": 35.0,
                "Toilets": 24.0,
                "Garden & Outdoor": 18.0 if profile["has_garden"] else 5.0,
                "Kitchen & Dishes": 13.0,
                "Laundry": 10.0
            }
        elif profile["user_type"] == "institution":
            disaggregation = {
                "Restrooms & Flushometers": 45.0,
                "Cooling & HVAC": 25.0,
                "Kitchen & Dining Hall": 15.0,
                "Landscape & Grounds": 10.0,
                "Maintenance & Cleaning": 5.0
            }
        else:
            disaggregation = {
                "Cooling Towers & Chiller Plants": 48.0,
                "Sanitary Restrooms": 30.0,
                "Cafeteria Facilities": 12.0,
                "Landscape Irrigation": 6.0,
                "Boiler & Domestic Hot Water": 4.0
            }

        # Compute volume per category from recent daily mean
        mean_daily_l = float(np.mean(daily_values)) if daily_values else 300.0
        disaggregated_liters = {cat: round(mean_daily_l * (pct / 100.0), 1) for cat, pct in disaggregation.items()}

        return {
            "meter_id": meter_id,
            "diurnal_hours": diurnal_hours,
            "diurnal_baseline": diurnal_baseline,
            "diurnal_recent": diurnal_recent,
            "peak_morning_hour": f"{peak_morning_hour:02d}:00",
            "peak_evening_hour": f"{peak_evening_hour:02d}:00",
            "daily_labels": daily_labels,
            "daily_values": daily_values,
            "moving_avg_7d": moving_avg_values,
            "disaggregated_pct": disaggregation,
            "disaggregated_liters": disaggregated_liters,
            "regional_benchmark_lpd": profile["regional_benchmark_lpd"],
            "current_7d_avg_lpd": round(float(np.mean(daily_values[-7:])), 1) if len(daily_values) >= 7 else round(mean_daily_l, 1)
        }

    def get_forecast(self, user_id: int) -> Dict[str, Any]:
        """
        Synthesizes Section C: Predictive Consumption Forecasting (Phase 3A).
        Calls inference.generate_7day_forecast with model attribution and surge analysis.
        """
        profile = self.get_user_profile(user_id)
        meter_id = profile["meter_id"]

        if meter_id in self._forecast_cache:
            return self._forecast_cache[meter_id]

        df = self._load_telemetry()
        meter_daily = self._daily_telemetry[self._daily_telemetry["meter_id"] == meter_id].sort_values("date")

        try:
            # Load forecaster via ml_models wrapper
            forecaster = ml_models.load_model()
            from predictive_models.inference import generate_7day_forecast
            raw_forecast = generate_7day_forecast(
                daily_df=self._daily_telemetry,
                forecaster=forecaster,
                meter_id=meter_id,
                seed=42
            )

            step_forecasts = raw_forecast.get("step_forecasts", [])
            dates = [step["forecast_date"] for step in step_forecasts]
            predictions = [round(float(step["predicted_consumption_liters"]), 1) for step in step_forecasts]
            baseline_7d = [round(float(step.get("seasonal_naive_7d_baseline", predictions[0])), 1) for step in step_forecasts]
            lower_bounds = [round(float(step.get("confidence_interval_lower", predictions[i] * 0.9)), 1) for i, step in enumerate(step_forecasts)]
            upper_bounds = [round(float(step.get("confidence_interval_upper", predictions[i] * 1.1)), 1) for i, step in enumerate(step_forecasts)]

            avg_forecast = float(np.mean(predictions)) if predictions else 0.0
            peak_day_idx = int(np.argmax(predictions)) if predictions else 0
            peak_day_date = dates[peak_day_idx] if dates else ""
            peak_day_vol = predictions[peak_day_idx] if predictions else 0.0

            result = {
                "meter_id": meter_id,
                "forecast_dates": dates,
                "predicted_liters": predictions,
                "baseline_liters": baseline_7d,
                "confidence_lower": lower_bounds,
                "confidence_upper": upper_bounds,
                "forecast_avg_liters_day": round(avg_forecast, 1),
                "peak_day_date": peak_day_date,
                "peak_day_liters": peak_day_vol,
                "model_name": "Random Forest Regressor (Phase 3A)",
                "benchmark_name": "Seasonal Naive 7-Day Baseline",
                "disclaimer": "Model Projection: Forward predictions are based on historical telemetry and seasonal patterns. Real-world usage is subject to weather fluctuations and occupant behavior."
            }
        except Exception as e:
            # Fallback based on seasonal naive extrapolation
            last_7 = meter_daily.tail(7)
            last_date = meter_daily["date"].max()
            dates = [(last_date + timedelta(days=i + 1)).isoformat() for i in range(7)]
            predictions = [round(float(v), 1) for v in last_7["daily_consumption_liters"].values] if len(last_7) == 7 else [350.0] * 7
            result = {
                "meter_id": meter_id,
                "forecast_dates": dates,
                "predicted_liters": predictions,
                "baseline_liters": predictions,
                "confidence_lower": [round(p * 0.9, 1) for p in predictions],
                "confidence_upper": [round(p * 1.1, 1) for p in predictions],
                "forecast_avg_liters_day": round(float(np.mean(predictions)), 1),
                "peak_day_date": dates[0] if dates else "",
                "peak_day_liters": predictions[0] if predictions else 0.0,
                "model_name": "Seasonal Naive 7-Day Baseline (Phase 3A Fallback)",
                "benchmark_name": "Historical Mean",
                "disclaimer": "Model Projection: Based on historical seasonal extrapolation."
            }

        self._forecast_cache[meter_id] = result
        return result

    def get_anomalies(self, user_id: int) -> Dict[str, Any]:
        """
        Synthesizes Section D: Anomaly & Leak Incident Center (Phase 3B).
        Executes hybrid detector across telemetry and structures incident cards.
        """
        profile = self.get_user_profile(user_id)
        meter_id = profile["meter_id"]

        if meter_id in self._anomaly_cache:
            detected_df = self._anomaly_cache[meter_id]
        else:
            raw_df = self._load_telemetry()
            meter_df = raw_df[raw_df["meter_id"] == meter_id].copy()
            detector = ml_models.load_anomaly_detector()
            detected_df = detector.detect(meter_df)
            self._anomaly_cache[meter_id] = detected_df

        # Filter detected anomalous rows
        anom_rows = detected_df[detected_df["is_anomaly"] == 1].sort_values("timestamp", ascending=False)
        total_anomalies = len(anom_rows)

        incidents = []
        # Group adjacent consecutive anomaly hours into physical incidents
        current_incident = None
        for _, row in anom_rows.iterrows():
            ts = str(row["timestamp"])
            atype = str(row.get("anomaly_type_detected", "leak"))
            sev = str(row.get("severity", "medium"))
            score = round(float(row.get("isolation_score", 0.75)), 3)
            expl = str(row.get("explanation", "Abnormal flow rate detected relative to diurnal baseline."))

            # Recommended action per anomaly type
            if atype == "leak":
                rec_action = "Conduct toilet flapper dye test; verify exterior irrigation valves; consult plumber if continuous."
            elif atype == "surge":
                rec_action = "CRITICAL: Inspect main supply line for pipe burst; verify high-pressure valves immediately."
            elif atype == "unusual_pattern":
                rec_action = "Check off-hours automated timer settings (e.g. nocturnal irrigation, HVAC chillers)."
            else:
                rec_action = "Inspect meter for potential sensor blockage, power failure, or unoccupied shutdown."

            incidents.append({
                "incident_id": f"INC-{meter_id}-{len(incidents) + 1}",
                "timestamp": ts,
                "meter_id": meter_id,
                "anomaly_type": atype,
                "severity": sev,
                "anomaly_score": score,
                "flow_rate_lph": round(float(row["consumption_liters"]), 1),
                "explanation": expl,
                "recommended_action": rec_action,
                "is_active": len(incidents) < 2  # Mark most recent as active
            })

            if len(incidents) >= 10:
                break

        # Check if there is an active high or critical alert
        active_critical = any(inc["is_active"] and inc["severity"] in ("critical", "high") for inc in incidents)
        primary_alert = incidents[0] if incidents else None

        return {
            "meter_id": meter_id,
            "active_alert_count": len([inc for inc in incidents if inc["is_active"]]),
            "has_critical_alert": active_critical,
            "primary_alert": primary_alert,
            "incidents": incidents,
            "total_detected_hours": total_anomalies
        }

    def get_recommendations(self, user_id: int) -> Dict[str, Any]:
        """
        Synthesizes Section E: Personalized Conservation Action Center (Phase 3C).
        Calls Phase 3C PersonalizedRecommendationEngine based on active leaks and profile.
        """
        profile = self.get_user_profile(user_id)
        meter_id = profile["meter_id"]
        anomalies_dto = self.get_anomalies(user_id)
        forecast_dto = self.get_forecast(user_id)

        # Build operational anomaly DataFrame for context builder
        op_anom_df = None
        if anomalies_dto.get("incidents"):
            rows = []
            for inc in anomalies_dto["incidents"]:
                rows.append({
                    "meter_id": meter_id,
                    "timestamp": inc["timestamp"],
                    "anomaly_type_detected": inc["anomaly_type"],
                    "severity": inc["severity"],
                    "is_anomaly": True,
                    "explanation": inc["explanation"]
                })
            op_anom_df = pd.DataFrame(rows)

        chatbot = ml_models.load_chatbot(telemetry_df=self._load_telemetry())
        context = chatbot.context_builder.build_context(
            user_id=user_id,
            meter_id=meter_id,
            operational_anomalies_df=op_anom_df,
            forecast_output=forecast_dto,
            custom_goal={
                "target_percentage": profile["conservation_goal_pct"],
                "baseline_liters_day": profile["regional_benchmark_lpd"]
            }
        )
        raw_recs = chatbot.recommendation_engine.generate_recommendations(context, max_recommendations=5)

        cost_per_l = profile["cost_per_kiloliter"] / 1000.0
        recommendations = []
        for r in raw_recs:
            r_dict = r.to_dict()
            savings_lpd = float(r_dict.get("estimated_savings_liters", 50.0))
            r_dict["estimated_savings_liters_day"] = savings_lpd
            monthly_fin = round(savings_lpd * 30.0 * cost_per_l, 2)
            r_dict["monthly_financial_savings"] = monthly_fin
            r_dict["currency_symbol"] = profile["currency_symbol"]
            recommendations.append(r_dict)

        total_potential_savings_lpd = sum(r["estimated_savings_liters_day"] for r in recommendations)
        total_potential_financial = round(sum(r["monthly_financial_savings"] for r in recommendations), 2)

        return {
            "meter_id": meter_id,
            "total_potential_savings_lpd": round(total_potential_savings_lpd, 1),
            "total_potential_financial": total_potential_financial,
            "currency_symbol": profile["currency_symbol"],
            "recommendations": recommendations
        }

    def get_goals(self, user_id: int) -> Dict[str, Any]:
        """
        Synthesizes Section G: Conservation Goal & SDG 6 Progress.
        """
        profile = self.get_user_profile(user_id)
        summary = self.get_summary(user_id)

        target_pct = profile["conservation_goal_pct"]
        progress_pct = summary["goal_progress_pct"]
        benchmark_lpd = profile["regional_benchmark_lpd"]
        current_lpd = summary["today_usage_liters"]

        # Target consumption volume
        target_volume_lpd = round(benchmark_lpd * (1.0 - (target_pct / 100.0)), 1)
        volume_remaining_lpd = max(0.0, round(current_lpd - target_volume_lpd, 1))

        # Assume monthly billing cycle with 18 days remaining
        days_remaining = 18

        return {
            "user_id": user_id,
            "meter_id": profile["meter_id"],
            "target_reduction_pct": target_pct,
            "achieved_progress_pct": progress_pct,
            "baseline_volume_lpd": benchmark_lpd,
            "target_volume_lpd": target_volume_lpd,
            "current_volume_lpd": current_lpd,
            "volume_remaining_lpd": volume_remaining_lpd,
            "days_remaining_in_cycle": days_remaining,
            "is_on_track": progress_pct >= 80.0,
            "sdg_target": "SDG 6.4 (Substantially increase water-use efficiency across all sectors)"
        }

    def handle_chat(self, user_id: int, user_message: str) -> Dict[str, Any]:
        """
        Synthesizes Section F: AI Water Conservation Chatbot Interaction.
        Calls ml_models.ask_water_advisor with full context grounding.
        """
        profile = self.get_user_profile(user_id)
        anomalies_dto = self.get_anomalies(user_id)
        forecast_dto = self.get_forecast(user_id)

        # Build operational anomaly DataFrame for grounding
        op_anom_df = None
        if anomalies_dto.get("incidents"):
            rows = []
            for inc in anomalies_dto["incidents"]:
                rows.append({
                    "meter_id": profile["meter_id"],
                    "timestamp": inc["timestamp"],
                    "anomaly_type_detected": inc["anomaly_type"],
                    "severity": inc["severity"],
                    "is_anomaly": True,
                    "explanation": inc["explanation"]
                })
            op_anom_df = pd.DataFrame(rows)

        # Query chatbot wrapper
        response = ml_models.ask_water_advisor(
            user_message=user_message,
            user_id=user_id,
            meter_id=profile["meter_id"],
            operational_anomalies_df=op_anom_df,
            forecast_output=forecast_dto,
            custom_goal={
                "target_percentage": profile["conservation_goal_pct"],
                "baseline_liters_day": profile["regional_benchmark_lpd"]
            }
        )

        # Harmonize key names for frontend client compatibility
        if "answer" in response:
            response["conversational_response"] = response["answer"]
        elif "conversational_response" in response:
            response["answer"] = response["conversational_response"]

        if "evidence" in response:
            response["source_citations"] = response["evidence"]
        elif "source_citations" in response:
            response["evidence"] = response["source_citations"]

        response["safety_disclaimer"] = response.get("plumbing_safety_note") or response.get("safety_disclaimer") or ""
        response["plumbing_safety_note"] = response["safety_disclaimer"]

        return response


# Global singleton instance
_data_service = DashboardDataService()

def get_data_service() -> DashboardDataService:
    """Returns the central DashboardDataService instance."""
    return _data_service
