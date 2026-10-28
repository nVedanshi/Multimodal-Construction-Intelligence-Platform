from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import APIResponse, ErrorResponse

CONSTRUCTION_TYPES = ("residential", "commercial", "industrial", "mixed_use", "other")
INTENDED_USES = (
    "house",
    "apartment",
    "office",
    "shop",
    "warehouse",
    "factory",
    "school",
    "hospital",
    "other",
)
QUALITY_LEVELS = ("standard", "medium", "premium")


class MaterialRequirement(BaseModel):
    material: str = Field(..., description="Material name (cement, sand, aggregate, steel, ...).")
    quantity: float = Field(..., description="Required quantity.", ge=0)
    unit: str = Field(..., description="Unit of measure (bags, cubic metres, kg, tonnes, ...).")
    estimated_cost_inr: Optional[float] = Field(
        None, description="Estimated cost in Indian Rupees.", ge=0
    )


class CostCategory(BaseModel):
    category: str = Field(..., description="Cost category (materials, labour, equipment, ...).")
    estimated_cost_inr: float = Field(..., description="Estimated cost in INR.", ge=0)
    notes: Optional[str] = Field(None, description="Assumptions or notes.")


class SchedulePhase(BaseModel):
    phase: str = Field(..., description="Construction phase name.")
    week: Optional[int] = Field(None, description="Approximate week number.", ge=1)
    activities: List[str] = Field(default_factory=list, description="Key activities in this phase.")
    duration_weeks: Optional[float] = Field(None, description="Duration in weeks.", ge=0)


class Milestone(BaseModel):
    name: str = Field(..., description="Milestone name.")
    target_week: Optional[int] = Field(None, description="Target week.", ge=1)
    description: Optional[str] = None


class ProjectPlanningResponseData(BaseModel):
    project_name: str = Field(..., description="Project name.")
    location: Optional[str] = Field(None, description="Project location.")
    construction_type: str = Field(..., description="Construction type.")
    intended_use: str = Field(..., description="Intended use.")
    num_floors: int = Field(..., description="Number of floors.", ge=1)
    plot_area_sqm: Optional[float] = Field(None, description="Plot area in square metres.", ge=0)
    built_up_area_sqm: Optional[float] = Field(
        None, description="Built-up area in square metres.", ge=0
    )
    quality_level: str = Field(..., description="Quality preference (standard/medium/premium).")

    material_requirements: List[MaterialRequirement] = Field(
        default_factory=list, description="Approximate material requirements."
    )
    total_material_cost_inr: float = Field(
        0.0, description="Total estimated material cost in INR.", ge=0
    )
    cost_categories: List[CostCategory] = Field(
        default_factory=list, description="Category-wise cost estimate in INR."
    )
    total_estimated_cost_inr: float = Field(
        0.0, description="Total estimated project cost in INR.", ge=0
    )
    labour_cost_inr: float = Field(
        0.0, description="Estimated labour cost in INR.", ge=0
    )
    contingency_inr: float = Field(
        0.0, description="Contingency allowance in INR.", ge=0
    )
    cost_assumptions: List[str] = Field(
        default_factory=list, description="Labour and material cost assumptions."
    )
    schedule_phases: List[SchedulePhase] = Field(
        default_factory=list, description="Phase-wise / week-wise construction schedule."
    )
    milestones: List[Milestone] = Field(
        default_factory=list, description="Important milestones."
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Practical planning recommendations."
    )
    visualization: Optional[dict] = Field(
        None, description="Conceptual layout / visualization data."
    )
    disclaimer: str = Field(
        default=(
            "Indicative planning estimate based on standard thumb rules. Not an "
            "engineering calculation, contractor quotation, or binding cost estimate."
        ),
        description="Standard planning disclaimer.",
    )


class ProjectPlanningResponse(APIResponse[ProjectPlanningResponseData]):
    pass


class ProjectPlanningError(ErrorResponse):
    pass


class PlanningLLMResponse(BaseModel):
    """Schema for the LLM planning narrative response (subset of fields)."""

    recommendations: List[str] = Field(
        default_factory=list, description="Practical planning recommendations."
    )
    assumptions: List[str] = Field(
        default_factory=list, description="Labour and material cost assumptions."
    )


class ProjectPlanningRequest(BaseModel):
    project_name: str = Field(..., min_length=1, description="Project name.")
    location: Optional[str] = Field(None, description="Project location.")
    construction_type: str = Field(..., description="Construction type.", examples=CONSTRUCTION_TYPES)
    intended_use: str = Field(..., description="Intended use.", examples=INTENDED_USES)
    num_floors: int = Field(1, ge=1, le=50, description="Number of floors.")
    plot_area: Optional[float] = Field(None, ge=0, description="Plot area (numeric).")
    plot_area_unit: str = Field("sqm", description="Unit of plot area (sqm/sqft/acre).")
    built_up_area: Optional[float] = Field(None, ge=0, description="Approximate built-up area (numeric).")
    built_up_area_unit: str = Field("sqm", description="Unit of built-up area (sqm/sqft).")
    quality_level: str = Field("medium", description="Quality preference.", examples=QUALITY_LEVELS)

    @field_validator("construction_type")
    @classmethod
    def _valid_construction_type(cls, v: str) -> str:
        if v.lower() not in CONSTRUCTION_TYPES:
            raise ValueError(f"Invalid construction type. Must be one of {CONSTRUCTION_TYPES}.")
        return v.lower()

    @field_validator("intended_use")
    @classmethod
    def _valid_intended_use(cls, v: str) -> str:
        if v.lower() not in INTENDED_USES:
            raise ValueError(f"Invalid intended use. Must be one of {INTENDED_USES}.")
        return v.lower()

    @field_validator("quality_level")
    @classmethod
    def _valid_quality(cls, v: str) -> str:
        if v.lower() not in QUALITY_LEVELS:
            raise ValueError(f"Invalid quality level. Must be one of {QUALITY_LEVELS}.")
        return v.lower()

    @field_validator("plot_area_unit", "built_up_area_unit")
    @classmethod
    def _valid_area_unit(cls, v: str) -> str:
        if v.lower() not in ("sqm", "sqft", "acre"):
            raise ValueError("Area unit must be sqm, sqft, or acre.")
        return v.lower()
