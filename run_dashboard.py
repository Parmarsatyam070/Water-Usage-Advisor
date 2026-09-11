"""
Smart Water Usage Advisor - Phase 4 Local Development Server
Location: run_dashboard.py

Standard-library Python HTTP server for Phase 4 Dashboard & Web UI evaluation.
Adheres strictly to the Phase 4 constraints:
- Uses ONLY Python's built-in `http.server` and `urllib` modules.
- NO Flask, FastAPI, Django, Express, or external backend frameworks.
- Serves static assets from `4_DEVELOPMENT/frontend/`.
- Routes `/api/dashboard/*` requests to `4_DEVELOPMENT/backend/dashboard_data_service.py`.
- Returns structured JSON DTOs to the browser.
- Production Flask REST API remains strictly reserved for Phase 5.
"""

import os
import sys
import json
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Dict, Any

# Ensure project directories are on python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "4_DEVELOPMENT", "frontend")
BACKEND_DIR = os.path.join(BASE_DIR, "4_DEVELOPMENT", "backend")

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if os.path.join(BASE_DIR, "4_DEVELOPMENT") not in sys.path:
    sys.path.insert(0, os.path.join(BASE_DIR, "4_DEVELOPMENT"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from backend.dashboard_data_service import get_data_service


class DashboardRequestHandler(SimpleHTTPRequestHandler):
    """
    HTTP Request Handler serving static frontend assets and routing local API requests.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def _send_json_response(self, data: Any, status: int = 200):
        """Helper to send a formatted JSON response with CORS headers."""
        payload = json.dumps(data, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self):
        """Handle CORS pre-flight requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        """Route GET requests: either serve static files or handle /api/dashboard/* endpoints."""
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        # Parse user_id from query params, default to 1
        user_id = 1
        if "user_id" in query_params:
            try:
                user_id = int(query_params["user_id"][0])
            except ValueError:
                user_id = 1

        ds = get_data_service()

        if path == "/api/dashboard/summary":
            summary = ds.get_summary(user_id=user_id)
            self._send_json_response(summary)
            return

        elif path == "/api/dashboard/consumption":
            time_range = query_params.get("range", ["30d"])[0]
            consumption = ds.get_consumption(user_id=user_id, time_range=time_range)
            self._send_json_response(consumption)
            return

        elif path == "/api/dashboard/forecast":
            forecast = ds.get_forecast(user_id=user_id)
            self._send_json_response(forecast)
            return

        elif path == "/api/dashboard/anomalies":
            anomalies = ds.get_anomalies(user_id=user_id)
            self._send_json_response(anomalies)
            return

        elif path == "/api/dashboard/recommendations":
            recs = ds.get_recommendations(user_id=user_id)
            self._send_json_response(recs)
            return

        elif path == "/api/dashboard/goals":
            goals = ds.get_goals(user_id=user_id)
            self._send_json_response(goals)
            return

        elif path == "/api/dashboard/users":
            # List available demo personas
            users_list = [
                {"user_id": 1, "name": "Sarah Jenkins", "type": "Residential Single-Family", "meter_id": 1},
                {"user_id": 2, "name": "Marcus Vance", "type": "Residential Multi-Family", "meter_id": 2},
                {"user_id": 3, "name": "Elena Rostova", "type": "Commercial Office Facility", "meter_id": 3}
            ]
            self._send_json_response(users_list)
            return

        # Fallback to serving static frontend files
        super().do_GET()

    def do_POST(self):
        """Route POST requests (e.g. Chatbot interaction)."""
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/api/dashboard/chat":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                data = json.loads(body) if body else {}
            except json.JSONDecodeError:
                self._send_json_response({"error": "Invalid JSON in request body."}, status=400)
                return

            user_id = int(data.get("user_id", 1))
            message = str(data.get("message", "")).strip()

            if not message:
                self._send_json_response({"error": "Message parameter is required."}, status=400)
                return

            ds = get_data_service()
            chat_response = ds.handle_chat(user_id=user_id, user_message=message)
            self._send_json_response(chat_response)
            return

        self._send_json_response({"error": f"Endpoint not found: {path}"}, status=404)


def create_dashboard_server(host: str = "127.0.0.1", port: int = 8080) -> HTTPServer:
    """Creates and returns the configured HTTPServer instance."""
    server_address = (host, port)
    httpd = HTTPServer(server_address, DashboardRequestHandler)
    return httpd


def run_server(host: str = "127.0.0.1", port: int = 8080):
    """Starts the local development server and serves requests until interrupted."""
    httpd = create_dashboard_server(host, port)
    print("=" * 60)
    print("SMART WATER USAGE ADVISOR - PHASE 4 LOCAL DEVELOPMENT SERVER")
    print("=" * 60)
    print(f"Serving Static Frontend from: {FRONTEND_DIR}")
    print(f"Dashboard available at:       http://{host}:{port}/")
    print(f"API endpoints routed to:      http://{host}:{port}/api/dashboard/")
    print("Zero external frameworks:     Python standard-library http.server")
    print("Press Ctrl+C to stop.")
    print("=" * 60)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard server...")
    finally:
        httpd.server_close()
        print("Dashboard server stopped.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Smart Water Usage Advisor Phase 4 Local Server")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind (default: 8080)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address (default: 127.0.0.1)")
    args = parser.parse_args()

    run_server(host=args.host, port=args.port)
