"""
Production API Integration Test Suite
Location: 6_TESTING/integration_tests/test_production_api.py

Validates all Flask REST API routes, status codes, query validation,
and sanitized error formats using pytest and Flask.test_client().
"""

import os
import sys
import pytest

# Ensure repository root and 4_DEVELOPMENT are on sys.path
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
def app():
    """Create Flask application in testing mode."""
    application = create_app(config=TestingConfig())
    return application


@pytest.fixture(scope="module")
def client(app):
    """Test client fixture."""
    return app.test_client()


@pytest.fixture(scope="module")
def user1_token():
    """Generate a valid JWT token for User 1 (Meter 1)."""
    auth = get_auth_service()
    res = auth.get_demo_token(user_id=1)
    return res["token"]


@pytest.fixture(scope="module")
def user2_token():
    """Generate a valid JWT token for User 2 (Meter 2)."""
    auth = get_auth_service()
    res = auth.get_demo_token(user_id=2)
    return res["token"]


# ============================================================
# Static & Public Health Endpoints
# ============================================================

def test_root_serves_frontend(client):
    """Ensure GET / serves index.html with 200 OK."""
    res = client.get("/")
    assert res.status_code == 200
    assert b"Smart Water Usage Advisor" in res.data or b"<!DOCTYPE html>" in res.data


def test_health_endpoint(client):
    """Ensure GET /api/health returns operational status without authentication."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert "status" in data
    assert data["status"] in ("healthy", "degraded")
    assert "services" in data
    assert "timestamp" in data
    assert "environment" in data


# ============================================================
# Authentication Routes
# ============================================================

def test_auth_login_valid(client):
    """Ensure POST /api/auth/login succeeds with valid credentials."""
    payload = {
        "email": "sarah.chen@example.com",
        "password": "ResidentPass2026!"
    }
    res = client.post("/api/auth/login", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert "token" in data
    assert "user" in data
    assert data["user"]["user_id"] == 1
    assert "password_hash" not in data["user"]


def test_auth_login_invalid_password(client):
    """Ensure POST /api/auth/login fails closed on invalid password."""
    payload = {
        "email": "sarah.chen@example.com",
        "password": "WrongPassword123!"
    }
    res = client.post("/api/auth/login", json=payload)
    assert res.status_code == 401
    data = res.get_json()
    assert data["status_code"] == 401


def test_auth_login_missing_fields(client):
    """Ensure POST /api/auth/login returns 400 on empty or missing body."""
    res = client.post("/api/auth/login", json={})
    assert res.status_code == 400


def test_auth_demo_token_allowed(client):
    """Ensure GET /api/auth/demo-token succeeds for whitelisted user_ids in test mode."""
    for uid in (1, 2, 3):
        res = client.get(f"/api/auth/demo-token?user_id={uid}")
        assert res.status_code == 200
        data = res.get_json()
        assert "token" in data
        assert data["user"]["user_id"] == uid


def test_auth_demo_token_disallowed(client):
    """Ensure GET /api/auth/demo-token rejects non-whitelisted user_ids."""
    res = client.get("/api/auth/demo-token?user_id=99")
    assert res.status_code == 400


def test_auth_me_with_token(client, user1_token):
    """Ensure GET /api/auth/me returns the authenticated user payload."""
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {user1_token}"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["user"]["user_id"] == 1
    assert "password_hash" not in data["user"]


def test_auth_me_unauthorized(client):
    """Ensure GET /api/auth/me returns 401 when no token is supplied."""
    res = client.get("/api/auth/me")
    assert res.status_code == 401


# ============================================================
# Dashboard Blueprint Routes
# ============================================================

def test_dashboard_summary(client, user1_token):
    """Ensure GET /api/dashboard/summary returns user summary metrics."""
    res = client.get(
        "/api/dashboard/summary?user_id=1",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert res.status_code == 200
    data = res.get_json()
    assert "today_consumption_liters" in data
    assert "monthly_consumption_liters" in data
    assert "active_anomalies_count" in data


def test_dashboard_consumption(client, user1_token):
    """Ensure GET /api/dashboard/consumption returns consumption analytics DTO."""
    res = client.get(
        "/api/dashboard/consumption?meter_id=1&range=30d",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert res.status_code == 200
    data = res.get_json()
    assert "daily_values" in data or "diurnal_hours" in data
    assert "meter_id" in data


def test_dashboard_forecast(client, user1_token):
    """Ensure GET /api/dashboard/forecast returns 7-day predictive forecast DTO."""
    res = client.get(
        "/api/dashboard/forecast?meter_id=1",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert res.status_code == 200
    data = res.get_json()
    assert "predicted_liters" in data or "forecast_dates" in data
    assert len(data.get("predicted_liters", [])) == 7 or len(data.get("forecast_dates", [])) == 7


def test_dashboard_anomalies(client, user1_token):
    """Ensure GET /api/dashboard/anomalies returns anomaly incident records DTO."""
    res = client.get(
        "/api/dashboard/anomalies?meter_id=1",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert res.status_code == 200
    data = res.get_json()
    assert "incidents" in data
    assert "active_alert_count" in data


def test_dashboard_recommendations(client, user1_token):
    """Ensure GET /api/dashboard/recommendations returns conservation guidance DTO."""
    res = client.get(
        "/api/dashboard/recommendations?user_id=1",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert res.status_code == 200
    data = res.get_json()
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)


def test_dashboard_goals(client, user1_token):
    """Ensure GET /api/dashboard/goals returns user conservation targets DTO."""
    res = client.get(
        "/api/dashboard/goals?user_id=1",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert res.status_code == 200
    data = res.get_json()
    assert "target_reduction_pct" in data or "achieved_progress_pct" in data


def test_dashboard_users_list(client, user1_token):
    """Ensure GET /api/dashboard/users returns persona options without password hashes."""
    res = client.get(
        "/api/dashboard/users",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert res.status_code == 200
    users = res.get_json()
    assert len(users) >= 3
    for u in users:
        assert "password_hash" not in u
        assert "user_id" in u
        assert "meter_id" in u


# ============================================================
# Telemetry, Forecasting & Anomaly v1 Blueprints
# ============================================================

def test_v1_telemetry_readings(client, user1_token):
    """Ensure GET /api/v1/telemetry/meters/1/readings returns hourly telemetry."""
    res = client.get(
        "/api/v1/telemetry/meters/1/readings?days=3",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert res.status_code == 200
    data = res.get_json()
    assert "readings" in data
    assert "meter_id" in data
    assert data["meter_id"] == 1


def test_v1_telemetry_daily(client, user1_token):
    """Ensure GET /api/v1/telemetry/meters/1/daily returns aggregated daily usage."""
    res = client.get(
        "/api/v1/telemetry/meters/1/daily?days=14",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert res.status_code == 200
    data = res.get_json()
    assert "daily_summary" in data


def test_v1_forecast_meter(client, user1_token):
    """Ensure GET /api/v1/forecast/meters/1 returns 7-day model forecast."""
    res = client.get(
        "/api/v1/forecast/meters/1?days=7",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert res.status_code == 200
    data = res.get_json()
    assert "forecast" in data
    assert len(data["forecast"]) == 7
    assert "disclaimer" in data


def test_v1_anomalies_meter(client, user1_token):
    """Ensure GET /api/v1/anomalies/meters/1 returns detected anomalies."""
    res = client.get(
        "/api/v1/anomalies/meters/1",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert res.status_code == 200
    data = res.get_json()
    assert "anomalies" in data


# ============================================================
# Chatbot Route
# ============================================================

def test_v1_chat_valid_message(client, user1_token):
    """Ensure POST /api/v1/chat answers water conservation questions."""
    payload = {
        "message": "How can I detect a leaking toilet in my home?",
        "user_id": 1
    }
    res = client.post(
        "/api/v1/chat",
        json=payload,
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert res.status_code == 200
    data = res.get_json()
    assert "response" in data
    assert len(data["response"]) > 10
    assert "disclaimer" in data


def test_v1_chat_empty_message(client, user1_token):
    """Ensure POST /api/v1/chat rejects empty queries with 400 Bad Request."""
    payload = {"message": "   "}
    res = client.post(
        "/api/v1/chat",
        json=payload,
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert res.status_code == 400


# ============================================================
# Centralized Error Handlers
# ============================================================

def test_404_not_found(client):
    """Ensure non-existent routes return standardized JSON 404."""
    res = client.get("/api/v1/nonexistent-route-for-testing")
    assert res.status_code == 404
    data = res.get_json()
    assert data["status_code"] == 404
    assert "error" in data


def test_405_method_not_allowed(client):
    """Ensure invalid HTTP method returns standardized JSON 405."""
    res = client.post("/api/health", json={"dummy": "data"})
    assert res.status_code == 405
    data = res.get_json()
    assert data["status_code"] == 405
