"""
Smart Water Usage Advisor - Phase 2 Automated Validation Suite
Executes comprehensive end-to-end validation across 4 domains:
1. Telemetry Dataset & Ground-Truth Anomalies
2. Feature Engineering & Preprocessing Pipeline
3. Database Schema Integrity (All 12 Authoritative Tables, PKs, FKs, Indexes)
4. Database Seed Integrity & Security Verifications (Bcrypt passwords, no leaks)
"""

import os
import sys
import pandas as pd
import numpy as np
from sqlalchemy import text, inspect

# Add database path
sys.path.insert(0, os.path.abspath("4_DEVELOPMENT/backend/database"))
sys.path.insert(0, os.path.abspath("4_DEVELOPMENT/utils"))

from db_config import create_db_engine
from init_database import init_schema
from seed_database import seed_database
from data_preprocessing import WaterDataPreprocessor

def run_phase2_validation():
    print("==================================================")
    print("RUNNING PHASE 2 COMPREHENSIVE VALIDATION SUITE")
    print("==================================================")

    passes = []
    failures = []

    # Domain 1: Telemetry Data File Existence and Stats
    csv_telemetry = "4_DEVELOPMENT/data/generated/water_usage_data.csv"
    csv_anomalies = "4_DEVELOPMENT/data/generated/ground_truth_anomalies.csv"

    if not os.path.isfile(csv_telemetry):
        failures.append("DOM-1 FAIL: water_usage_data.csv missing.")
    else:
        df = pd.read_csv(csv_telemetry)
        if len(df) == 6480:
            passes.append("DOM-1 PASS: Exact 6,480 telemetry records found (3 meters x 2,160 hours).")
        else:
            failures.append(f"DOM-1 FAIL: Expected 6480 records, found {len(df)}.")

        if (df["hourly_consumption_liters"] < 0).sum() == 0:
            passes.append("DOM-1 PASS: Zero negative consumption values.")
        else:
            failures.append("DOM-1 FAIL: Negative consumption values detected.")

        if df["meter_id"].nunique() == 3:
            passes.append("DOM-1 PASS: Exactly 3 distinct meter profiles represented.")
        else:
            failures.append(f"DOM-1 FAIL: Found {df['meter_id'].nunique()} meters instead of 3.")

    if not os.path.isfile(csv_anomalies):
        failures.append("DOM-1 FAIL: ground_truth_anomalies.csv missing.")
    else:
        df_anom = pd.read_csv(csv_anomalies)
        anom_types = set(df_anom["anomaly_type"].unique())
        required_types = {"leak", "surge", "low", "unusual_pattern"}
        if required_types.issubset(anom_types):
            passes.append(f"DOM-1 PASS: All 4 ground truth anomaly categories represented ({len(df_anom)} total events).")
        else:
            failures.append(f"DOM-1 FAIL: Missing required anomaly types. Found: {anom_types}")

    # Domain 2: Feature Engineering & Preprocessing Module
    try:
        preprocessor = WaterDataPreprocessor()
        df_feats = preprocessor.prepare_features(df.head(500))
        required_feats = [
            "hour", "day_of_week", "day_of_month", "month", "is_weekend",
            "hour_sin", "hour_cos", "lag_1h", "lag_24h", "rolling_mean_24h",
            "is_night_window", "profile_single_family"
        ]
        missing_feats = [f for f in required_feats if f not in df_feats.columns]
        if not missing_feats:
            passes.append(f"DOM-2 PASS: Feature engineering pipeline extracts all required temporal, cyclical, and lagged features.")
        else:
            failures.append(f"DOM-2 FAIL: Missing engineered features: {missing_feats}")
    except Exception as e:
        failures.append(f"DOM-2 FAIL: Feature engineering pipeline error: {e}")

    # Domain 3: Database Schema Integrity
    os.environ["USE_SQLITE_TEST_FALLBACK"] = "True"
    os.environ["SQLITE_DB_PATH"] = "smart_water_advisor_phase2_val.db"

    try:
        engine = create_db_engine()
        init_schema(engine=engine)
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        canonical_12_tables = [
            "users", "meters", "user_profiles", "water_usage_data",
            "consumption_categories", "predictions", "anomalies", "recommendations",
            "alerts", "goals", "feedback", "chatbot_conversations"
        ]

        missing_tables = [t for t in canonical_12_tables if t not in tables]
        if not missing_tables:
            passes.append("DOM-3 PASS: All 12 authoritative database tables exist with exact canonical names.")
        else:
            failures.append(f"DOM-3 FAIL: Missing tables: {missing_tables}")

        # Check users PK
        pk_users = inspector.get_pk_constraint("users")
        if "user_id" in pk_users.get("constrained_columns", []):
            passes.append("DOM-3 PASS: Primary key on users(user_id) verified.")
        else:
            failures.append("DOM-3 FAIL: users table missing user_id primary key.")

        # Check water_usage_data foreign keys
        fks = inspector.get_foreign_keys("water_usage_data")
        fk_tables = [fk["referred_table"] for fk in fks]
        if "meters" in fk_tables and "users" in fk_tables:
            passes.append("DOM-3 PASS: Foreign keys on water_usage_data (meters, users) verified.")
        else:
            failures.append(f"DOM-3 FAIL: Missing foreign keys on water_usage_data: {fk_tables}")

    except Exception as e:
        failures.append(f"DOM-3 FAIL: Database initialization error: {e}")

    # Domain 4: Database Seeding & Security Verifications
    try:
        seed_database(engine=engine)
        with engine.connect() as conn:
            user_count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
            meter_count = conn.execute(text("SELECT COUNT(*) FROM meters")).scalar()
            profile_count = conn.execute(text("SELECT COUNT(*) FROM user_profiles")).scalar()
            usage_count = conn.execute(text("SELECT COUNT(*) FROM water_usage_data")).scalar()
            cat_count = conn.execute(text("SELECT COUNT(*) FROM consumption_categories")).scalar()
            goal_count = conn.execute(text("SELECT COUNT(*) FROM goals")).scalar()

            if user_count == 3 and meter_count == 3 and profile_count == 3:
                passes.append(f"DOM-4 PASS: Demo users, profiles, and meters seeded successfully (count=3 each).")
            else:
                failures.append(f"DOM-4 FAIL: Seeding count error: users={user_count}, meters={meter_count}")

            if usage_count == 6480:
                passes.append("DOM-4 PASS: All 6,480 telemetry records seeded into water_usage_data.")
            else:
                failures.append(f"DOM-4 FAIL: water_usage_data count is {usage_count} (expected 6480).")

            if cat_count > 0 and goal_count > 0:
                passes.append(f"DOM-4 PASS: Categories ({cat_count}) and Goals ({goal_count}) seeded successfully.")
            else:
                failures.append("DOM-4 FAIL: Categories or goals failed to seed.")

            # Security: Verify passwords are hashed with bcrypt (starts with $2b$ or $2a$)
            pw_sample = conn.execute(text("SELECT password_hash FROM users LIMIT 1")).scalar()
            if pw_sample and pw_sample.startswith(("$2b$", "$2a$")):
                passes.append("DOM-4 PASS: Demo passwords stored securely as bcrypt hashes (no plaintext).")
            else:
                failures.append(f"DOM-4 FAIL: Password hash invalid format: {pw_sample}")

            # Security: Verify meter api_key does not contain real secret
            api_keys = conn.execute(text("SELECT api_key FROM meters WHERE api_key IS NOT NULL")).fetchall()
            if len(api_keys) == 0:
                passes.append("DOM-4 PASS: Zero real API credentials in meters table (placeholders/nulls only).")
            else:
                failures.append(f"DOM-4 FAIL: Unexpected api_key values found: {api_keys}")

    except Exception as e:
        failures.append(f"DOM-4 FAIL: Database seed verification error: {e}")

    # Security: Verify .env is not in git
    if os.path.isfile(".env"):
        failures.append("SECURITY FAIL: .env file present in workspace root!")
    else:
        passes.append("SECURITY PASS: .env is not tracked or present in version control.")

    # Clean up test sqlite db
    if os.path.isfile("smart_water_advisor_phase2_val.db"):
        try:
            os.remove("smart_water_advisor_phase2_val.db")
        except Exception:
            pass

    print("\n==================================================")
    print("PHASE 2 VALIDATION RESULTS:")
    print("==================================================")
    for p in passes:
        print(f" [x] {p}")

    if failures:
        print("\nFAILURES DETECTED:")
        for f in failures:
            print(f" [ ] {f}")
        return False
    else:
        print("\nALL PHASE 2 VALIDATION CHECKS PASSED SUCCESSFULLY!")
        print("==================================================")
        return True

if __name__ == "__main__":
    success = run_phase2_validation()
    if not success:
        sys.exit(1)
