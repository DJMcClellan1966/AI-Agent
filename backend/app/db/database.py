from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

# Create database engine (SQLite-friendly for simplified local run)
_engine_kw: dict = {"pool_pre_ping": True}
if "sqlite" in settings.DATABASE_URL:
    _engine_kw["connect_args"] = {"check_same_thread": False}
else:
    _engine_kw["pool_size"] = 10
    _engine_kw["max_overflow"] = 20

engine = create_engine(settings.DATABASE_URL, **_engine_kw)

# Create session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Session:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
