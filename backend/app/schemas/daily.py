from __future__ import annotations

from typing import List, Optional, Union

from pydantic import BaseModel, Field

from app.schemas.common import APIResponse, ErrorResponse


class DailyTask(BaseModel):
    id: str = Field(..., description="Stable task identifier.")
    title: str = Field(..., description="Task title.")
    priority: str = Field(..., description="Priority (high / medium / low).")
    category: Optional[str] = Field(None, description="Task category.")
    description: str = Field(..., description="Task description.")
    workforce_required: Optional[str] = Field(None, description="Workforce requirement.")
    equipment_required: Optional[str] = Field(None, description="Equipment requirement.")
    materials: Optional[str] = Field(None, description="Material preparation needed.")
    safety_checks: Optional[str] = Field(None, description="Safety checks for this task.")
    risks: Optional[str] = Field(None, description="Possible risks.")
    completed: bool = Field(False, description="Whether the task is marked completed.")


class DailySiteResponseData(BaseModel):
    date: str = Field(..., description="Planned date.")
    project_phase: str = Field(..., description="Current project phase.")
    prioritized_tasks: List[DailyTask] = Field(
        default_factory=list, description="Prioritized daily tasks."
    )
    workforce_requirements: Optional[str] = Field(
        None, description="Overall workforce requirements."
    )
    equipment_requirements: Optional[str] = Field(
        None, description="Overall equipment requirements."
    )
    material_preparation: Optional[str] = Field(
        None, description="Material preparation summary."
    )
    safety_checks: List[str] = Field(
        default_factory=list, description="Site safety checks."
    )
    possible_risks: List[str] = Field(
        default_factory=list, description="Possible site risks."
    )
    coordination_notes: Optional[str] = Field(
        None, description="Coordination notes."
    )
    recommended_follow_up: List[str] = Field(
        default_factory=list, description="Recommended follow-up actions."
    )
    assumptions: List[str] = Field(
        default_factory=list, description="Disclosed assumptions."
    )
    disclaimer: str = Field(
        default=(
            "AI-generated daily plan. Does not replace a site engineer's professional "
            "judgment or site-specific safety procedures."
        ),
        description="Standard daily-assistant disclaimer.",
    )


class DailySiteResponse(APIResponse[DailySiteResponseData]):
    pass


class DailySiteError(ErrorResponse):
    pass


class DailyLLMResponse(BaseModel):
    """Schema for the LLM daily plan narrative response (subset of fields)."""

    prioritized_tasks: List[dict] = Field(
        default_factory=list, description="Prioritized daily tasks."
    )
    workforce_requirements: Optional[str] = Field(
        None, description="Overall workforce requirements."
    )
    equipment_requirements: Optional[str] = Field(
        None, description="Overall equipment requirements."
    )
    material_preparation: Optional[str] = Field(
        None, description="Material preparation summary."
    )
    safety_checks: List[str] = Field(
        default_factory=list, description="Site safety checks."
    )
    possible_risks: List[str] = Field(
        default_factory=list, description="Possible site risks."
    )
    coordination_notes: Optional[str] = Field(
        None, description="Coordination notes."
    )
    recommended_follow_up: List[str] = Field(
        default_factory=list, description="Recommended follow-up actions."
    )
    assumptions: List[str] = Field(
        default_factory=list, description="Disclosed assumptions."
    )


class DailyTaskLLM(BaseModel):
    """Schema for a single LLM-generated daily task (all fields optional)."""

    id: Optional[str] = Field(None, description="Stable task identifier.")
    title: Optional[str] = Field(None, description="Task title.")
    priority: Optional[str] = Field(None, description="Priority (high / medium / low).")
    category: Optional[str] = Field(None, description="Task category.")
    description: Optional[str] = Field(None, description="Task description.")
    workforce_required: Optional[Union[str, List[str]]] = Field(
        None, description="Workforce requirement."
    )
    equipment_required: Optional[Union[str, List[str]]] = Field(
        None, description="Equipment requirement."
    )
    materials: Optional[Union[str, List[str]]] = Field(
        None, description="Material preparation needed."
    )
    safety_checks: Optional[Union[str, List[str]]] = Field(
        None, description="Safety checks for this task."
    )
    risks: Optional[Union[str, List[str]]] = Field(
        None, description="Possible risks."
    )
    completed: Optional[bool] = Field(
        None, description="Whether the task is marked completed."
    )


class DailySiteRequest(BaseModel):
    date: str = Field(..., description="Planned date (ISO format).")
    project_phase: str = Field(..., description="Current project phase.")
    planned_activities: Optional[str] = Field(None, description="Planned activities.")
    workforce_availability: Optional[str] = Field(None, description="Workforce availability.")
    materials: Optional[str] = Field(None, description="Available materials.")
    equipment: Optional[str] = Field(None, description="Available equipment.")
    site_conditions: Optional[str] = Field(None, description="Site conditions.")
    constraints: Optional[str] = Field(None, description="User-provided constraints.")


class DailyTaskUpdate(BaseModel):
    """Request to update a single daily task's completion state."""

    task_id: str = Field(..., description="Stable task identifier.")
    completed: bool = Field(..., description="Whether the task is marked completed.")
