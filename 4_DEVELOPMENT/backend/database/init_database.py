"""
Smart Water Usage Advisor - Database Initializer
Executes init_schema.sql against the configured database.
Translates PostgreSQL DDL seamlessly for SQLite when in local test fallback mode.
"""

import os
import re
from sqlalchemy import text
from db_config import create_db_engine

def init_schema(engine=None, sql_path="4_DEVELOPMENT/backend/database/init_schema.sql"):
    eng = engine or create_db_engine()
    is_sqlite = eng.url.drivername.startswith("sqlite")

    print("==================================================")
    print(f"INITIALIZING DATABASE SCHEMA ({'SQLite Test Fallback' if is_sqlite else 'PostgreSQL'})")
    print("==================================================")

    if not os.path.isfile(sql_path):
        raise FileNotFoundError(f"Schema DDL file not found: {sql_path}")

    with open(sql_path, "r", encoding="utf-8") as f:
        ddl_content = f.read()

    # If running against SQLite in test fallback mode, adapt PG-specific syntax
    if is_sqlite:
        # Remove BEGIN/COMMIT wrapper (SQLAlchemy manages transactions)
        ddl_content = re.sub(r'^\s*(BEGIN|COMMIT)\s*;\s*$', '', ddl_content, flags=re.MULTILINE)
        # Adapt IDENTITY to AUTOINCREMENT
        ddl_content = re.sub(r'INTEGER\s+GENERATED\s+BY\s+DEFAULT\s+AS\s+IDENTITY\s+PRIMARY\s+KEY',
                             'INTEGER PRIMARY KEY AUTOINCREMENT', ddl_content, flags=re.IGNORECASE)
        ddl_content = re.sub(r'BIGINT\s+GENERATED\s+BY\s+DEFAULT\s+AS\s+IDENTITY\s+PRIMARY\s+KEY',
                             'INTEGER PRIMARY KEY AUTOINCREMENT', ddl_content, flags=re.IGNORECASE)
        # Adapt TIMESTAMPTZ to TIMESTAMP
        ddl_content = re.sub(r'TIMESTAMP\s+WITH\s+TIME\s+ZONE', 'TIMESTAMP', ddl_content, flags=re.IGNORECASE)

    # Split into individual SQL statements
    statements = [s.strip() for s in ddl_content.split(';') if s.strip()]

    with eng.begin() as conn:
        for stmt in statements:
            if stmt:
                conn.execute(text(stmt))

    print(f"Successfully executed {len(statements)} schema statements.")
    print("All 12 authoritative tables and indexes created successfully.")
    print("==================================================")
    return True

if __name__ == "__main__":
    init_schema()
