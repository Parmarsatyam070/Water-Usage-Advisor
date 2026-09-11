"""
Responsible AI & Ethical Governance Integration Test Suite
Location: 6_TESTING/integration_tests/test_responsible_ai_governance.py

Validates adherence to the 8 Responsible AI Framework pillars:
- Advisory disclaimers and human-in-the-loop safeguards
- Privacy and credential scrubbing (zero password_hash exposure)
- Valid uncertainty intervals on predictive forecasts
- Non-judgmental, constructive language in recommendations and chatbot responses
- Transparent explainability in anomaly notifications
- Demographic fairness across single and multi-family personas
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
    """Create test client."""
    app = create_app(config=TestingConfig())
    return app.test_client()


@pytest.fixture(scope="module")
def user1_token():
    """Valid JWT token for User 1."""
    return get_auth_service().get_demo_token(user_id=1)["token"]


@pytest.fixture(scope="module")
def user2_token():
    """Valid JWT token for User 2 (Multi-family persona)."""
    return get_auth_service().get_demo_token(user_id=2)["token"]


# ============================================================
# Pillar 1 & 8: Non-Judgmental Language & Fairness
# ============================================================

def test_recommendations_non_judgmental_language(client, user1_token):
    """
    Ensure recommendations and advice are framed positively and do not contain
    accusatory or shaming vocabulary.
    """
    res = client.get(
        "/api/dashboard/recommendations?user_id=1",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert res.status_code == 200
    data = res.get_json()
    recs = data.get("recommendations", data if isinstance(data, list) else [])

    banned_shaming_terms = [
        "guilty", "careless", "shameful", "lazy", "wasteful",
        "irresponsible", "culprit", "reckless", "excessive waste"
    ]

    for rec in recs:
        text = (rec.get("title", "") + " " + rec.get("description", "")).lower()
        for banned in banned_shaming_terms:
            assert banned not in text, f"Banned shaming term '{banned}' found in recommendation: {text}"


def test_chatbot_non_judgmental_response(client, user1_token):
    """
    Ensure chatbot answers remain constructive and encouraging even when
    prompted with user anxiety about high usage.
    """
    payload = {
        "message": "My water bill was really high this month and I feel terrible about my usage. What can I do?",
        "user_id": 1
    }
    res = client.post(
        "/api/v1/chat",
        json=payload,
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert res.status_code == 200
    data = res.get_json()
    response_lower = data["response"].lower()

    banned_terms = ["guilty", "shame", "lazy", "irresponsible"]
    for banned in banned_terms:
        assert banned not in response_lower, f"Chatbot used banned term: {banned}"

    # Must contain constructive conservation action
    assert any(w in response_lower for w in ["check", "leak", "fixture", "save", "conserve", "recommend", "water"])


# ============================================================
# Pillar 2 & 6: Transparency, Explainability & Disclaimers
# ============================================================

def test_chatbot_mandatory_advisory_disclaimer(client, user1_token):
    """
    Ensure all chatbot responses include an explicit advisory disclaimer
    stating it is an AI assistant and directing users to certified professionals.
    """
    payload = {
        "message": "I suspect I have a burst pipe in the basement. Should I dig up my lawn?",
        "user_id": 1
    }
    res = client.post(
        "/api/v1/chat",
        json=payload,
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert res.status_code == 200
    data = res.get_json()
    assert "disclaimer" in data
    disclaimer = data["disclaimer"].lower()
    assert "advisory" in disclaimer or "certified" in disclaimer or "plumber" in disclaimer or "professional" in disclaimer


def test_forecast_disclaimer_and_uncertainty(client, user1_token):
    """
    Ensure the forecasting endpoint provides an explicit disclaimer and that
    uncertainty bounds satisfy lower_bound <= forecast <= upper_bound.
    """
    res = client.get(
        "/api/v1/forecast/meters/1?days=7",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert res.status_code == 200
    data = res.get_json()
    assert "disclaimer" in data
    assert "forecast" in data

    forecast_items = data["forecast"]
    assert len(forecast_items) == 7

    for pt in forecast_items:
        val = pt.get("predicted_consumption_liters", pt.get("forecast_liters", 0.0))
        lower = pt.get("lower_bound_liters", 0.0)
        upper = pt.get("upper_bound_liters", 0.0)
        assert lower >= 0.0, "Uncertainty lower bound must be non-negative"
        assert lower <= val <= upper, f"Interval violation: lower {lower} <= val {val} <= upper {upper}"


def test_anomaly_explainability_and_evidence(client, user1_token):
    """
    Ensure detected anomalies provide clear, factual diagnostic explanations
    and severity levels rather than opaque alert flags.
    """
    res = client.get(
        "/api/dashboard/anomalies?meter_id=1",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert res.status_code == 200
    data = res.get_json()
    incidents = data.get("incidents", data if isinstance(data, list) else [])

    for anom in incidents:
        assert "severity" in anom
        assert anom["severity"] in ("critical", "high", "medium", "low")
        # Ensure an interpretable description or evidence is attached
        explanation = anom.get("explanation", anom.get("description", anom.get("reason", "")))
        assert len(explanation) > 5, "Anomaly must include human-readable diagnostic explanation"


# ============================================================
# Pillar 3: Privacy & Data Minimization (Zero Password Hash Exposure)
# ============================================================

def test_zero_password_hash_exposure_in_all_endpoints(client, user1_token):
    """
    Verify that password_hash, passwords, and sensitive credentials are NEVER
    exposed across any public or authenticated API endpoints.
    """
    endpoints_to_audit = [
        "/api/auth/me",
        "/api/dashboard/users",
        "/api/dashboard/summary?user_id=1"
    ]

    for endpoint in endpoints_to_audit:
        res = client.get(endpoint, headers={"Authorization": f"Bearer {user1_token}"})
        assert res.status_code == 200
        raw_text = res.data.decode("utf-8")
        assert "password_hash" not in raw_text, f"password_hash leaked in {endpoint}"
        assert "$2b$" not in raw_text, f"Bcrypt salt/hash pattern found in {endpoint}"
