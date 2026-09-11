#!/usr/bin/env python3
"""
Deployment Smoke Verification Script
Phase 6 - Deployment & Verification Layer

Performs end-to-end operational health, authentication, security, and AI service
probes against a deployed instance (Local Docker or Public Cloud).
Implemented strictly using Python's built-in standard library (urllib, json, argparse).
"""

import argparse
import json
import sys
import urllib.error
import urllib.request


class DeploymentVerifier:
    def __init__(self, base_url: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.auth_token = None
        self.results = []

    def _log(self, status: str, check_name: str, message: str = ""):
        symbol = "+" if status == "PASS" else ("-" if status == "FAIL" else "*")
        detail = f" - {message}" if message else ""
        print(f"[{symbol}] {check_name}: {status}{detail}")
        self.results.append({"check": check_name, "status": status, "message": message})

    def _make_request(self, path: str, method: str = "GET", data: dict = None, headers: dict = None):
        url = f"{self.base_url}{path}"
        req_headers = {"User-Agent": "DeploymentVerifier/1.0"}
        if headers:
            req_headers.update(headers)

        payload = None
        if data is not None:
            req_headers["Content-Type"] = "application/json"
            payload = json.dumps(data).encode("utf-8")

        req = urllib.request.Request(url, data=payload, headers=req_headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                status_code = resp.status
                body = resp.read().decode("utf-8")
                return status_code, body, None
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8") if e.fp else ""
            return e.code, body, None
        except Exception as e:
            return 0, "", str(e)

    def check_health(self) -> bool:
        check = "Health Check (/api/health)"
        status_code, body, err = self._make_request("/api/health")
        if err:
            self._log("FAIL", check, f"Network error: {err}")
            return False
        if status_code != 200:
            self._log("FAIL", check, f"Expected HTTP 200, received {status_code}")
            return False
        try:
            data = json.loads(body)
            status_val = data.get("status")
            if status_val in ("healthy", "degraded"):
                self._log("PASS", check, f"Status={status_val}, DB={data.get('database')}")
                return True
            else:
                self._log("FAIL", check, f"Unexpected health payload: {data}")
                return False
        except json.JSONDecodeError:
            self._log("FAIL", check, "Invalid JSON response")
            return False

    def check_static_frontend(self) -> bool:
        check = "Static Frontend (GET /)"
        status_code, body, err = self._make_request("/")
        if err or status_code != 200:
            self._log("FAIL", check, f"HTTP {status_code}, error={err}")
            return False
        if "<!DOCTYPE html>" in body or "Smart Water Usage Advisor" in body:
            self._log("PASS", check, "HTML landing page served successfully")
            return True
        self._log("FAIL", check, "HTML content missing expected markup")
        return False

    def check_vendored_chart_js(self) -> bool:
        check = "Vendored Chart.js (/js/vendor/chart.umd.js)"
        status_code, body, err = self._make_request("/js/vendor/chart.umd.js")
        if err or status_code != 200:
            self._log("FAIL", check, f"HTTP {status_code}, error={err}")
            return False
        if "Chart" in body and ("umd" in body.lower() or "function" in body):
            self._log("PASS", check, f"Chart.js bundle served ({len(body)} bytes)")
            return True
        self._log("FAIL", check, "Chart.js asset signature missing")
        return False

    def check_authentication(self) -> bool:
        check = "Authentication (POST /api/auth/login)"
        login_payload = {
            "email": "sarah.jenkins@example.com",
            "password": "ResidentPass2026!"
        }
        status_code, body, err = self._make_request("/api/auth/login", method="POST", data=login_payload)
        if err or status_code != 200:
            self._log("FAIL", check, f"HTTP {status_code}, error={err}, response={body}")
            return False
        try:
            data = json.loads(body)
            token = data.get("token") or data.get("access_token")
            if token and len(token) > 20:
                self.auth_token = token
                self._log("PASS", check, f"JWT token issued for user {data.get('user', {}).get('email')}")
                return True
            self._log("FAIL", check, f"Token missing from response: {data}")
            return False
        except json.JSONDecodeError:
            self._log("FAIL", check, "Invalid JSON response")
            return False

    def check_protected_dashboard(self) -> bool:
        check = "Protected Dashboard (GET /api/dashboard/summary)"
        if not self.auth_token:
            self._log("FAIL", check, "Skipped due to prior authentication failure")
            return False
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        status_code, body, err = self._make_request("/api/dashboard/summary", headers=headers)
        if err or status_code != 200:
            self._log("FAIL", check, f"HTTP {status_code}, error={err}")
            return False
        try:
            data = json.loads(body)
            if any(k in data for k in ("user", "today_usage_liters", "today_consumption_liters", "meter_id", "persona")):
                self._log("PASS", check, f"Dashboard summary retrieved successfully")
                return True
            self._log("FAIL", check, f"Expected dashboard fields missing in: {list(data.keys())}")
            return False
        except json.JSONDecodeError:
            self._log("FAIL", check, "Invalid JSON response")
            return False

    def check_bola_idor_protection(self) -> bool:
        check = "BOLA/IDOR Protection (Cross-Tenant Access Rejection)"
        if not self.auth_token:
            self._log("FAIL", check, "Skipped due to prior authentication failure")
            return False
        # Sarah Jenkins owns meter 1; querying meter 2 must be rejected with HTTP 403 Forbidden
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        status_code, body, err = self._make_request("/api/v1/forecast/meters/2", headers=headers)
        if status_code == 403:
            self._log("PASS", check, "Cross-tenant access correctly denied with HTTP 403 Forbidden")
            return True
        self._log("FAIL", check, f"Expected HTTP 403 Forbidden, but received HTTP {status_code}")
        return False

    def check_forecasting_endpoint(self) -> bool:
        check = "Predictive Forecaster (GET /api/v1/forecast/meters/1)"
        if not self.auth_token:
            self._log("FAIL", check, "Skipped due to prior authentication failure")
            return False
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        status_code, body, err = self._make_request("/api/v1/forecast/meters/1", headers=headers)
        if err or status_code != 200:
            self._log("FAIL", check, f"HTTP {status_code}, error={err}")
            return False
        try:
            data = json.loads(body)
            forecast = data.get("forecast")
            if isinstance(forecast, list) and len(forecast) == 7:
                first_step = forecast[0]
                has_bounds = "lower_bound" in first_step and "upper_bound" in first_step
                detail = "7-day projection with uncertainty bounds" if has_bounds else "7-day projection"
                self._log("PASS", check, detail)
                return True
            self._log("FAIL", check, f"Invalid forecast array: {forecast}")
            return False
        except json.JSONDecodeError:
            self._log("FAIL", check, "Invalid JSON response")
            return False

    def check_chatbot_endpoint(self) -> bool:
        check = "Grounded Conservation Chatbot (POST /api/v1/chat)"
        if not self.auth_token:
            self._log("FAIL", check, "Skipped due to prior authentication failure")
            return False
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        chat_payload = {
            "message": "I noticed high water usage, could there be a continuous leak in my pipes?",
            "meter_id": 1
        }
        status_code, body, err = self._make_request("/api/v1/chat", method="POST", data=chat_payload, headers=headers)
        if err or status_code != 200:
            self._log("FAIL", check, f"HTTP {status_code}, error={err}")
            return False
        try:
            data = json.loads(body)
            reply = data.get("response", "")
            if len(reply) > 20:
                self._log("PASS", check, f"Grounded response received ({len(reply)} chars)")
                return True
            self._log("FAIL", check, f"Empty or truncated reply: {data}")
            return False
        except json.JSONDecodeError:
            self._log("FAIL", check, "Invalid JSON response")
            return False

    def run_all(self) -> bool:
        print(f"\n========================================================")
        print(f"SMART WATER USAGE ADVISOR - DEPLOYMENT SMOKE PROBE")
        print(f"Target URL: {self.base_url}")
        print(f"========================================================\n")

        checks = [
            self.check_health,
            self.check_static_frontend,
            self.check_vendored_chart_js,
            self.check_authentication,
            self.check_protected_dashboard,
            self.check_bola_idor_protection,
            self.check_forecasting_endpoint,
            self.check_chatbot_endpoint,
        ]

        passed = 0
        for chk in checks:
            if chk():
                passed += 1

        total = len(checks)
        print(f"\n--------------------------------------------------------")
        print(f"Results: {passed}/{total} probes passed")
        print(f"--------------------------------------------------------\n")
        return passed == total


def main():
    parser = argparse.ArgumentParser(description="Verify Smart Water Usage Advisor Deployment")
    parser.add_argument("--url", default="http://localhost:5000", help="Base URL of target service")
    parser.add_argument("--timeout", type=float, default=10.0, help="Request timeout in seconds")
    args = parser.parse_args()

    verifier = DeploymentVerifier(base_url=args.url, timeout=args.timeout)
    success = verifier.run_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
