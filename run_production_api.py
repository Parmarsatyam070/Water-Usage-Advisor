"""
Smart Water Usage Advisor - Phase 5 Production-Style API Server
Location: run_production_api.py

Launches the production-style Flask application:
- Application Factory Pattern via backend.app.create_app()
- Hosts all 7 modular Blueprints:
  - /api/auth
  - /api/dashboard
  - /api/v1/telemetry
  - /api/v1/forecast
  - /api/v1/anomalies
  - /api/v1/chat
  - /api/health
- Serves the existing Phase 4 static frontend assets at http://127.0.0.1:5000/
- Note: Production process managers (Gunicorn), Docker containers, and cloud orchestrators
  remain strictly reserved for Phase 6.
"""

import os
import sys
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

DEV_DIR = os.path.join(BASE_DIR, "4_DEVELOPMENT")
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from backend.app import create_app
from backend.config import get_config


def main():
    parser = argparse.ArgumentParser(description="Smart Water Usage Advisor Phase 5 Production-Style API Server")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host interface (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind (default: 5000)")
    parser.add_argument("--env", type=str, default=None, help="Environment override (development, testing, production)")
    args = parser.parse_args()

    if args.env:
        os.environ["ENVIRONMENT"] = args.env

    config = get_config()
    app = create_app(config)

    print("=" * 70)
    print("[+] SMART WATER USAGE ADVISOR - PHASE 5 PRODUCTION-STYLE API SERVER")
    print("=" * 70)
    print(f"Environment:             {config.ENVIRONMENT}")
    print(f"Static Frontend Served:  http://{args.host}:{args.port}/")
    print(f"Dashboard API Endpoints: http://{args.host}:{args.port}/api/dashboard/")
    print(f"Modular v1 API:          http://{args.host}:{args.port}/api/v1/")
    print(f"Health Probe:            http://{args.host}:{args.port}/api/health")
    print("Zero External CDN:       Vendored Chart.js v4.4.1 offline bundle")
    print("Phase 6 Notice:          Docker & Gunicorn reserved for Phase 6 deployment")
    print("Press Ctrl+C to stop.")
    print("=" * 70)

    app.run(host=args.host, port=args.port, debug=config.DEBUG)


if __name__ == "__main__":
    main()
