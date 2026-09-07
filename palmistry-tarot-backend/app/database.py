"""
Database setup.

We're using SQLite here (a single local file, palmistry_tarot.db) instead of
the doc's PostgreSQL — same SQL concepts, zero setup required. When you're
ready for production, changing DATABASE_URL to a postgres:// connection
string is usually the only line that needs to change, because SQLAlchemy
abstracts the differences between databases.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./palmistry_tarot.db")

# check_same_thread=False is an SQLite-specific quirk: by default it only
# allows the thread that created the connection to use it, but FastAPI
# handles requests on different threads.
engine_kwargs = {"connect_args": {"check_same_thread": False}} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class every database model (like User) inherits from.
# SQLAlchemy uses it to know which Python classes map to which SQL tables.
Base = declarative_base()


def get_db():
    """
    A FastAPI dependency: creates one database session per request, and
    guarantees it's closed afterward even if the request raises an error.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
