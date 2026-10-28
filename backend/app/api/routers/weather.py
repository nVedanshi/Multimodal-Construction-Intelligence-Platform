from __future__ import annotations

from fastapi import APIRouter

from app.services.weather_service import weather_advisory
from app.schemas.weather import WeatherRequest, WeatherResponseData
from app.utils.responses import error_response, success_response

router = APIRouter()


@router.post("/weather/advisory", tags=["Weather-Aware Advisory"])
def weather_advisory_endpoint(request: WeatherRequest):
    """Generate a weather-aware construction advisory.

    Accepts activity, location, planned time, and optional manual weather
    conditions. Returns a GO / NO-GO / REVIEW REQUIRED decision with reasoning,
    hazards, precautions, and data limitations.
    """
    try:
        result = weather_advisory(request=request)
    except Exception as exc:
        return error_response(
            code="weather_failed",
            message="Weather advisory failed: %s" % exc,
            status_code=500,
            feature="weather_aware_advisory",
            mode="fallback",
        )

    if result.get("error"):
        return error_response(
            code=result["error"].get("code", "weather_failed"),
            message=result["error"].get("message", "Weather advisory unavailable."),
            status_code=502,
            feature="weather_aware_advisory",
            mode=result.get("mode", "fallback"),
            model=result.get("model"),
        )

    data = result["result"]
    if not isinstance(data, WeatherResponseData):
        return error_response(
            code="invalid_response",
            message="Weather advisory returned an invalid response.",
            status_code=500,
            feature="weather_aware_advisory",
            mode="fallback",
        )

    return success_response(
        data=data.model_dump(),
        feature="weather_aware_advisory",
        mode=result.get("mode", "demo"),
        model=result.get("model"),
    )
