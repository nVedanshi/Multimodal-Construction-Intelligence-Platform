from __future__ import annotations

from fastapi import APIRouter

from app.services.planning_service import plan_project
from app.schemas.planning import (
    ProjectPlanningRequest,
    ProjectPlanningResponseData,
)
from app.utils.responses import error_response, success_response

router = APIRouter()


@router.post("/planning/project", tags=["Construction Project Planning"])
def plan_project_endpoint(request: ProjectPlanningRequest):
    """Generate a consolidated construction project plan.

    Accepts structured project parameters and returns material requirements,
    category-wise cost estimate in INR, schedule, milestones, and a conceptual
    visualization. All numerical values are backend-computed using documented
    thumb rules.
    """
    try:
        result = plan_project(request=request)
    except Exception as exc:
        return error_response(
            code="planning_failed",
            message="Project planning failed: %s" % exc,
            status_code=500,
            feature="construction_project_planning",
            mode="fallback",
        )

    if result.get("error"):
        return error_response(
            code=result["error"].get("code", "planning_failed"),
            message=result["error"].get("message", "Project planning unavailable."),
            status_code=502,
            feature="construction_project_planning",
            mode=result.get("mode", "fallback"),
            model=result.get("model"),
        )

    data = result["result"]
    if not isinstance(data, ProjectPlanningResponseData):
        return error_response(
            code="invalid_response",
            message="Project planning returned an invalid response.",
            status_code=500,
            feature="construction_project_planning",
            mode="fallback",
        )

    return success_response(
        data=data.model_dump(),
        feature="construction_project_planning",
        mode=result.get("mode", "demo"),
        model=result.get("model"),
    )
