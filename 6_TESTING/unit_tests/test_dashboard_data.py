"""
Unit Test Suite: Phase 4 Dashboard Data Service & Local Server Endpoints
Location: 6_TESTING/unit_tests/test_dashboard_data.py

Validates:
1. Summary / KPI Overview DTO structure, types, and values.
2. Consumption Analytics 24h diurnal curve and 30d daily aggregation.
3. Phase 3A 7-Day Forecasting DTO format and confidence bounds.
4. Phase 3B Anomaly & Leak Incident Center transformation and severities.
5. Phase 3C Personalized Conservation Action Center recommendations.
6. User Persona Isolation: Meter 1, Meter 2, and Meter 3 data remain segregated.
7. Resilience to unconfigured/empty user IDs.
8. Chatbot interaction round-trip via dashboard data service.
9. Python standard-library HTTP server request routing and JSON responses.
"""

import os
import sys
import json
import threading
import time
import urllib.request
import urllib.error
import pytest

# Ensure root and 4_DEVELOPMENT are in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

DEV_DIR = os.path.join(BASE_DIR, "4_DEVELOPMENT")
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from backend.dashboard_data_service import get_data_service, DashboardDataService
from run_dashboard import create_dashboard_server


@pytest.fixture(scope="module")
def data_service():
    """Provides the singleton DashboardDataService instance."""
    return get_data_service()


def test_dashboard_summary_dto(data_service):
    """Verifies structure and types of the KPI Overview summary DTO."""
    summary = data_service.get_summary(user_id=1)
    assert isinstance(summary, dict)
    assert "user" in summary
    assert summary["user"]["user_id"] == 1
    assert summary["user"]["name"] == "Sarah Jenkins"

    # Numeric fields
    assert isinstance(summary["today_usage_liters"], (int, float))
    assert summary["today_usage_liters"] > 0
    assert isinstance(summary["today_delta_pct"], (int, float))
    assert isinstance(summary["forecast_avg_liters_day"], (int, float))
    assert summary["forecast_avg_liters_day"] > 0
    assert isinstance(summary["monthly_water_saved_liters"], (int, float))
    assert isinstance(summary["monthly_financial_saved"], (int, float))
    assert isinstance(summary["active_alert_count"], int)
    assert 0.0 <= summary["goal_progress_pct"] <= 100.0
    assert summary["currency_symbol"] == "₹"


def test_consumption_analytics_aggregation(data_service):
    """Validates diurnal 24-hour curve calculation and 30-day daily aggregation."""
    cons = data_service.get_consumption(user_id=1, time_range="30d")
    assert isinstance(cons, dict)
    assert cons["meter_id"] == 1

    # 24-Hour Diurnal Profile
    assert len(cons["diurnal_hours"]) == 24
    assert len(cons["diurnal_baseline"]) == 24
    assert len(cons["diurnal_recent"]) == 24
    assert all(v >= 0 for v in cons["diurnal_baseline"])

    # Peak hours callout
    assert ":" in cons["peak_morning_hour"]
    assert ":" in cons["peak_evening_hour"]

    # 30-day Daily series
    assert len(cons["daily_labels"]) > 0
    assert len(cons["daily_values"]) == len(cons["daily_labels"])
    assert len(cons["moving_avg_7d"]) == len(cons["daily_labels"])

    # Disaggregation
    assert "disaggregated_pct" in cons
    assert "disaggregated_liters" in cons
    assert sum(cons["disaggregated_pct"].values()) == pytest.approx(100.0, abs=1.0)


def test_forecast_dto_formatting(data_service):
    """Ensures Phase 3A 7-day model predictions are properly formatted with dates and bounds."""
    fc = data_service.get_forecast(user_id=1)
    assert isinstance(fc, dict)
    assert fc["meter_id"] == 1
    assert len(fc["forecast_dates"]) == 7
    assert len(fc["predicted_liters"]) == 7
    assert len(fc["baseline_liters"]) == 7
    assert len(fc["confidence_lower"]) == 7
    assert len(fc["confidence_upper"]) == 7

    # Confidence interval order
    for i in range(7):
        assert fc["confidence_lower"][i] <= fc["predicted_liters"][i] <= fc["confidence_upper"][i]

    assert fc["forecast_avg_liters_day"] > 0
    assert len(fc["peak_day_date"]) > 0
    assert "Random Forest" in fc["model_name"] or "Baseline" in fc["model_name"]
    assert "Model Projection" in fc["disclaimer"]


def test_anomaly_log_dto(data_service):
    """Verifies Phase 3B anomaly alerts are correctly transformed into incident records."""
    anoms = data_service.get_anomalies(user_id=1)
    assert isinstance(anoms, dict)
    assert anoms["meter_id"] == 1
    assert "active_alert_count" in anoms
    assert "incidents" in anoms
    assert isinstance(anoms["incidents"], list)

    if anoms["incidents"]:
        inc = anoms["incidents"][0]
        assert "incident_id" in inc
        assert "timestamp" in inc
        assert inc["anomaly_type"] in ("leak", "surge", "unusual_pattern", "low")
        assert inc["severity"] in ("critical", "high", "medium", "low")
        assert len(inc["explanation"]) > 0
        assert len(inc["recommended_action"]) > 0


def test_recommendations_dto(data_service):
    """Validates that recommendations from Phase 3C have positive savings and urgency indicators."""
    recs = data_service.get_recommendations(user_id=1)
    assert isinstance(recs, dict)
    assert "recommendations" in recs
    assert len(recs["recommendations"]) > 0

    for r in recs["recommendations"]:
        assert len(r["title"]) > 0
        assert len(r["description"]) > 0
        assert r["estimated_savings_liters_day"] >= 0
        assert r["monthly_financial_savings"] >= 0
        assert r["difficulty"] in ("easy", "moderate", "hard")
        assert r["priority"] in ("critical", "high", "medium", "low")

    assert recs["total_potential_savings_lpd"] >= 0
    assert recs["total_potential_financial"] >= 0


def test_user_isolation(data_service):
    """Confirms that querying user 1, user 2, and user 3 returns strictly isolated meter data."""
    u1 = data_service.get_summary(user_id=1)
    u2 = data_service.get_summary(user_id=2)
    u3 = data_service.get_summary(user_id=3)

    assert u1["user"]["meter_id"] == 1
    assert u2["user"]["meter_id"] == 2
    assert u3["user"]["meter_id"] == 3

    assert u1["user"]["name"] == "Sarah Jenkins"
    assert u2["user"]["name"] == "Marcus Vance"
    assert u3["user"]["name"] == "Elena Rostova"

    # Scale differences across profiles
    assert u1["user"]["household_size"] == 4
    assert u2["user"]["household_size"] == 12
    assert u3["user"]["household_size"] == 85

    # Volumes differ according to scale
    assert u1["today_usage_liters"] != u2["today_usage_liters"]
    assert u2["today_usage_liters"] != u3["today_usage_liters"]


def test_empty_telemetry_resilience():
    """Verifies that an unknown user ID receives safe default cards without unhandled exceptions."""
    ds = get_data_service()
    # Query non-existent user 999
    summary = ds.get_summary(user_id=999)
    assert isinstance(summary, dict)
    assert "user" in summary
    assert summary["today_usage_liters"] > 0  # Falls back to safe default profile


def test_chatbot_api_integration(data_service):
    """Tests end-to-end question answering through the dashboard data adapter."""
    res = data_service.handle_chat(user_id=1, user_message="How can I detect a silent toilet leak?")
    assert isinstance(res, dict)
    assert "conversational_response" in res
    assert len(res["conversational_response"]) > 0
    assert "recommendations" in res
    assert "source_citations" in res
    assert "safety_disclaimer" in res


def test_http_server_endpoints():
    """Validates that the Python standard-library HTTP server correctly handles /api/dashboard/* endpoints."""
    # Spin up server in background thread on an ephemeral test port
    port = 8899
    server = create_dashboard_server(host="127.0.0.1", port=port)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    time.sleep(0.3)

    base_url = f"http://127.0.0.1:{port}"

    try:
        # 1. Test Summary Endpoint
        with urllib.request.urlopen(f"{base_url}/api/dashboard/summary?user_id=1", timeout=5) as response:
            assert response.status == 200
            data = json.loads(response.read().decode("utf-8"))
            assert data["user"]["user_id"] == 1
            assert "today_usage_liters" in data

        # 2. Test Consumption Endpoint
        with urllib.request.urlopen(f"{base_url}/api/dashboard/consumption?user_id=1&range=30d", timeout=5) as response:
            assert response.status == 200
            data = json.loads(response.read().decode("utf-8"))
            assert "diurnal_baseline" in data
            assert len(data["diurnal_baseline"]) == 24

        # 3. Test Forecast Endpoint
        with urllib.request.urlopen(f"{base_url}/api/dashboard/forecast?user_id=1", timeout=5) as response:
            assert response.status == 200
            data = json.loads(response.read().decode("utf-8"))
            assert len(data["forecast_dates"]) == 7

        # 4. Test Anomalies Endpoint
        with urllib.request.urlopen(f"{base_url}/api/dashboard/anomalies?user_id=1", timeout=5) as response:
            assert response.status == 200
            data = json.loads(response.read().decode("utf-8"))
            assert "incidents" in data

        # 5. Test Recommendations Endpoint
        with urllib.request.urlopen(f"{base_url}/api/dashboard/recommendations?user_id=1", timeout=5) as response:
            assert response.status == 200
            data = json.loads(response.read().decode("utf-8"))
            assert "recommendations" in data

        # 6. Test Users Endpoint
        with urllib.request.urlopen(f"{base_url}/api/dashboard/users", timeout=5) as response:
            assert response.status == 200
            data = json.loads(response.read().decode("utf-8"))
            assert len(data) == 3

        # 7. Test Chat POST Endpoint
        req_body = json.dumps({"user_id": 1, "message": "Why is my bill high?"}).encode("utf-8")
        post_req = urllib.request.Request(
            f"{base_url}/api/dashboard/chat",
            data=req_body,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(post_req, timeout=5) as response:
            assert response.status == 200
            data = json.loads(response.read().decode("utf-8"))
            assert "conversational_response" in data

    finally:
        server.shutdown()
        server.server_close()
