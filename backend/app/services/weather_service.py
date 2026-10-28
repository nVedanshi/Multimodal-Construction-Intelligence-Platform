from __future__ import annotations

from typing import Optional

try:
    import httpx  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    httpx = None

from app.config import get_settings
from app.services.ai_service import call_llm, invoke_with_schema, request_metadata
from app.schemas.weather import (
    WeatherRequest,
    WeatherResponseData,
    DECISIONS,
)

FEATURE = "weather_aware_advisory"

DECISION_GO = "GO"
DECISION_NO_GO = "NO-GO"
DECISION_REVIEW = "REVIEW REQUIRED"

HIGH_RISK_ACTIVITIES = {
    "concrete pouring",
    "concreting",
    "lifting",
    "crane",
    "elevated",
    "work at height",
    "scaffolding",
}


def _demo_result(request: WeatherRequest) -> WeatherResponseData:
    return WeatherResponseData(
        activity=request.activity,
        location=request.location,
        planned_time=request.planned_time,
        decision=DECISION_REVIEW,
        reasoning=(
            "Demo mode: no live weather data was retrieved. Decision is "
            "illustrative only."
        ),
        hazards=["Demo: weather conditions not assessed."],
        precautions=["Obtain current weather before proceeding."],
        mitigation_actions=["Delay until weather is confirmed suitable."],
        weather_source="Demo mode (simulated)",
        weather_timestamp=None,
        data_limitations=["Demo response. No real weather data used."],
    )


def _fallback_result(request: WeatherRequest, limitation: str) -> WeatherResponseData:
    return WeatherResponseData(
        activity=request.activity,
        location=request.location,
        planned_time=request.planned_time,
        decision=DECISION_REVIEW,
        reasoning="Weather advisory unavailable: %s. Manual weather input recommended." % limitation,
        hazards=["Weather data unavailable."],
        precautions=["Check official weather warnings before work."],
        mitigation_actions=["Postpone weather-sensitive work until conditions are known."],
        weather_source="Unavailable",
        weather_timestamp=None,
        data_limitations=["Live weather service unavailable: %s" % limitation],
    )


def _fetch_weather(location: str) -> Optional[dict]:
    settings = get_settings()
    if httpx is None or not settings.WEATHER_ENABLED or not settings.WEATHER_API_KEY:
        return None
    try:
        with httpx.Client(timeout=settings.WEATHER_REQUEST_TIMEOUT_SECONDS) as client:
            response = client.get(
                settings.WEATHER_BASE_URL,
                params={"q": location, "appid": settings.WEATHER_API_KEY, "units": "metric"},
            )
            if response.status_code != 200:
                return None
            data = response.json()
            return {
                "source": "OpenWeatherMap",
                "temperature_c": data.get("main", {}).get("temp"),
                "condition": (data.get("weather") or [{}])[0].get("description"),
                "wind_speed_mps": data.get("wind", {}).get("speed"),
                "humidity": data.get("main", {}).get("humidity"),
                "rain_mm_1h": data.get("rain", {}).get("1h"),
                "timestamp": data.get("dt"),
            }
    except Exception:
        return None


def _assess(activity: str, weather: Optional[dict], manual_conditions: Optional[str]) -> dict:
    activity_l = (activity or "").lower()
    is_high_risk = any(k in activity_l for k in HIGH_RISK_ACTIVITIES)

    source = "Manual input"
    timestamp = None
    condition = ""
    wind = None
    temp = None

    if weather:
        source = weather.get("source", "Weather provider")
        timestamp = weather.get("timestamp")
        condition = weather.get("condition") or ""
        wind = weather.get("wind_speed_mps")
        temp = weather.get("temperature_c")
    elif manual_conditions:
        source = "Manual input (user-provided)"
        condition = manual_conditions
    else:
        source = "Unavailable"
        condition = "Not provided"

    hazards = []
    precautions = []
    mitigations = []
    decision = DECISION_GO

    cond_l = (condition or "").lower()

    if any(k in cond_l for k in ["rain", "shower", "storm", "thunder"]):
        hazards.append("Precipitation detected: %s" % condition)
        precautions.append("Protect materials and electrical equipment from moisture.")
        if is_high_risk:
            decision = DECISION_NO_GO
        else:
            decision = DECISION_REVIEW

    if any(k in cond_l for k in ["thunderstorm", "lightning"]):
        hazards.append("Lightning risk.")
        precautions.append("Suspend all outdoor and elevated work during lightning.")
        decision = DECISION_NO_GO

    if wind is not None and wind > 10:
        hazards.append("Strong wind: %s m/s." % wind)
        precautions.append("Secure loose materials; avoid crane/lifting operations.")
        if is_high_risk:
            decision = DECISION_NO_GO

    if temp is not None and temp > 35:
        hazards.append("High temperature: %s C." % temp)
        precautions.append("Provide shade, water, and rest breaks for workers.")
        decision = DECISION_REVIEW

    if "concrete" in activity_l and any(k in cond_l for k in ["rain", "storm"]):
        hazards.append("Rain during concrete work can affect curing and strength.")
        precautions.append("Cover fresh concrete; schedule pours for dry windows.")

    if not hazards:
        hazards.append("No significant weather-related hazards identified from available data.")
        precautions.append("Proceed with standard site safety procedures.")
        decision = DECISION_GO

    if decision == DECISION_GO:
        reasoning = "Conditions appear suitable for '%s' based on available weather data." % activity
    elif decision == DECISION_NO_GO:
        reasoning = "Conditions are not suitable for '%s'. Postpone or reschedule." % activity
    else:
        reasoning = "Conditions require review for '%s'. Confirm with site supervisor before proceeding." % activity

    mitigations = [
        "Monitor official weather warnings throughout the day.",
        "Defer to equipment wind limits and site safety procedures.",
    ]

    return {
        "decision": decision,
        "reasoning": reasoning,
        "hazards": hazards,
        "precautions": precautions,
        "mitigation_actions": mitigations,
        "weather_source": source,
        "weather_timestamp": timestamp,
    }


def weather_advisory(
    *,
    request: WeatherRequest,
) -> dict:
    settings = get_settings()

    weather = None
    if settings.WEATHER_ENABLED:
        weather = _fetch_weather(request.location)
        if weather is None and not request.weather_conditions:
            return {
                "result": _fallback_result(request, "Live weather unavailable and no manual conditions provided."),
                "mode": "fallback",
                "model": None,
                "error": {
                    "code": "weather_unavailable",
                    "message": "Live weather could not be fetched and no manual conditions were provided.",
                },
                "meta": request_metadata(FEATURE, "fallback", None),
            }

    assessment = _assess(request.activity, weather, request.weather_conditions)

    from app.schemas.weather import WeatherResponseData

    response = WeatherResponseData(
        activity=request.activity,
        location=request.location,
        planned_time=request.planned_time,
        decision=assessment["decision"],
        reasoning=assessment["reasoning"],
        hazards=assessment["hazards"],
        precautions=assessment["precautions"],
        mitigation_actions=assessment["mitigation_actions"],
        weather_source=assessment["weather_source"],
        weather_timestamp=assessment["weather_timestamp"],
        data_limitations=[
            "Weather data source: %s." % assessment["weather_source"],
            "AI recommendation is not authorization to perform dangerous work.",
        ],
    )

    if settings.DEMO_MODE:
        result = {
            "result": response,
            "mode": "demo",
            "model": None,
            "error": None,
            "meta": request_metadata(FEATURE, "demo", None),
        }
    else:
        result = {
            "result": response,
            "mode": "fallback",
            "model": None,
            "error": None,
            "meta": request_metadata(FEATURE, "fallback", None),
        }

    return result
