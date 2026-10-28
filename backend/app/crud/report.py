"""CRUD operations for report records."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.database import ReportRecord


def create_report(
    db: Session,
    *,
    feature: str,
    title: str,
    file_path: Optional[str] = None,
) -> ReportRecord:
    record = ReportRecord(
        feature=feature,
        title=title,
        file_path=file_path,
        created_at=datetime.now(timezone.utc),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_report(db: Session, report_id: int) -> Optional[ReportRecord]:
    return db.query(ReportRecord).filter(ReportRecord.id == report_id).first()


def list_reports(db: Session, limit: int = 50) -> list[ReportRecord]:
    return (
        db.query(ReportRecord)
        .order_by(ReportRecord.id.desc())
        .limit(limit)
        .all()
    )
