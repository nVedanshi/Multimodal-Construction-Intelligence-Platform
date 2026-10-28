"""CRUD operations for analysis history records."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.database import AnalysisRecord


def create_analysis(
    db: Session,
    *,
    feature: str,
    mode: str,
    request_summary: Optional[str] = None,
    result_json: Optional[str] = None,
) -> AnalysisRecord:
    record = AnalysisRecord(
        feature=feature,
        mode=mode,
        request_summary=request_summary,
        result_json=result_json,
        created_at=datetime.now(timezone.utc),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_analysis(db: Session, analysis_id: int) -> Optional[AnalysisRecord]:
    return db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()


def list_analyses(
    db: Session, feature: Optional[str] = None, limit: int = 50
) -> list[AnalysisRecord]:
    query = db.query(AnalysisRecord).order_by(AnalysisRecord.id.desc())
    if feature:
        query = query.filter(AnalysisRecord.feature == feature)
    return query.limit(limit).all()
