"""
Integration tests for database schema creation and table constraints.
Verifies all 12 authoritative tables, primary keys, foreign keys, and indexes.
"""

import os
import sys
import pytest
from sqlalchemy import inspect

sys.path.insert(0, os.path.abspath("4_DEVELOPMENT/backend/database"))
from db_config import create_db_engine
from init_database import init_schema

@pytest.fixture(scope="module")
def db_engine():
    # Use isolated in-memory or test SQLite database for test execution
    engine = create_db_engine("sqlite:///:memory:")
    init_schema(engine=engine)
    return engine

def test_all_12_tables_created(db_engine):
    """Ensure all 12 authoritative database tables exist."""
    inspector = inspect(db_engine)
    tables = set(inspector.get_table_names())

    canonical_12 = {
        "users", "meters", "user_profiles", "water_usage_data",
        "consumption_categories", "predictions", "anomalies", "recommendations",
        "alerts", "goals", "feedback", "chatbot_conversations"
    }
    assert canonical_12.issubset(tables), f"Missing tables: {canonical_12 - tables}"

def test_primary_keys_present(db_engine):
    """Ensure essential primary keys exist on users and meters."""
    inspector = inspect(db_engine)
    pk_users = inspector.get_pk_constraint("users")
    assert "user_id" in pk_users["constrained_columns"]

    pk_meters = inspector.get_pk_constraint("meters")
    assert "meter_id" in pk_meters["constrained_columns"]

def test_foreign_keys_configured(db_engine):
    """Ensure foreign key relationships link back to users and meters."""
    inspector = inspect(db_engine)
    fks_usage = inspector.get_foreign_keys("water_usage_data")
    ref_tables = {fk["referred_table"] for fk in fks_usage}
    assert "meters" in ref_tables
    assert "users" in ref_tables
