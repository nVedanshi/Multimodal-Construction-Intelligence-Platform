from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends

from app.crud.daily_task import (
    create_daily_tasks,
    get_daily_tasks,
    update_daily_task_completion,
)
from app.database import get_db
from app.services.daily_service import plan_daily_site
from app.schemas.daily import (
    DailySiteRequest,
    DailySiteResponseData,
    DailyTaskUpdate,
)
from app.utils.responses import error_response, success_response

router = APIRouter()


@router.post("/daily-site/plan", tags=["Daily Site Assistant"])
def daily_site_plan_endpoint(
    request: DailySiteRequest,
    db=Depends(get_db),
):
    """Generate a structured daily construction site action plan.

    Accepts date, phase, activities, workforce, materials, equipment, site
    conditions, and constraints. Returns prioritized tasks, safety checks,
    risks, and follow-up actions. Persisted tasks survive page refreshes.
    """
    try:
        result = plan_daily_site(request=request)
    except Exception as exc:
        return error_response(
            code="daily_plan_failed",
            message="Daily site planning failed: %s" % exc,
            status_code=500,
            feature="daily_site_assistant",
            mode="fallback",
        )

    if result.get("error"):
        return error_response(
            code=result["error"].get("code", "daily_plan_failed"),
            message=result["error"].get("message", "Daily site planning unavailable."),
            status_code=502,
            feature="daily_site_assistant",
            mode=result.get("mode", "fallback"),
            model=result.get("model"),
        )

    data = result["result"]
    if not isinstance(data, DailySiteResponseData):
        return error_response(
            code="invalid_response",
            message="Daily site plan returned an invalid response.",
            status_code=500,
            feature="daily_site_assistant",
            mode="fallback",
        )

    # Persist generated tasks so completion state survives refreshes.
    try:
        task_dicts = [t.model_dump() if hasattr(t, "model_dump") else dict(t) for t in data.prioritized_tasks]
        create_daily_tasks(db, plan_date=request.date, tasks=task_dicts)
    except Exception:
        # Persistence failures must not block the plan response.
        pass

    return success_response(
        data=data.model_dump(),
        feature="daily_site_assistant",
        mode=result.get("mode", "demo"),
        model=result.get("model"),
    )


@router.get("/daily-site/tasks", tags=["Daily Site Assistant"])
def get_daily_site_tasks(
    plan_date: str,
    db=Depends(get_db),
):
    """Retrieve persisted daily tasks for a given plan date."""
    try:
        records = get_daily_tasks(db, plan_date=plan_date)
    except Exception as exc:
        return error_response(
            code="task_fetch_failed",
            message="Failed to retrieve daily tasks: %s" % exc,
            status_code=500,
            feature="daily_site_assistant",
            mode="fallback",
        )
    return success_response(
        data=[r.to_dict() for r in records],
        feature="daily_site_assistant",
        mode="demo",
    )


@router.patch("/daily-site/tasks/{task_id}/complete", tags=["Daily Site Assistant"])
def patch_daily_task_complete(
    task_id: str,
    update: DailyTaskUpdate,
    plan_date: Optional[str] = None,
    db=Depends(get_db),
):
    """Update the completion state of a single daily task."""
    if not plan_date:
        return error_response(
            code="missing_date",
            message="plan_date query parameter is required.",
            status_code=400,
            feature="daily_site_assistant",
            mode="fallback",
        )
    try:
        record = update_daily_task_completion(
            db, plan_date=plan_date, task_id=task_id, completed=update.completed
        )
    except Exception as exc:
        return error_response(
            code="task_update_failed",
            message="Failed to update task: %s" % exc,
            status_code=500,
            feature="daily_site_assistant",
            mode="fallback",
        )
    if record is None:
        return error_response(
            code="task_not_found",
            message="Task not found for date %s and task id %s." % (plan_date, task_id),
            status_code=404,
            feature="daily_site_assistant",
            mode="fallback",
        )
    return success_response(
        data=record.to_dict(),
        feature="daily_site_assistant",
        mode="demo",
    )
