"""
Smart Water Usage Advisor - Backend Configuration Module
Location: 4_DEVELOPMENT/backend/config.py

Provides environment-aware configuration classes (Development, Testing, Production).
Enforces fail-closed security policies in Production mode.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FRONTEND_DIR = os.path.join(BASE_DIR, "4_DEVELOPMENT", "frontend")


class BaseConfig:
    """Base application configuration with secure defaults."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-fallback-secret-water-advisor-2026")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-fallback-jwt-secret-water-advisor-2026")
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", 24))
    JWT_EXPIRATION_DELTA = timedelta(hours=JWT_EXPIRATION_HOURS)
    
    # Static asset path
    FRONTEND_DIR = FRONTEND_DIR
    
    # CORS Origins (never wildcard * in production)
    CORS_ALLOWED_ORIGINS = os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://127.0.0.1:8080,http://localhost:8080,http://127.0.0.1:5000,http://localhost:5000"
    ).split(",")

    # Demo Auth Toggle (Defaults to False, enabled only in Dev/Test)
    ENABLE_DEMO_AUTH = False
    ENVIRONMENT = "development"


class DevelopmentConfig(BaseConfig):
    """Configuration for local development."""
    DEBUG = True
    ENVIRONMENT = "development"
    ENABLE_DEMO_AUTH = os.getenv("ENABLE_DEMO_AUTH", "true").lower() in ("true", "1", "yes")


class TestingConfig(BaseConfig):
    """Configuration for automated test execution."""
    TESTING = True
    DEBUG = False
    ENVIRONMENT = "testing"
    ENABLE_DEMO_AUTH = True
    # In-memory or isolated test database
    USE_SQLITE_TEST_FALLBACK = True


class ProductionConfig(BaseConfig):
    """Configuration for production deployment (fail-closed security)."""
    DEBUG = False
    TESTING = False
    ENVIRONMENT = "production"
    # In production, demo token generation is strictly forbidden
    ENABLE_DEMO_AUTH = False

    def __init__(self):
        super().__init__()
        # Enforce that secrets are explicitly set in production
        if not os.getenv("JWT_SECRET_KEY") or self.JWT_SECRET_KEY.startswith("dev-fallback"):
            raise ValueError(
                "SECURITY ERROR: Production configuration requires an explicit, non-default JWT_SECRET_KEY environment variable."
            )
        if not os.getenv("SECRET_KEY") or self.SECRET_KEY.startswith("dev-fallback"):
            raise ValueError(
                "SECURITY ERROR: Production configuration requires an explicit, non-default SECRET_KEY environment variable."
            )


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig
}

def get_config():
    """Returns the active configuration object based on ENVIRONMENT env var."""
    env = os.getenv("ENVIRONMENT", "development").lower()
    cfg_class = config_by_name.get(env, DevelopmentConfig)
    return cfg_class()
