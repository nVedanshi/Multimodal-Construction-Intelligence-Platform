from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import APIResponse, ErrorResponse

PROPERTY_TYPES = ("residential", "commercial", "industrial", "land", "other")
CONDITIONS = ("excellent", "good", "average", "fair", "poor")
AREA_UNITS = ("sqft", "sqm", "sqyard", "acre", "hectare")


class ROICenario(BaseModel):
    scenario: str = Field(..., description="Scenario name (conservative / expected / optimistic).")
    annual_rental_income_inr: float = Field(..., ge=0, description="Annual rental income in INR.")
    annual_expenses_inr: float = Field(..., ge=0, description="Annual expenses in INR.")
    net_annual_income_inr: float = Field(..., ge=0, description="Net annual income in INR.")
    roi_percent: float = Field(..., description="ROI percentage.")


class ValuationResponseData(BaseModel):
    city: str = Field(..., description="City.")
    locality: str = Field(..., description="Locality / neighbourhood.")
    property_type: str = Field(..., description="Property type.", examples=PROPERTY_TYPES)
    area_sqft: float = Field(..., ge=0, description="Normalised area in square feet.")
    area_unit_input: str = Field(..., description="Original area unit supplied by user.")
    area_value_input: float = Field(..., ge=0, description="Original area value supplied by user.")
    property_age_years: Optional[float] = Field(None, ge=0, description="Property age in years.")
    condition: str = Field(..., description="Property condition.", examples=CONDITIONS)

    indicative_value_min_inr: float = Field(..., ge=0, description="Indicative minimum market value in INR.")
    indicative_value_max_inr: float = Field(..., ge=0, description="Indicative maximum market value in INR.")
    indicative_value_mid_inr: float = Field(..., ge=0, description="Indicative mid-point market value in INR.")
    estimated_price_per_sqft_inr: float = Field(..., ge=0, description="Estimated price per square foot in INR.")

    market_assumptions: List[str] = Field(
        default_factory=list, description="Assumptions about the local market."
    )
    estimated_monthly_rent_inr: Optional[float] = Field(
        None, ge=0, description="Estimated monthly rent in INR."
    )
    estimated_annual_rental_yield_percent: Optional[float] = Field(
        None, ge=0, description="Estimated annual rental yield percentage."
    )
    estimated_annual_expenses_inr: Optional[float] = Field(
        None, ge=0, description="Estimated annual expenses in INR, where calculable."
    )
    roi_scenarios: List[ROICenario] = Field(
        default_factory=list, description="ROI scenarios."
    )
    appreciation_outlook: Optional[str] = Field(
        None, description="Qualitative appreciation outlook."
    )
    data_limitations: List[str] = Field(
        default_factory=list, description="Known data limitations."
    )
    disclaimer: str = Field(
        default=(
            "Indicative AI estimate only. Not a certified valuation and not based "
            "on verified live comparable transactions unless a data source is configured."
        ),
        description="Standard valuation disclaimer.",
    )


class ValuationResponse(APIResponse[ValuationResponseData]):
    pass


class ValuationError(ErrorResponse):
    pass


class ValuationLLMResponse(BaseModel):
    """Schema for the LLM valuation narrative response (subset of fields)."""

    market_assumptions: List[str] = Field(
        default_factory=list, description="Assumptions about the local market."
    )
    appreciation_outlook: Optional[str] = Field(
        None, description="Qualitative appreciation outlook."
    )
    data_limitations: List[str] = Field(
        default_factory=list, description="Known data limitations."
    )


class ValuationRequest(BaseModel):
    city: str = Field(..., min_length=1, description="City.")
    locality: str = Field(..., min_length=1, description="Locality / neighbourhood.")
    property_type: str = Field(..., description="Property type.", examples=PROPERTY_TYPES)
    area_value: float = Field(..., ge=0, description="Land or built-up area value.")
    area_unit: str = Field("sqft", description="Area unit.", examples=AREA_UNITS)
    property_age_years: Optional[float] = Field(None, ge=0, description="Property age in years.")
    condition: str = Field("average", description="Property condition.", examples=CONDITIONS)
    amenities: Optional[str] = Field(None, description="Comma-separated amenities.")
    parking: Optional[bool] = Field(None, description="Parking available.")
    floor_number: Optional[int] = Field(None, ge=0, description="Floor number (for apartments).")
    total_floors: Optional[int] = Field(None, ge=0, description="Total floors in building.")

    @field_validator("property_type")
    @classmethod
    def _valid_type(cls, v: str) -> str:
        if v.lower() not in PROPERTY_TYPES:
            raise ValueError(f"Invalid property type. Must be one of {PROPERTY_TYPES}.")
        return v.lower()

    @field_validator("condition")
    @classmethod
    def _valid_condition(cls, v: str) -> str:
        if v.lower() not in CONDITIONS:
            raise ValueError(f"Invalid condition. Must be one of {CONDITIONS}.")
        return v.lower()

    @field_validator("area_unit")
    @classmethod
    def _valid_unit(cls, v: str) -> str:
        if v.lower() not in AREA_UNITS:
            raise ValueError(f"Invalid area unit. Must be one of {AREA_UNITS}.")
        return v.lower()
