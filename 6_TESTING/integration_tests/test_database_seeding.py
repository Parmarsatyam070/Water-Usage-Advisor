"""
Integration tests for database seeding.
Verifies record populations, bcrypt hash validation, telemetry counts, and category integrity.
"""

import os
import sys
import pytest
from sqlalchemy import text
import bcrypt

sys.path.insert(0, os.path.abspath("4_DEVELOPMENT/backend/database"))
from db_config import create_db_engine
from init_database import init_schema
from seed_database import seed_database

@pytest.fixture(scope="module")
def seeded_engine():
    # Use isolated test SQLite database
    test_db = "sqlite:///test_seeded_water_advisor.db"
    engine = create_db_engine(test_db)
    init_schema(engine=engine)
    seed_database(engine=engine)
    yield engine
    # Teardown
    if os.path.isfile("test_seeded_water_advisor.db"):
        try:
            os.remove("test_seeded_water_advisor.db")
        except Exception:
            pass

def test_demo_users_seeded(seeded_engine):
    """Verify 3 demo users are seeded with correct roles."""
    with seeded_engine.connect() as conn:
        res = conn.execute(text("SELECT email, user_type FROM users ORDER BY user_id")).fetchall()
        assert len(res) == 3
        user_types = [r[1] for r in res]
        assert user_types == ["household", "institution", "municipal"]

def test_passwords_are_bcrypt_hashed(seeded_engine):
    """Verify that stored password hashes are authentic bcrypt hashes and verify correctly."""
    with seeded_engine.connect() as conn:
        hashes = conn.execute(text("SELECT password_hash FROM users")).fetchall()
        for (h,) in hashes:
            assert h.startswith(("$2b$", "$2a$"))
            assert bcrypt.checkpw(b"DemoWaterAdvisor2026!", h.encode("utf-8"))

def test_telemetry_records_seeded(seeded_engine):
    """Verify all 6,480 telemetry rows are present in water_usage_data."""
    with seeded_engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM water_usage_data")).scalar()
        assert count == 6480

def test_categories_and_goals_seeded(seeded_engine):
    """Verify category disaggregation and goals are populated."""
    with seeded_engine.connect() as conn:
        cat_count = conn.execute(text("SELECT COUNT(*) FROM consumption_categories")).scalar()
        goal_count = conn.execute(text("SELECT COUNT(*) FROM goals")).scalar()
        assert cat_count == 6
        assert goal_count == 3
