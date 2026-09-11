"""
Smart Water Usage Advisor - Production-Style Flask Application Factory
Location: 4_DEVELOPMENT/backend/app.py

Implements:
- Application Factory Pattern (create_app)
- Explicit CORS whitelisting (never wildcard * in production)
- Serving of existing Phase 4 static frontend assets from 4_DEVELOPMENT/frontend/ at /
- Complete registration of all 7 modular API blueprints
- Centralized, sanitized JSON error handlers
"""

import os
import sys
from flask import Flask, send_from_directory
from flask_cors import CORS

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

DEV_DIR = os.path.join(BASE_DIR, "4_DEVELOPMENT")
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from backend.config import get_config, BaseConfig
from backend.api.middleware import register_error_handlers

# Import upstream Phase 5/6 Blueprints
from backend.api.routes_auth import auth_bp
from backend.api.routes_dashboard import dashboard_bp
from backend.api.routes_telemetry import telemetry_bp
from backend.api.routes_forecasting import forecasting_bp
from backend.api.routes_anomalies import anomalies_bp
from backend.api.routes_chat import chat_bp
from backend.api.routes_health import health_bp

# Import Phase 7 Advanced Water Intelligence Blueprints
from backend.api.routes_water_intelligence import water_bp
from backend.api.routes_alerts_history import alerts_history_bp
from backend.api.routes_sdg6 import sdg6_bp
from backend.api.routes_goals_adv import goals_adv_bp
from backend.api.routes_reports import reports_bp
from backend.api.routes_admin import admin_bp


def create_app(config=None) -> Flask:
    """
    Constructs and configures the production-style Flask application instance.
    """
    app_config = config or get_config()

    app = Flask(
        __name__,
        static_folder=app_config.FRONTEND_DIR,
        static_url_path=""
    )

    # Apply configuration object
    app.config.from_object(app_config)

    # Enable CORS for explicitly whitelisted origins
    allowed_origins = getattr(app_config, "CORS_ALLOWED_ORIGINS", ["http://127.0.0.1:8080", "http://localhost:8080"])
    CORS(
        app,
        resources={r"/api/*": {"origins": allowed_origins}},
        supports_credentials=True
    )

    # Register centralized error handlers
    register_error_handlers(app)

    # Register upstream Phase 5/6 Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(telemetry_bp)
    app.register_blueprint(forecasting_bp)
    app.register_blueprint(anomalies_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(health_bp)

    # Register Phase 7 Blueprints
    app.register_blueprint(water_bp)
    app.register_blueprint(alerts_history_bp)
    app.register_blueprint(sdg6_bp)
    app.register_blueprint(goals_adv_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(admin_bp)

    # Static Frontend Asset Serving at http://127.0.0.1:5000/
    @app.route("/", methods=["GET"])
    def index():
        """Serves Phase 4 index.html at root."""
        return send_from_directory(app_config.FRONTEND_DIR, "index.html")

    @app.route("/<path:path>", methods=["GET"])
    def static_proxy(path):
        """Serves CSS, JS, and vendored Chart.js assets safely from FRONTEND_DIR."""
        target_path = os.path.join(app_config.FRONTEND_DIR, path)
        if os.path.isfile(target_path):
            return send_from_directory(app_config.FRONTEND_DIR, path)
        # Fallback to index.html for client-side routing if required
        return send_from_directory(app_config.FRONTEND_DIR, "index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=True)
