"""
Phase 7 API Security & RBAC Integration Test Suite
Location: 6_TESTING/integration_tests/test_phase7_api_security.py

Validates all 10 defined security test categories for Phase 7 endpoints:
1. Authorized same-user access
2. Unauthorized cross-user access
3. Cross-meter access attempt
4. Household role boundary
5. Institution role boundary
6. Municipal/admin role boundary
7. Nonexistent resource handling
8. Invalid resource ID handling
9. Missing/invalid authentication
10. Privilege escalation attempts
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
    """Create test application configured for testing."""
    return create_app(config=TestingConfig())


@pytest.fixture(scope="module")
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope="module")
def user1_token():
    """Household user token (User 1, Meter 1, Household role)."""
    return get_auth_service().get_demo_token(user_id=1)["token"]


@pytest.fixture(scope="module")
def user2_token():
    """Institution user token (User 2, Meter 2, Institution role)."""
    return get_auth_service().get_demo_token(user_id=2)["token"]


@pytest.fixture(scope="module")
def user3_token():
    """Municipal user token (User 3, Meter 3, Municipal role)."""
    return get_auth_service().get_demo_token(user_id=3)["token"]


class TestPhase7SecurityCategories:
    """Tests covering all 10 defined security test categories for Phase 7."""

    # Category 1: Authorized same-user access
    def test_cat1_authorized_same_user_access(self, client, user1_token):
        headers = {"Authorization": f"Bearer {user1_token}"}

        # Simulator
        res1 = client.post("/api/water/savings/simulate", json={"baseline_consumption": 440, "reduction_percentage": 10}, headers=headers)
        assert res1.status_code == 200

        # Sustainability score
        res2 = client.get("/api/water/sustainability-score", headers=headers)
        assert res2.status_code == 200
        assert res2.json["user_id"] == 1

        # SDG 6.4 impact
        res3 = client.get("/api/sdg6/impact", headers=headers)
        assert res3.status_code == 200
        assert res3.json["user_id"] == 1

        # Insights
        res4 = client.get("/api/water/insights", headers=headers)
        assert res4.status_code == 200

        # Budget
        res5 = client.get("/api/water/budget", headers=headers)
        assert res5.status_code == 200

        # Goal recommendations
        res6 = client.get("/api/goals/recommendations", headers=headers)
        assert res6.status_code == 200

        # Reports
        res7 = client.get("/api/reports/water.csv", headers=headers)
        assert res7.status_code == 200
        assert "text/csv" in res7.content_type

    # Category 2: Unauthorized cross-user access (BOLA / IDOR defense)
    def test_cat2_unauthorized_cross_user_access(self, client, user1_token):
        headers = {"Authorization": f"Bearer {user1_token}"}
        # User 1 attempting to query User 2's sustainability score explicitly
        res = client.get("/api/water/sustainability-score?user_id=2", headers=headers)
        assert res.status_code == 403
        assert res.json["error_code"] == "FORBIDDEN"

    # Category 3: Cross-meter access attempt
    def test_cat3_cross_meter_access_attempt(self, client, user1_token):
        headers = {"Authorization": f"Bearer {user1_token}"}
        # User 1 attempting to access Meter 2
        res = client.get("/api/water/insights?meter_id=2", headers=headers)
        assert res.status_code == 403
        assert res.json["error_code"] == "FORBIDDEN"

    # Category 4: Household role boundary
    def test_cat4_household_role_boundary(self, client, user1_token):
        headers = {"Authorization": f"Bearer {user1_token}"}
        # Household can access own alerts
        res = client.get("/api/alerts/history", headers=headers)
        assert res.status_code == 200
        for alert in res.json.get("alerts", []):
            assert alert["user_id"] == 1

    # Category 5: Institution role boundary
    def test_cat5_institution_role_boundary(self, client, user2_token):
        headers = {"Authorization": f"Bearer {user2_token}"}
        # Institution can access own budget and goals
        res = client.get("/api/water/budget", headers=headers)
        assert res.status_code == 200
        assert res.json["user_id"] == 2

    # Category 6: Municipal/admin role boundary
    def test_cat6_municipal_admin_role_boundary(self, client, user1_token, user2_token, user3_token):
        # Household access to admin system summary -> 403 Forbidden
        h_res = client.get("/api/admin/system-summary", headers={"Authorization": f"Bearer {user1_token}"})
        assert h_res.status_code == 403
        assert h_res.json["error_code"] == "FORBIDDEN"

        # Institution access to admin system summary -> 403 Forbidden
        i_res = client.get("/api/admin/system-summary", headers={"Authorization": f"Bearer {user2_token}"})
        assert i_res.status_code == 403
        assert i_res.json["error_code"] == "FORBIDDEN"

        # Municipal access to admin system summary -> 200 OK
        m_res = client.get("/api/admin/system-summary", headers={"Authorization": f"Bearer {user3_token}"})
        assert m_res.status_code == 200
        assert "system_status" in m_res.json
        assert "database" in m_res.json

    # Category 7: Nonexistent resource handling
    def test_cat7_nonexistent_resource_handling(self, client, user1_token):
        headers = {"Authorization": f"Bearer {user1_token}"}
        # Nonexistent alert ID
        res = client.patch("/api/alerts/99999999/status", json={"status": "ACKNOWLEDGED"}, headers=headers)
        assert res.status_code == 404
        assert res.json["error_code"] == "NOT_FOUND"

    # Category 8: Invalid resource ID and parameter handling
    def test_cat8_invalid_parameter_handling(self, client, user1_token):
        headers = {"Authorization": f"Bearer {user1_token}"}

        # Missing required parameter in savings simulator
        res1 = client.post("/api/water/savings/simulate", json={}, headers=headers)
        assert res1.status_code == 400

        # Invalid percentage in what-if scenario
        res2 = client.post("/api/water/scenarios", json={"percentage_change": 500.0, "category": "kitchen"}, headers=headers)
        assert res2.status_code == 400

        # Invalid alert status
        res3 = client.patch("/api/alerts/1/status", json={"status": "INVALID_STATUS"}, headers=headers)
        assert res3.status_code == 400

    # Category 9: Missing and invalid authentication
    def test_cat9_missing_and_invalid_authentication(self, client):
        # Missing token -> 401 Unauthorized
        res1 = client.get("/api/water/sustainability-score")
        assert res1.status_code == 401
        assert res1.json["error_code"] == "UNAUTHORIZED"

        # Invalid token signature -> 401 Unauthorized
        res2 = client.get("/api/water/sustainability-score", headers={"Authorization": "Bearer invalid.jwt.token"})
        assert res2.status_code == 401
        assert res2.json["error_code"] in ["INVALID_TOKEN", "UNAUTHORIZED"]

    # Category 10: Privilege escalation attempts
    def test_cat10_privilege_escalation_attempts(self, client, user1_token):
        headers = {"Authorization": f"Bearer {user1_token}"}
        # Household attempting to mutate another user's alert or budget with spoofed user_id
        res = client.post("/api/water/budget", json={"user_id": 2, "period": "monthly", "target_liters": 500}, headers=headers)
        assert res.status_code == 403
        assert res.json["error_code"] == "FORBIDDEN"
