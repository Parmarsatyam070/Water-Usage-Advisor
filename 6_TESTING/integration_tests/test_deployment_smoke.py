"""
Automated Deployment Smoke Test Suite
Phase 6 - Deployment & Verification Layer

Validates deployment contracts, WSGI entry point, Gunicorn configuration syntax,
static asset serving, health endpoints, and fail-closed production security.
"""

import os
import sys
import importlib.util
import pytest

# Ensure repository root is on sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

DEV_DIR = os.path.join(BASE_DIR, "4_DEVELOPMENT")
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from backend.app import create_app
from backend.config import BaseConfig, ProductionConfig, TestingConfig


@pytest.fixture
def test_client():
    app = create_app(config=TestingConfig())
    with app.test_client() as client:
        yield client


class TestDeploymentSmoke:
    """Validates deployment contracts and packaging integrity."""

    def test_wsgi_entrypoint_loads(self):
        """Verify 8_DEPLOYMENT/wsgi.py cleanly loads and exports a Flask application instance."""
        wsgi_path = os.path.join(BASE_DIR, "8_DEPLOYMENT", "wsgi.py")
        assert os.path.exists(wsgi_path), "8_DEPLOYMENT/wsgi.py must exist"

        spec = importlib.util.spec_from_file_location("deployment_wsgi", wsgi_path)
        wsgi_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(wsgi_module)

        assert hasattr(wsgi_module, "app"), "wsgi.py must export an 'app' instance"
        assert wsgi_module.app is not None
        assert wsgi_module.app.name in ("backend.app", "4_DEVELOPMENT.backend.app")

    def test_gunicorn_configuration_syntax(self):
        """Verify 8_DEPLOYMENT/gunicorn.conf.py parses cleanly with valid parameters."""
        gunicorn_path = os.path.join(BASE_DIR, "8_DEPLOYMENT", "gunicorn.conf.py")
        assert os.path.exists(gunicorn_path), "8_DEPLOYMENT/gunicorn.conf.py must exist"

        config_dict = {}
        with open(gunicorn_path, "r", encoding="utf-8") as f:
            code = compile(f.read(), gunicorn_path, "exec")
            exec(code, config_dict)

        assert "workers" in config_dict
        assert isinstance(config_dict["workers"], int)
        assert config_dict["workers"] >= 1

        assert "threads" in config_dict
        assert isinstance(config_dict["threads"], int)
        assert config_dict["threads"] >= 1

        assert "timeout" in config_dict
        assert isinstance(config_dict["timeout"], int)
        assert config_dict["timeout"] >= 30

        assert config_dict.get("preload_app") is False
        assert config_dict.get("worker_class") in ("gthread", "sync")

    def test_health_endpoint_contract(self, test_client):
        """Verify /api/health returns HTTP 200 with operational component statuses."""
        resp = test_client.get("/api/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data is not None
        assert data.get("status") in ("healthy", "degraded")
        assert "services" in data
        assert "database" in data
        assert "timestamp" in data

    def test_production_config_enforcement(self, monkeypatch):
        """Verify ProductionConfig fails closed when production secrets are missing or default."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
        monkeypatch.delenv("SECRET_KEY", raising=False)

        # In production mode, missing secret keys must raise ValueError
        with pytest.raises(ValueError, match="JWT_SECRET_KEY"):
            ProductionConfig()

        # Default fallback JWT key must raise ValueError
        monkeypatch.setenv("JWT_SECRET_KEY", "dev-fallback-jwt-secret-water-advisor-2026")
        with pytest.raises(ValueError, match="JWT_SECRET_KEY"):
            ProductionConfig()

        # Valid JWT key but default SECRET_KEY must raise ValueError
        monkeypatch.setenv("JWT_SECRET_KEY", "custom-valid-production-jwt-key-64-characters-long-hex-string")
        monkeypatch.setenv("SECRET_KEY", "dev-fallback-secret-water-advisor-2026")
        with pytest.raises(ValueError, match="SECRET_KEY"):
            ProductionConfig()

    def test_static_frontend_served_at_root(self, test_client):
        """Verify GET / serves the Phase 4 HTML user interface."""
        resp = test_client.get("/")
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        assert "<!DOCTYPE html>" in html or "<html" in html
        assert "Smart Water Usage Advisor" in html

    def test_offline_chart_js_accessible(self, test_client):
        """Verify locally vendored Chart.js bundle is accessible via static routing."""
        resp = test_client.get("/js/vendor/chart.umd.js")
        assert resp.status_code == 200
        content = resp.get_data(as_text=True)
        assert len(content) > 50000, "Chart.js bundle should be full-sized"
        assert "Chart" in content

    def test_deployment_artifacts_exist(self):
        """Verify all mandatory deployment artifacts exist with non-empty content."""
        deployment_dir = os.path.join(BASE_DIR, "8_DEPLOYMENT")
        expected_files = [
            "Dockerfile",
            "docker-compose.yml",
            ".dockerignore",
            "gunicorn.conf.py",
            "wsgi.py",
            "requirements-deploy.txt",
            "verify_deployment.py",
        ]
        for filename in expected_files:
            file_path = os.path.join(deployment_dir, filename)
            assert os.path.exists(file_path), f"Missing deployment file: {filename}"
            assert os.path.getsize(file_path) > 0, f"Empty deployment file: {filename}"
