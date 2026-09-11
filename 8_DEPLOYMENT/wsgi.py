"""
Authoritative WSGI Entry Point for Smart Water Usage Advisor
Phase 6 - Deployment & Serving Layer

This module serves as the single canonical entry point for production WSGI process
managers (e.g. Gunicorn in Docker containers, cloud hosting platforms).
It instantiates the Flask application via the official application factory pattern.
"""

import os
import sys

# Ensure repository root and 4_DEVELOPMENT are in Python path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

DEV_DIR = os.path.join(BASE_DIR, "4_DEVELOPMENT")
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from backend.app import create_app

# Instantiate the single authoritative Flask application
app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
