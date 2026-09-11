"""
Smart Water Usage Advisor - Database Configuration Module
Provides SQLAlchemy engine and session management.
Grounds credentials strictly in environment variables (.env).
Provides secure fallback for isolated testing when configured.
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

Base = declarative_base()

def get_database_url() -> str:
    """
    Retrieves and validates the database connection string from environment variables.
    Fails safely with an explicit error message if unconfigured.
    """
    db_url = os.getenv("DATABASE_URL")
    
    # Check if testing fallback is requested
    use_sqlite_fallback = os.getenv("USE_SQLITE_TEST_FALLBACK", "False").lower() in ("true", "1")
    if use_sqlite_fallback and not db_url:
        sqlite_path = os.getenv("SQLITE_DB_PATH", "smart_water_advisor_test.db")
        return f"sqlite:///{sqlite_path}"

    if not db_url:
        # Check individual Postgres parameters
        pg_user = os.getenv("POSTGRES_USER")
        pg_pass = os.getenv("POSTGRES_PASSWORD")
        pg_host = os.getenv("POSTGRES_HOST", "localhost")
        pg_port = os.getenv("POSTGRES_PORT", "5432")
        pg_db = os.getenv("POSTGRES_DB", "smart_water_advisor_db")

        if pg_user and pg_pass and pg_db:
            return f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
        
        raise EnvironmentError(
            "CONFIGURATION ERROR: Missing DATABASE_URL environment variable.\n"
            "Please configure PostgreSQL credentials in your local .env file using .env.example as a template,\n"
            "or set USE_SQLITE_TEST_FALLBACK=True for isolated local unit testing."
        )

    return db_url

def create_db_engine(db_url: str = None, echo: bool = False):
    """
    Creates and returns a SQLAlchemy Engine instance.
    """
    url = db_url or get_database_url()
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    engine = create_engine(url, echo=echo, connect_args=connect_args)
    return engine

def get_session_factory(engine=None):
    """
    Returns a configured sessionmaker bound to the engine.
    """
    eng = engine or create_db_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=eng)
