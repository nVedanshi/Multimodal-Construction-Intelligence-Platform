"""CRUD operations for project records."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.database import ProjectRecord


def create_project(
    db: Session,
    *,
    project_name: str,
    location: Optional[str] = None,
    construction_type: Optional[str] = None,
    intended_use: Optional[str] = None,
    num_floors: Optional[int] = None,
    plot_area: Optional[float] = None,
    built_up_area: Optional[float] = None,
) -> ProjectRecord:
    record = ProjectRecord(
        project_name=project_name,
        location=location,
        construction_type=construction_type,
        intended_use=intended_use,
        num_floors=num_floors,
        plot_area=plot_area,
        built_up_area=built_up_area,
        created_at=datetime.now(timezone.utc),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_project(db: Session, project_id: int) -> Optional[ProjectRecord]:
    return db.query(ProjectRecord).filter(ProjectRecord.id == project_id).first()


def list_projects(db: Session, limit: int = 50) -> list[ProjectRecord]:
    return (
        db.query(ProjectRecord)
        .order_by(ProjectRecord.id.desc())
        .limit(limit)
        .all()
    )
