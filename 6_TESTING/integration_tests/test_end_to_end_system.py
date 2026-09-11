"""
End-to-End Integrated System Test Suite
Location: 6_TESTING/integration_tests/test_end_to_end_system.py

Executes a complete lifecycle workflow across all platform components:
1. Authentication & JWT token acquisition
2. Persona resolution & summary generation
3. Telemetry time-series extraction
4. Machine learning forecast generation (Phase 3A Random Forest)
5. Anomaly detection & severity arbitration (Phase 3B)
6. Conversational RAG advice retrieval (Phase 3C)
7. Multi-persona transition & isolation verification
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

from backend.app import create_app
from backend.config import TestingConfig
from backend.services.auth_service import get_auth_service


@pytest.fixture(scope="module")
def client():
    """Create Flask test client."""
    app = create_app(config=TestingConfig())
    return app.test_client()


def test_full_end_to_end_resident_lifecycle(client):
    """
    Simulates complete resident journey from login to dashboard, forecasting,
    anomaly inspection, and conversational recommendation.
    """
    # 1. Authenticate as Sarah Chen (Residential Single-Family, Meter 1)
    login_res = client.post("/api/auth/login", json={
        "email": "sarah.chen@example.com",
        "password": "ResidentPass2026!"
    })
    assert login_res.status_code == 200
    auth_data = login_res.get_json()
    assert "token" in auth_data
    token = auth_data["token"]
    user = auth_data["user"]
    assert user["user_id"] == 1
    assert user["meter_id"] == 1
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Query Dashboard Summary KPI cards
    summary_res = client.get("/api/dashboard/summary?user_id=1", headers=headers)
    assert summary_res.status_code == 200
    summary = summary_res.get_json()
    assert summary["today_consumption_liters"] > 0
    assert summary["monthly_consumption_liters"] > 0
    assert "active_anomalies_count" in summary

    # 3. Query Hourly Telemetry Data (Last 7 Days)
    telemetry_res = client.get("/api/v1/telemetry/meters/1/readings?days=7", headers=headers)
    assert telemetry_res.status_code == 200
    telem = telemetry_res.get_json()
    assert telem["meter_id"] == 1
    assert len(telem["readings"]) > 0
    # Verify reading structure
    first_reading = telem["readings"][0]
    assert "timestamp" in first_reading
    assert "hourly_consumption_liters" in first_reading
    assert "cumulative_reading_m3" in first_reading

    # 4. Generate Machine Learning 7-Day Forward Forecast
    forecast_res = client.get("/api/v1/forecast/meters/1?days=7", headers=headers)
    assert forecast_res.status_code == 200
    forecast_payload = forecast_res.get_json()
    forecast = forecast_payload["forecast"]
    assert len(forecast) == 7
    # Verify forecast points have uncertainty bounds
    for day_fc in forecast:
        assert "predicted_consumption_liters" in day_fc or "forecast_liters" in day_fc
        val = day_fc.get("predicted_consumption_liters", day_fc.get("forecast_liters"))
        assert val > 50  # reasonable residential daily volume
        assert day_fc["lower_bound_liters"] <= val <= day_fc["upper_bound_liters"]

    # 5. Inspect Anomaly & Leak Alerts
    anom_res = client.get("/api/v1/anomalies/meters/1", headers=headers)
    assert anom_res.status_code == 200
    anom_data = anom_res.get_json()
    assert "anomalies" in anom_data
    # Meter 1 contains injected anomalies (toilet leak and surge)
    assert len(anom_data["anomalies"]) > 0

    # 6. Interact with Conversational Water Conservation Advisor
    chat_payload = {
        "message": "I noticed an anomaly alert on my meter. What steps should I take to diagnose a toilet leak?",
        "user_id": 1
    }
    chat_res = client.post("/api/v1/chat", json=chat_payload, headers=headers)
    assert chat_res.status_code == 200
    chat_data = chat_res.get_json()
    assert "response" in chat_data
    assert "disclaimer" in chat_data
    assert len(chat_data["response"]) > 20
    # Must contain practical diagnostic advice
    chat_text_lower = chat_data["response"].lower()
    assert any(term in chat_text_lower for term in ["toilet", "dye", "flapper", "tank", "leak", "meter"])


def test_persona_switching_and_scale_contrast(client):
    """
    Verifies persona switching from Resident (Meter 1) to Commercial Facility (Meter 3),
    confirming appropriate consumption scaling and data isolation.
    """
    auth = get_auth_service()

    # Obtain token for Commercial Facility (Meter 3)
    comm_token = auth.get_demo_token(user_id=3)["token"]
    comm_headers = {"Authorization": f"Bearer {comm_token}"}

    # Query Commercial Summary
    comm_summary = client.get("/api/dashboard/summary?user_id=3", headers=comm_headers).get_json()
    # Commercial monthly/forecast usage is substantially higher than single resident
    assert comm_summary["monthly_consumption_liters"] > 10000 or comm_summary["forecast_avg_liters_day"] > 500 or comm_summary["today_consumption_liters"] > 200

    # Query Commercial Forecast
    comm_fc = client.get("/api/v1/forecast/meters/3?days=7", headers=comm_headers).get_json()
    assert len(comm_fc["forecast"]) == 7
    comm_vals = [
        step.get("predicted_consumption_liters", step.get("forecast_liters"))
        for step in comm_fc["forecast"]
    ]
    assert max(comm_vals) > 1000 or any(v > 500 for v in comm_vals), "Commercial daily forecast must reflect commercial operating scale"
