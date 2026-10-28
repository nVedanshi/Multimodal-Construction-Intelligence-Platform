from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.common import APIResponse, ErrorResponse

DECISIONS = ("GO", "NO-GO", "REVIEW REQUIRED")


class WeatherResponseData(BaseModel):
    activity: str = Field(..., description="Construction activity.")
    location: str = Field(..., description="Location.")
    planned_time: Optional[str] = Field(None, description="Planned time.")
    decision: str = Field(..., description="GO / NO-GO / REVIEW REQUIRED.", examples=DECISIONS)
    reasoning: str = Field(..., description="Reasoning for the decision.")
    hazards: List[str] = Field(default_factory=list, description="Relevant hazards.")
    precautions: List[str] = Field(default_factory=list, description="Precautions.")
    mitigation_actions: List[str] = Field(default_factory=list, description="Mitigation actions.")
    weather_source: str = Field(..., description="Source of weather information.")
    weather_timestamp: Optional[str] = Field(None, description="Timestamp of weather data.")
    data_limitations: List[str] = Field(
        default_factory=list, description="Known data limitations."
    )
    disclaimer: str = Field(
        default=(
            "AI recommendation only. Not authorization to perform dangerous work. "
            "Defer to official weather warnings, regulations, equipment limits, and site procedures."
        ),
        description="Standard weather advisory disclaimer.",
    )


class WeatherResponse(APIResponse[WeatherResponseData]):
    pass


class WeatherError(ErrorResponse):
    pass


class WeatherRequest(BaseModel):
    activity: str = Field(..., min_length=1, description="Construction activity.")
    location: str = Field(..., min_length=1, description="Location.")
    planned_time: Optional[str] = Field(None, description="Planned time.")
    weather_conditions: Optional[str] = Field(
        None, description="Manually provided weather conditions (if live data unavailable)."
    )

