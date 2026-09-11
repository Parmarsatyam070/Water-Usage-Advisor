"""
Smart Water Usage Advisor - Phase 7 Water Intelligence Unit Tests
Location: 6_TESTING/unit_tests/test_phase7_water_intelligence.py

Validates mathematical formulations, edge cases, deterministic behavior,
and disclosures across all Phase 7 Advanced Water Intelligence services.
"""

import os
import sys
import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

DEV_DIR = os.path.join(REPO_ROOT, "4_DEVELOPMENT")
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from backend.services.water_savings_service import WaterSavingsService
from backend.services.scenario_service import ScenarioAnalysisService
from backend.services.sustainability_score_service import SustainabilityScoreService
from backend.services.alert_history_service import AlertHistoryService
from backend.services.sdg6_service import SDG6Service
from backend.services.goal_recommendation_service import GoalRecommendationService
from backend.services.water_insights_service import WaterInsightsService
from backend.services.water_budget_service import WaterBudgetService
from backend.services.report_service import ReportService
from backend.services.system_monitoring_service import SystemMonitoringService


class TestWaterSavingsService:
    """Feature 1: Water Savings Simulator Tests"""

    def test_savings_simulator_percentage_valid(self):
        res = WaterSavingsService.simulate_savings(
            baseline_consumption=400.0,
            reduction_percentage=25.0,
            rate_per_kiloliter=40.0,
            period="daily"
        )
        assert res["baseline_consumption_liters"] == 400.0
        assert res["estimated_liters_saved"] == 100.0
        assert res["projected_consumption_liters"] == 300.0
        assert res["estimated_monetary_savings"] == 4.0  # (100 / 1000) * 40
        assert res["annualized_liters_saved"] == 36500.0
        assert res["annualized_monetary_savings"] == 1460.0
        assert res["is_estimate"] is True
        assert "estimates based on user-supplied assumptions" in res["disclaimer"]

    def test_savings_simulator_target_based(self):
        res = WaterSavingsService.simulate_savings(
            baseline_consumption=500.0,
            target_consumption=350.0,
            rate_per_kiloliter=50.0,
            period="daily"
        )
        assert res["estimated_liters_saved"] == 150.0
        assert res["estimated_percentage_reduction"] == 30.0
        assert res["projected_consumption_liters"] == 350.0

    def test_savings_simulator_zero_and_rate_omitted(self):
        res = WaterSavingsService.simulate_savings(
            baseline_consumption=0.0,
            reduction_percentage=10.0,
            rate_per_kiloliter=None
        )
        assert res["baseline_consumption_liters"] == 0.0
        assert res["estimated_liters_saved"] == 0.0
        assert res["estimated_monetary_savings"] is None

    def test_savings_simulator_invalid_inputs(self):
        with pytest.raises(ValueError, match="non-negative"):
            WaterSavingsService.simulate_savings(baseline_consumption=-10.0, reduction_percentage=10.0)

        with pytest.raises(ValueError, match="between 0.0 and 100.0"):
            WaterSavingsService.simulate_savings(baseline_consumption=100.0, reduction_percentage=120.0)

        with pytest.raises(ValueError, match="Invalid period"):
            WaterSavingsService.simulate_savings(baseline_consumption=100.0, reduction_percentage=10.0, period="hourly")


class TestScenarioAnalysisService:
    """Feature 2: What-If Scenario Analysis Tests"""

    def test_scenario_run_bathroom_reduction(self):
        service = ScenarioAnalysisService()
        res = service.run_scenario(
            user_id=1,
            scenario_name="Aerators Test",
            category="bathroom",
            percentage_change=-25.0,
            save_to_history=False
        )
        assert res["target_category"] == "bathroom"
        assert res["percentage_change"] == -25.0
        assert res["difference_daily_liters"] > 0
        assert res["is_simulation"] is True
        assert "analytical simulations intended for decision support" in res["disclaimer"]
        assert "bathroom" in res["scenario_breakdown"]
        # Ensure other categories remained constant
        assert res["scenario_breakdown"]["kitchen"] == res["baseline_breakdown"]["kitchen"]

    def test_scenario_invalid_category_and_bounds(self):
        service = ScenarioAnalysisService()
        with pytest.raises(ValueError, match="Invalid category"):
            service.run_scenario(user_id=1, scenario_name="Bad", category="swimming_pool", percentage_change=10.0)

        with pytest.raises(ValueError, match="Percentage change"):
            service.run_scenario(user_id=1, scenario_name="Bad", category="kitchen", percentage_change=-150.0)


class TestSustainabilityScoreService:
    """Feature 3: Sustainability Score Tests"""

    def test_sustainability_score_bounds_and_weights(self):
        service = SustainabilityScoreService()
        res = service.calculate_score(user_id=1)

        assert 0.0 <= res["sustainability_score"] <= 100.0
        assert res["grade"] in ["A", "B", "C", "D", "F"]

        comps = res["components"]
        assert "efficiency" in comps
        assert "anomaly_status" in comps
        assert "goal_progress" in comps
        assert "usage_trend" in comps

        # Check weights sum exactly to 1.0
        total_weight = sum([comps[k]["weight"] for k in comps])
        assert abs(total_weight - 1.0) < 1e-6

        # Check disclosures
        assert "decision-support metric" in res["methodology_disclosure"]
        assert "Project-configured benchmark" in comps["efficiency"]["benchmark_provenance"]

    def test_sustainability_score_single_class_penalty(self):
        service = SustainabilityScoreService()
        res = service.calculate_score(user_id=1)
        penalties = res["components"]["anomaly_status"]["penalties_applied"]
        # Penalties must be 25, 15, or 5 once per severity class
        assert penalties["critical"] in (0.0, 25.0)
        assert penalties["high"] in (0.0, 15.0)
        assert penalties["medium"] in (0.0, 5.0)


class TestAlertHistoryService:
    """Feature 4: Alert History & Resolution Tests"""

    def test_get_alert_history_filtering(self):
        service = AlertHistoryService()
        history = service.get_alert_history(user_id=1, status="ALL")
        assert "alerts" in history
        assert "counts" in history
        assert history["total"] >= 0

    def test_invalid_status_filter(self):
        service = AlertHistoryService()
        with pytest.raises(ValueError, match="Invalid status filter"):
            service.get_alert_history(user_id=1, status="UNKNOWN_STATUS")

    def test_update_alert_status_validation(self):
        service = AlertHistoryService()
        with pytest.raises(ValueError, match="Invalid status"):
            service.update_alert_status(alert_id=1, new_status="INVALID", user_id=1)


class TestSDG6Service:
    """Feature 5: SDG 6.4 Impact Tests"""

    def test_sdg6_impact_metrics_and_naming(self):
        service = SDG6Service()
        res = service.get_impact_metrics(user_id=1)

        assert "SDG 6.4" in res["sdg_target"]
        assert res["measured_telemetry"]["is_measured"] is True
        assert res["leak_impact"]["metric_name"] == "Estimated avoided leak volume after resolution"
        assert res["leak_impact"]["is_estimate"] is True
        assert "does not constitute official UN SDG certification" in res["methodology_disclosure"]


class TestGoalRecommendationService:
    """Feature 6: Smart Goal Recommendations Tests"""

    def test_goal_recommendations_who_floor(self):
        service = GoalRecommendationService()
        res = service.generate_recommendations(user_id=1)

        assert len(res["recommendations"]) == 3
        # Sanitary floor check: 4 occupants * 50 L/capita/day = 200 L/day
        assert res["sanitary_floor_lpd"] >= 200.0
        assert "WHO baseline guideline" in res["sanitary_floor_disclosure"]

        for rec in res["recommendations"]:
            if rec["goal_type"] == "daily_limit":
                assert rec["target_value"] >= res["sanitary_floor_lpd"]

    def test_adopt_goal_invalid(self):
        service = GoalRecommendationService()
        with pytest.raises(ValueError, match="Invalid goal_type"):
            service.adopt_goal(user_id=1, goal_type="unsupported_goal", target_value=100.0)

        with pytest.raises(ValueError, match="strictly positive"):
            service.adopt_goal(user_id=1, goal_type="daily_limit", target_value=-50.0)


class TestWaterInsightsService:
    """Feature 7: Trend & Pattern Insights Tests"""

    def test_insights_generation(self):
        service = WaterInsightsService()
        res = service.get_insights(user_id=1)

        assert res["user_id"] == 1
        assert res["total_insights_count"] >= 1
        assert "correlations and behavioral tendencies" in res["methodology_note"]

        # Check diurnal or temporal pattern present
        types = [item["type"] for item in res["insights"]]
        assert any("diurnal" in t or "temporal" in t for t in types)


class TestWaterBudgetService:
    """Feature 8: Water Budget Planner Tests"""

    def test_active_budget_burndown(self):
        service = WaterBudgetService()
        res = service.get_active_budget(user_id=1)

        assert res["target_liters"] > 0
        assert res["time_progress"]["total_days"] > 0
        assert "ideal_burn_rate_lpd" in res["consumption_status"]
        assert "is_overshoot_predicted" in res["forecast_projection"]
        assert isinstance(res["forecast_projection"]["is_overshoot_predicted"], bool)

    def test_set_budget_invalid(self):
        service = WaterBudgetService()
        with pytest.raises(ValueError, match="Invalid period"):
            service.set_budget(user_id=1, period="hourly", target_liters=100.0)

        with pytest.raises(ValueError, match="strictly positive"):
            service.set_budget(user_id=1, period="monthly", target_liters=-10.0)


class TestReportService:
    """Feature 9: Exportable Water Report Tests"""

    def test_csv_report_generation(self):
        service = ReportService()
        csv_text = service.generate_csv_report(user_id=1)

        assert "# SMART WATER USAGE ADVISOR - OFFICIAL WATER AUDIT REPORT" in csv_text
        assert "Date,Daily_Consumption_Liters" in csv_text
        assert "synthetic smart meter telemetry" in csv_text

    def test_executive_html_report_generation(self):
        service = ReportService()
        html_text = service.generate_executive_html_report(user_id=1)

        assert "<!DOCTYPE html>" in html_text
        assert "Smart Water Usage Advisor — Executive Audit Report" in html_text
        assert "Mandatory Methodology Disclosure:" in html_text


class TestSystemMonitoringService:
    """Feature 10: Admin System Monitoring Tests"""

    def test_system_summary_safe_metrics(self):
        service = SystemMonitoringService()
        summary = service.get_system_summary()

        assert summary["system_status"] in ["operational", "degraded"]
        assert summary["uptime_seconds"] >= 0
        assert "database" in summary
        assert "ai_models" in summary
        assert "predictive_forecasting" in summary["ai_models"]
        assert "anomaly_detection" in summary["ai_models"]

        # Ensure zero passwords or secrets leaked
        summary_str = str(summary).lower()
        for sensitive in ["password", "secret_key", "jwt_secret", "postgres://", "postgresql://"]:
            assert sensitive not in summary_str
