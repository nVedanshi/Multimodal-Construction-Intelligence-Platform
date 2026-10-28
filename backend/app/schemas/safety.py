"""
Schemas for Construction Site Safety Monitoring (Activity 2.1).

Multipart request: image + optional text observation log + optional safety doc.
Response: validated JSON safety report.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import APIResponse, ErrorResponse, ResponseMeta

RISK_LEVELS = ("low", "medium", "high", "critical")


class SafetyHazard(BaseModel):
    """A single identified safety hazard."""

    hazard: str = Field(..., description="Name of the hazard.")
    category: str = Field(
        ...,
        description="Hazard category (e.g. PPE, fall protection, housekeeping, electrical).",
    )
    severity: str = Field(
        ...,
        description="Severity of this specific hazard (low/medium/high/critical).",
        examples=["low", "medium", "high", "critical"],
    )
    observable: bool = Field(
        True,
        description="True if directly observable in the image; False if inferred/uncertain.",
    )
    observation: str = Field(
        ..., description="Supporting visual observation or basis for the inference."
    )


class SafetyAnalysisResponseData(BaseModel):
    """Structured safety analysis report."""

    summary: str = Field(..., description="Plain-language summary of the assessment.")
    overall_risk_level: str = Field(
        ...,
        description="Overall site risk level.",
        examples=["low", "medium", "high", "critical"],
    )
    identified_hazards: List[SafetyHazard] = Field(
        default_factory=list, description="List of identified hazards."
    )
    severity: str = Field(
        ...,
        description="Overall severity rating (low/medium/high/critical).",
        examples=["low", "medium", "high", "critical"],
    )
    supporting_visual_observations: List[str] = Field(
        default_factory=list,
        description="Directly observable conditions from the image.",
    )
    recommended_ppe: List[str] = Field(
        default_factory=list, description="Recommended personal protective equipment."
    )
    corrective_actions: List[str] = Field(
        default_factory=list, description="Immediate corrective actions."
    )
    preventive_guidelines: List[str] = Field(
        default_factory=list, description="Ongoing preventive guidelines."
    )
    uncertainty_notes: Optional[str] = Field(
        None, description="Conditions that are unclear or could not be assessed."
    )
    disclaimer: str = Field(
        default=(
            "AI-assisted preliminary assessment only. Not a certified safety "
            "inspection and not a substitute for a qualified safety professional."
        ),
        description="Standard safety disclaimer.",
    )


class SafetyAnalysisResponse(APIResponse[SafetyAnalysisResponseData]):
    """Concrete safety analysis response envelope."""


class SafetyAnalysisError(ErrorResponse):
    """Concrete safety analysis error envelope."""


# --------------------------------------------------------------------------- #
# Validation helpers (used by endpoints)
# --------------------------------------------------------------------------- #

def validate_risk_level(value: str) -> str:
    if value.lower() not in RISK_LEVELS:
        raise ValueError(f"Invalid risk level: {value}. Must be one of {RISK_LEVELS}.")
    return value.lower()


class SafetyRequestForm(BaseModel):
    """Validated textual fields for the safety multipart endpoint."""

    observation_log: Optional[str] = Field(
        None, description="Optional description of the scene."
    )
    site_photo_present: bool = Field(
        False, description="Whether an image file was included."
    )
    safety_doc_present: bool = Field(
        False, description="Whether a safety document file was included."
    )

    @field_validator("observation_log")
    @classmethod
    def _trim_log(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if v else None
