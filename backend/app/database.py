"""
Database access layer using SQLite via SQLAlchemy.

Provides session management, the declarative base, and CRUD helpers for
persisting project records, analysis history, and generated reports.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Optional

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from app.config import get_settings

settings = get_settings()

# Normalise sqlite URL for SQLAlchemy compatibility.
database_url = settings.DATABASE_URL
if database_url.startswith("sqlite:///"):
    database_url = database_url.replace("sqlite:///", "sqlite:///", 1)

engine: Engine = create_engine(
    database_url,
    connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {},
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Iterator[Session]:
    """FastAPI dependency that yields a SQLAlchemy session and closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope() -> Iterator[Session]:
    """Context manager for a transactional SQLAlchemy session outside FastAPI."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """Create all tables defined on the declarative base."""
    # Import models here to ensure they are registered on Base.metadata.
    from app import models  # noqa: F401  (registers models)
    Base.metadata.create_all(bind=engine)


# --------------------------------------------------------------------------- #
# ORM models
# --------------------------------------------------------------------------- #

class ProjectRecord(Base):
    """Persisted construction project record."""

    __tablename__ = "project_records"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=True)
    construction_type = Column(String(100), nullable=True)
    intended_use = Column(String(100), nullable=True)
    num_floors = Column(Integer, nullable=True)
    plot_area = Column(Float, nullable=True)
    built_up_area = Column(Float, nullable=True)
    created_at = Column(DateTime, default=None, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "project_name": self.project_name,
            "location": self.location,
            "construction_type": self.construction_type,
            "intended_use": self.intended_use,
            "num_floors": self.num_floors,
            "plot_area": self.plot_area,
            "built_up_area": self.built_up_area,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AnalysisRecord(Base):
    """Persisted analysis history (safety, crack, valuation, daily, weather)."""

    __tablename__ = "analysis_records"

    id = Column(Integer, primary_key=True, index=True)
    feature = Column(String(50), nullable=False, index=True)
    mode = Column(String(20), nullable=False)  # real_ai | demo | fallback
    request_summary = Column(Text, nullable=True)
    result_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=None, nullable=True)

    def to_dict(self) -> dict:
        import json

        return {
            "id": self.id,
            "feature": self.feature,
            "mode": self.mode,
            "request_summary": self.request_summary,
            "result": json.loads(self.result_json) if self.result_json else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ReportRecord(Base):
    """Persisted generated reports."""

    __tablename__ = "report_records"

    id = Column(Integer, primary_key=True, index=True)
    feature = Column(String(50), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=None, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "feature": self.feature,
            "title": self.title,
            "file_path": self.file_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DailyTaskRecord(Base):
    """Persisted daily site task completion state."""

    __tablename__ = "daily_task_records"

    id = Column(Integer, primary_key=True, index=True)
    plan_date = Column(String(50), nullable=False, index=True)
    task_id = Column(String(100), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    priority = Column(String(50), nullable=True)
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=None, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "plan_date": self.plan_date,
            "task_id": self.task_id,
            "title": self.title,
            "priority": self.priority,
            "category": self.category,
            "description": self.description,
            "completed": self.completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
