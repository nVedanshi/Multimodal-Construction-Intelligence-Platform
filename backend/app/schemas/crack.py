"""
Schemas for Structural Crack Detection and Analysis (Activity 2.2).

Image upload with optional structural context. Returns a structured crack
analysis report that explicitly avoids claiming structural diagnoses or
measurements unless a reliable reference scale is available.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import APIResponse, ErrorResponse

CRACK_PATTERN_CATEGORIES = (
    "hairline",
    "vertical",
    "diagonal",
    "map_cracking",
    "structural",
    "other",
)

SEVERITY_LEVELS = ("low", "moderate", "high", "severe")


class CrackCharacteristic(BaseModel):
    """An observable crack characteristic."""

    characteristic: str = Field(..., description="Name of the characteristic.")
    description: str = Field(..., description="Description of what is observed.")
    confidence: str = Field(
        ...,
        description="Confidence level (high/medium/low).",
        examples=["high", "medium", "low"],
    )


class CrackAnalysisResponseData(BaseModel):
    """Structured crack analysis report."""

    image_id: Optional[str] = Field(
        None, description="Stored identifier for the analysed image."
    )
    crack_classification: str = Field(
        ...,
        description="Apparent crack pattern category.",
        examples=CRACK_PATTERN_CATEGORIES,
    )
    observable_characteristics: List[CrackCharacteristic] = Field(
        default_factory=list, description="Observable crack characteristics."
    )
    continuity: Optional[str] = Field(
        None, description="Observed continuity (continuous / segmented / branching)."
    )
    apparent_orientation: Optional[str] = Field(
        None, description="Apparent orientation (horizontal / vertical / diagonal)."
    )
    preliminary_severity: str = Field(
        ...,
        description="Preliminary severity (low/moderate/high/severe).",
        examples=SEVERITY_LEVELS,
    )
    possible_causes: List[str] = Field(
        default_factory=list, description="Possible causes (not a confirmed diagnosis)."
    )
    uncertainty: str = Field(
        ...,
        description="Statement of uncertainty and limitations of image-only analysis.",
    )
    potential_risks: List[str] = Field(
        default_factory=list, description="Potential risks if left unaddressed."
    )
    recommended_next_steps: List[str] = Field(
        default_factory=list, description="Recommended next steps."
    )
    maintenance_suggestions: List[str] = Field(
        default_factory=list, description="Suggested maintenance actions."
    )
    needs_professional_inspection: bool = Field(
        True,
        description="Whether a qualified structural professional should assess.",
    )
    disclaimer: str = Field(
        default=(
            "Image-only preliminary assessment. Cannot establish structural safety, "
            "actual crack cause, or physical measurements. Consult a qualified "
            "structural engineer for load-bearing or severe cracks."
        ),
        description="Standard crack-analysis disclaimer.",
    )


class CrackAnalysisResponse(APIResponse[CrackAnalysisResponseData]):
    """Concrete crack analysis response envelope."""


class CrackAnalysisError(ErrorResponse):
    """Concrete crack analysis error envelope."""


class CrackRequestContext(BaseModel):
    """Optional structural context accompanying a crack image."""

    surface_type: Optional[str] = Field(
        None, description="Surface type (wall, concrete, column, beam, slab, other)."
    )
    element_type: Optional[str] = Field(
        None, description="Structural element type (load-bearing / non-load-bearing / unknown)."
    )
    age_years: Optional[float] = Field(
        None, description="Approximate age of the structure in years.", ge=0
    )
    noted_concerns: Optional[str] = Field(
        None, description="User-noted concerns about the crack."
    )

    @field_validator("age_years")
    @classmethod
    def _round_age(cls, v: Optional[float]) -> Optional[float]:
        return round(v, 1) if v is not None else None
