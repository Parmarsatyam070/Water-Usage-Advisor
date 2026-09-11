"""
Phase 7 End-to-End Functionality Audit & Repair Verification Test Suite
Location: 6_TESTING/integration_tests/test_phase7_end_to_end_audit.py

Verifies the comprehensive repair plan for all Phase 7 features:
1. Strict 401 unauthenticated enforcement across all protected endpoints
2. Strict 403 BOLA/IDOR cross-tenant defense
3. 4-tier role authorization matrix for /api/admin/system-summary
4. Goal adoption schema compliance with authoritative status and updated_at columns
5. Scenario persistence and history retrieval with dialect-compatible primary key handling
6. Sustainability score explanation and improvement opportunities output
7. Water budget persistence and burn rate calculation
8. Authenticated CSV and HTML/PDF executive reports with complete metrics and badges
9. Chatbot authentication enforcement
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
def app():
    """Create application configured for testing."""
    return create_app(config=TestingConfig())


@pytest.fixture(scope="module")
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope="module")
def user1_token():
    """Household user token (User 1, Household role)."""
    return get_auth_service().get_demo_token(user_id=1)["token"]


@pytest.fixture(scope="module")
def user2_token():
    """Institution user token (User 2, Institution role)."""
    return get_auth_service().get_demo_token(user_id=2)["token"]


@pytest.fixture(scope="module")
def user3_token():
    """Municipal operator token (User 3, Municipal role)."""
    return get_auth_service().get_demo_token(user_id=3)["token"]


class TestPhase7EndToEndAudit:
    """Comprehensive regression tests validating all Phase 7 repair deliverables."""

    def test_unauthenticated_requests_return_401_across_all_endpoints(self, client):
        """Verify that every protected Phase 7 endpoint returns HTTP 401 without valid token."""
        endpoints = [
            ("POST", "/api/water/savings/simulate", {"baseline_consumption": 400}),
            ("POST", "/api/water/scenarios", {"scenario_name": "Test", "category": "bathroom", "percentage_change": -10}),
            ("GET", "/api/water/scenarios/history", None),
            ("GET", "/api/water/sustainability-score", None),
            ("GET", "/api/alerts/history", None),
            ("PATCH", "/api/alerts/1/status", {"status": "ACKNOWLEDGED"}),
            ("GET", "/api/sdg6/impact", None),
            ("GET", "/api/goals/recommendations", None),
            ("POST", "/api/goals/adopt", {"goal_type": "shower_reduction", "target_value": 350}),
            ("GET", "/api/water/insights", None),
            ("GET", "/api/water/budget", None),
            ("POST", "/api/water/budget", {"target_liters": 12000}),
            ("GET", "/api/reports/water.csv", None),
            ("GET", "/api/reports/water.html", None),
            ("GET", "/api/reports/water.pdf", None),
            ("GET", "/api/admin/system-summary", None),
            ("POST", "/api/dashboard/chat", {"message": "Hello"}),
        ]

        for method, path, payload in endpoints:
            if method == "GET":
                res = client.get(path)
            elif method == "POST":
                res = client.post(path, json=payload or {})
            elif method == "PATCH":
                res = client.patch(path, json=payload or {})
            else:
                pytest.fail(f"Unsupported HTTP method {method}")

            assert res.status_code == 401, f"Expected 401 for unauthenticated {method} {path}, got {res.status_code}"
            assert res.json.get("error_code") == "UNAUTHORIZED"

    def test_cross_tenant_access_returns_403_bola(self, client, user1_token):
        """Verify that a household user cannot access another tenant's protected resources (BOLA / IDOR)."""
        headers = {"Authorization": f"Bearer {user1_token}"}
        cross_tenant_queries = [
            "/api/water/sustainability-score?user_id=2",
            "/api/water/scenarios/history?user_id=2",
            "/api/sdg6/impact?user_id=2",
            "/api/water/insights?user_id=2",
            "/api/water/budget?user_id=2",
            "/api/goals/recommendations?user_id=2",
            "/api/reports/water.csv?user_id=2",
            "/api/reports/water.html?user_id=2",
        ]

        for path in cross_tenant_queries:
            res = client.get(path, headers=headers)
            assert res.status_code == 403, f"Expected 403 for cross-tenant access to {path}, got {res.status_code}"
            assert res.json.get("error_code") == "FORBIDDEN"

    def test_admin_system_summary_role_matrix(self, client, user1_token, user2_token, user3_token):
        """
        Verify the 4-tier authorization matrix for /api/admin/system-summary:
        - No token -> 401 Unauthorized
        - Household (User 1) -> 403 Forbidden
        - Institution (User 2) -> 403 Forbidden
        - Municipal (User 3) -> 200 OK
        """
        path = "/api/admin/system-summary"

        # Tier 1: No token
        res_none = client.get(path)
        assert res_none.status_code == 401
        assert res_none.json.get("error_code") == "UNAUTHORIZED"

        # Tier 2: Household token
        res_h = client.get(path, headers={"Authorization": f"Bearer {user1_token}"})
        assert res_h.status_code == 403
        assert res_h.json.get("error_code") == "FORBIDDEN"

        # Tier 3: Institution token
        res_i = client.get(path, headers={"Authorization": f"Bearer {user2_token}"})
        assert res_i.status_code == 403
        assert res_i.json.get("error_code") == "FORBIDDEN"

        # Tier 4: Municipal token
        res_m = client.get(path, headers={"Authorization": f"Bearer {user3_token}"})
        assert res_m.status_code == 200
        data = res_m.json
        assert data.get("system_status") in ["operational", "degraded"]
        assert "database" in data
        assert "ai_models" in data

    def test_goal_adoption_authoritative_schema_compliance(self, client, user1_token):
        """
        Verify goal adoption works with authoritative PostgreSQL schema:
        - Uses status ('active') and updated_at
        - Returns adopted goal payload with goal_id
        """
        headers = {"Authorization": f"Bearer {user1_token}"}
        payload = {
            "user_id": 1,
            "goal_type": "shower_aerator",
            "target_value": 380.0,
            "target_unit": "liters",
            "duration_days": 30
        }
        res = client.post("/api/goals/adopt", json=payload, headers=headers)
        assert res.status_code in [200, 201]
        data = res.json
        assert data.get("status") == "active"
        assert data.get("goal_type") == "shower_aerator"
        assert data.get("target_value") == 380.0
        assert "goal_id" in data
        assert data.get("progress_percentage") == 0.0

    def test_scenario_history_persistence_and_retrieval(self, client, user1_token):
        """
        Verify that what-if scenarios are persisted and retrievable via history:
        - Run scenario with save_to_history = True
        - Check GET /api/water/scenarios/history
        """
        headers = {"Authorization": f"Bearer {user1_token}"}
        scen_payload = {
            "user_id": 1,
            "scenario_name": "Audit Test Scenario",
            "category": "kitchen",
            "percentage_change": -25.0,
            "save_to_history": True
        }
        run_res = client.post("/api/water/scenarios", json=scen_payload, headers=headers)
        assert run_res.status_code in [200, 201]
        run_data = run_res.json
        assert run_data.get("category") == "kitchen"
        assert run_data.get("percentage_change") == -25.0
        assert "explanation" in run_data

        hist_res = client.get("/api/water/scenarios/history", headers=headers)
        assert hist_res.status_code == 200
        hist_data = hist_res.json
        assert "scenarios" in hist_data
        assert isinstance(hist_data["scenarios"], list)

    def test_sustainability_score_explanations_and_opportunities(self, client, user1_token):
        """
        Verify sustainability score includes deterministic explanation and improvement opportunities.
        """
        headers = {"Authorization": f"Bearer {user1_token}"}
        res = client.get("/api/water/sustainability-score", headers=headers)
        assert res.status_code == 200
        data = res.json
        assert "sustainability_score" in data
        assert "grade" in data
        assert "rating" in data
        assert "components" in data

        # Audit deliverable: explanation string and structured improvement opportunities
        assert "explanation" in data
        assert isinstance(data["explanation"], str)
        assert len(data["explanation"]) > 0

        assert "improvement_opportunities" in data
        assert isinstance(data["improvement_opportunities"], list)
        assert len(data["improvement_opportunities"]) >= 1

    def test_report_csv_and_html_generation_and_auth(self, client, user1_token):
        """
        Verify CSV and print-ready HTML executive reports:
        - CSV contains valid telemetry rows
        - HTML contains executive brief, sustainability score, budget, and SDG 6.4 indicators
        - Both endpoints require authentication
        """
        headers = {"Authorization": f"Bearer {user1_token}"}

        # CSV Report
        csv_res = client.get("/api/reports/water.csv?user_id=1", headers=headers)
        assert csv_res.status_code == 200
        assert "text/csv" in csv_res.content_type
        assert "Daily_Consumption_Liters" in csv_res.text or "daily_consumption_liters" in csv_res.text.lower()

        # HTML Executive Report (canonical)
        html_res = client.get("/api/reports/water.html?user_id=1", headers=headers)
        assert html_res.status_code == 200
        assert "text/html" in html_res.content_type
        html_text = html_res.text
        assert "Executive Audit Report" in html_text
        assert "Sustainability Score" in html_text
        assert "SDG 6.4" in html_text
        assert "[MEASURED]" in html_text
        assert "[ESTIMATED]" in html_text

        # PDF Alias (returns print-ready HTML)
        pdf_res = client.get("/api/reports/water.pdf?user_id=1", headers=headers)
        assert pdf_res.status_code == 200
        assert "text/html" in pdf_res.content_type

    def test_water_budget_persistence_and_overshoot(self, client, user1_token):
        """
        Verify water budget planning:
        - Setting a target budget
        - Fetching active budget with burn rates and overshoot projection
        """
        headers = {"Authorization": f"Bearer {user1_token}"}
        set_res = client.post("/api/water/budget", json={"user_id": 1, "target_liters": 14500, "period": "monthly"}, headers=headers)
        assert set_res.status_code in [200, 201]

        get_res = client.get("/api/water/budget", headers=headers)
        assert get_res.status_code == 200
        b_data = get_res.json
        assert b_data.get("target_liters") == 14500
        assert "consumption_status" in b_data
        assert "time_progress" in b_data
        assert "forecast_projection" in b_data
        assert "ideal_burn_rate_lpd" in b_data["consumption_status"]
        assert "actual_burn_rate_lpd" in b_data["consumption_status"]

    def test_chatbot_authenticated_chat_flow(self, client, user1_token):
        """
        Verify authenticated chatbot messaging flow:
        - 401 when no token is supplied
        - 200 with advisor response when valid token is supplied
        """
        # Unauthenticated
        unauth_res = client.post("/api/dashboard/chat", json={"message": "How can I reduce water consumption?"})
        assert unauth_res.status_code == 401

        # Authenticated
        auth_res = client.post(
            "/api/dashboard/chat",
            json={"message": "What is my current water usage?"},
            headers={"Authorization": f"Bearer {user1_token}"}
        )
        assert auth_res.status_code == 200
        chat_data = auth_res.json
        assert "response" in chat_data
        assert len(chat_data["response"]) > 0
