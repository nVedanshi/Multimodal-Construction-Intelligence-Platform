"""CRUD operations for daily task records."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.database import DailyTaskRecord


def create_daily_tasks(
    db: Session,
    *,
    plan_date: str,
    tasks: list[dict],
) -> list[DailyTaskRecord]:
    """Persist a list of daily tasks for a given plan date."""
    records: list[DailyTaskRecord] = []
    for task in tasks:
        record = DailyTaskRecord(
            plan_date=plan_date,
            task_id=task.get("id", ""),
            title=task.get("title", ""),
            priority=task.get("priority"),
            category=task.get("category"),
            description=task.get("description"),
            completed=bool(task.get("completed", False)),
            created_at=datetime.now(timezone.utc),
        )
        db.add(record)
        records.append(record)
    db.commit()
    for record in records:
        db.refresh(record)
    return records


def get_daily_tasks(db: Session, plan_date: str) -> list[DailyTaskRecord]:
    """Return all persisted daily tasks for a given date."""
    return (
        db.query(DailyTaskRecord)
        .filter(DailyTaskRecord.plan_date == plan_date)
        .order_by(DailyTaskRecord.id.asc())
        .all()
    )


def update_daily_task_completion(
    db: Session,
    *,
    plan_date: str,
    task_id: str,
    completed: bool,
) -> Optional[DailyTaskRecord]:
    """Update the completion state of a single daily task."""
    record = (
        db.query(DailyTaskRecord)
        .filter(DailyTaskRecord.plan_date == plan_date)
        .filter(DailyTaskRecord.task_id == task_id)
        .first()
    )
    if record is None:
        return None
    record.completed = completed
    db.commit()
    db.refresh(record)
    return record
