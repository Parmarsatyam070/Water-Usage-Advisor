"""
Smart Water Usage Advisor - Database Seeder
Seeds PostgreSQL (or fallback database) with:
- 3 labeled demo users (Household, Institution, Municipality) with bcrypt password hashes
- 3 corresponding user profiles
- 3 registered meters
- 6,480 validated smart-meter telemetry records from generated CSV
- Realistic disaggregated consumption categories (bathroom, kitchen, laundry, garden, cleaning, other)
- Active conservation goals (SDG 6 targets)
"""

import os
import sys
import bcrypt
import pandas as pd
from datetime import datetime, date, timezone
from sqlalchemy import text
from db_config import create_db_engine

def get_demo_password_hash(password: str = "DemoWaterAdvisor2026!") -> str:
    """Generates a secure, bcrypt-compatible hash for demo accounts."""
    salt = bcrypt.gensalt(rounds=10)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def seed_database(engine=None, csv_path="4_DEVELOPMENT/data/generated/water_usage_data.csv"):
    eng = engine or create_db_engine()
    demo_pw_hash = get_demo_password_hash()

    print("==================================================")
    print("STARTING SMART WATER ADVISOR DATABASE SEEDING")
    print("==================================================")

    with eng.begin() as conn:
        # 1. Seed Demo Users
        print("[1/5] Seeding 3 Demo Users...")
        users_data = [
            (1, "sarah.jenkins@example.com", demo_pw_hash, "Sarah", "Jenkins", "household", "Bengaluru", "India", True),
            (2, "marcus.vance@campus.edu", demo_pw_hash, "Marcus", "Vance", "institution", "Pune", "India", True),
            (3, "elena.rostova@metro.gov", demo_pw_hash, "Elena", "Rostova", "municipal", "Delhi", "India", True)
        ]
        for u in users_data:
            conn.execute(text("""
                INSERT INTO users (user_id, email, password_hash, first_name, last_name, user_type, city, country, is_active)
                VALUES (:u_id, :email, :pw, :fn, :ln, :utype, :city, :country, :active)
                ON CONFLICT (email) DO NOTHING;
            """), {
                "u_id": u[0], "email": u[1], "pw": u[2], "fn": u[3], "ln": u[4],
                "utype": u[5], "city": u[6], "country": u[7], "active": u[8]
            })

        # 2. Seed User Profiles
        print("[2/5] Seeding User Profiles...")
        profiles_data = [
            (1, 1, 4, "house", 140.0, True, False, "municipal", "medium", "full-time", "high", "en", "standard"),
            (2, 2, 250, "commercial", 4500.0, True, False, "mixed", "high", "part-time", "high", "en", "standard"),
            (3, 3, 12000, "apartment", 18000.0, True, True, "municipal", "mixed", "full-time", "medium", "en", "aggregated")
        ]
        for p in profiles_data:
            conn.execute(text("""
                INSERT INTO user_profiles (profile_id, user_id, household_size, property_type, property_area_sqm, 
                                          has_garden, has_swimming_pool, water_source, annual_income_range, 
                                          occupancy_type, conservation_priority, preferred_communication_language, privacy_level)
                VALUES (:pid, :uid, :hsize, :ptype, :area, :garden, :pool, :source, :income, :occ, :prio, :lang, :priv)
                ON CONFLICT (user_id) DO UPDATE SET household_size = EXCLUDED.household_size;
            """), {
                "pid": p[0], "uid": p[1], "hsize": p[2], "ptype": p[3], "area": p[4], "garden": p[5],
                "pool": p[6], "source": p[7], "income": p[8], "occ": p[9], "prio": p[10], "lang": p[11], "priv": p[12]
            })

        # 3. Seed Meters
        print("[3/5] Seeding Meters...")
        meters_data = [
            (1, 1, "MTR-RES-1001", "smart", "2026-01-15", "EcoFlow Meters", None, None, "Main Domestic Supply", True),
            (2, 2, "MTR-RES-2002", "smart", "2025-11-20", "AquaSense Pro", None, None, "Campus Facilities Inflow", True),
            (3, 3, "MTR-COM-3003", "digital", "2025-08-10", "HydroMetrix Industrial", None, None, "District Main Meter", True)
        ]
        for m in meters_data:
            conn.execute(text("""
                INSERT INTO meters (meter_id, user_id, meter_serial_number, meter_type, installation_date, 
                                    manufacturer, api_key, api_endpoint, location_description, is_active)
                VALUES (:mid, :uid, :serial, :mtype, :idate, :mfg, :key, :endp, :loc, :active)
                ON CONFLICT (meter_serial_number) DO NOTHING;
            """), {
                "mid": m[0], "uid": m[1], "serial": m[2], "mtype": m[3], "idate": m[4],
                "mfg": m[5], "key": m[6], "endp": m[7], "loc": m[8], "active": m[9]
            })

        # 4. Seed Telemetry (Water Usage Data)
        print(f"[4/5] Loading Telemetry from {csv_path}...")
        if os.path.isfile(csv_path):
            df_telemetry = pd.read_csv(csv_path)
            # Take core fields
            cols_to_insert = [
                "reading_id", "meter_id", "user_id", "timestamp", "cumulative_reading",
                "hourly_consumption_liters", "daily_consumption_liters", "monthly_consumption_liters",
                "temperature_celsius", "quality_score", "data_source", "is_validated"
            ]
            records = df_telemetry[cols_to_insert].to_dict(orient="records")

            # Batch insert in chunks of 1000
            chunk_size = 1000
            for i in range(0, len(records), chunk_size):
                chunk = records[i:i + chunk_size]
                conn.execute(text("""
                    INSERT INTO water_usage_data (reading_id, meter_id, user_id, timestamp, cumulative_reading,
                                                 hourly_consumption_liters, daily_consumption_liters, monthly_consumption_liters,
                                                 temperature_celsius, quality_score, data_source, is_validated)
                    VALUES (:reading_id, :meter_id, :user_id, :timestamp, :cumulative_reading,
                            :hourly_consumption_liters, :daily_consumption_liters, :monthly_consumption_liters,
                            :temperature_celsius, :quality_score, :data_source, :is_validated)
                    ON CONFLICT (meter_id, timestamp) DO NOTHING;
                """), chunk)
            print(f"      Successfully inserted/verified {len(records)} telemetry readings.")
        else:
            print(f"      WARNING: {csv_path} not found. Skipping telemetry load.")

        # 5. Seed Consumption Categories and Goals
        print("[5/5] Seeding Categories & Conservation Goals...")
        categories_data = [
            # User 1 (Single-family household baseline distribution)
            (1, 1, "bathroom", "2026-08-25", 145.0, 38.0, "fixture_audit_baseline"),
            (2, 1, "kitchen", "2026-08-25", 50.0, 13.0, "fixture_audit_baseline"),
            (3, 1, "laundry", "2026-08-25", 30.0, 8.0, "fixture_audit_baseline"),
            (4, 1, "garden", "2026-08-25", 80.0, 21.0, "seasonal_model"),
            (5, 1, "cleaning", "2026-08-25", 45.0, 12.0, "fixture_audit_baseline"),
            (6, 1, "other", "2026-08-25", 30.0, 8.0, "residual_calculation")
        ]
        for c in categories_data:
            conn.execute(text("""
                INSERT INTO consumption_categories (category_id, user_id, category_name, date, estimated_liters, 
                                                   percentage_of_daily, estimation_method)
                VALUES (:cid, :uid, :cname, :cdate, :est, :pct, :method)
                ON CONFLICT (category_id) DO NOTHING;
            """), {
                "cid": c[0], "uid": c[1], "cname": c[2], "cdate": c[3], "est": c[4], "pct": c[5], "method": c[6]
            })

        goals_data = [
            (1, 1, "percentage_reduction", 20.00, "percentage", "2026-08-01", "2026-08-31", 65.00, "active"),
            (2, 2, "weekly_target", 6500.00, "liters", "2026-08-01", "2026-08-31", 82.00, "active"),
            (3, 3, "daily_limit", 25000.00, "liters", "2026-08-01", "2026-08-31", 45.00, "active")
        ]
        for g in goals_data:
            conn.execute(text("""
                INSERT INTO goals (goal_id, user_id, goal_type, target_value, target_unit, start_date, end_date, 
                                  progress_percentage, status)
                VALUES (:gid, :uid, :gtype, :val, :unit, :sdate, :edate, :prog, :status)
                ON CONFLICT (goal_id) DO NOTHING;
            """), {
                "gid": g[0], "uid": g[1], "gtype": g[2], "val": g[3], "unit": g[4],
                "sdate": g[5], "edate": g[6], "prog": g[7], "status": g[8]
            })

        # Synchronize identity sequences in PostgreSQL so subsequent inserts do not collide
        if eng.dialect.name == "postgresql":
            tables_to_sync = [
                ("users", "user_id"),
                ("meters", "meter_id"),
                ("consumption_categories", "category_id"),
                ("goals", "goal_id")
            ]
            for tbl, col in tables_to_sync:
                conn.execute(text(f"""
                    SELECT setval(pg_get_serial_sequence('{tbl}', '{col}'), COALESCE((SELECT MAX({col}) FROM {tbl}), 1));
                """))

    print("==================================================")
    print("DATABASE SEEDING COMPLETED SUCCESSFULLY!")
    print("==================================================")
    return True

if __name__ == "__main__":
    seed_database()
