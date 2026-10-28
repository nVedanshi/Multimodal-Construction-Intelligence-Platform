from __future__ import annotations

from typing import Optional

from app.services.ai_service import (
    call_llm,
    image_to_data_uri,
    invoke_with_schema,
    request_metadata,
)
from app.schemas.safety import (
    SafetyAnalysisResponseData,
    SafetyHazard,
    validate_risk_level,
)

FEATURE = "site_safety_monitoring"

SYSTEM_PROMPT = (
    "You are a construction site safety analyst. Analyse the provided site "
    "photograph and optional observation log. Identify visible safety concerns "
    "such as missing PPE, unsafe worker positioning, proximity to hazards, "
    "elevated work, scaffolding concerns, open edges, debris, poor lighting, "
    "and other observable risks. Distinguish directly observable conditions "
    "from uncertain interpretations. If the image is blurry, incomplete, or "
    "unsuitable, state the limitation instead of inventing observations. "
    "Return ONLY a JSON object with these exact fields: \"summary\" (string), "
    "\"overall_risk_level\" (string: low/medium/high/critical), "
    "\"identified_hazards\" (array of objects with hazard, category, severity, "
    "observable, observation), \"severity\" (string: low/medium/high/critical), "
    "\"supporting_visual_observations\" (array of strings), "
    "\"recommended_ppe\" (array of strings), \"corrective_actions\" (array of "
    "strings), \"preventive_guidelines\" (array of strings), \"uncertainty_notes\" "
    "(string or null), \"disclaimer\" (string). Include a clear disclaimer that "
    "this is an AI-assisted preliminary assessment, not a certified safety "
    "inspection. Output format: json"
)


def _demo_result() -> SafetyAnalysisResponseData:
    return SafetyAnalysisResponseData(
        summary="Demo safety assessment. No image was analysed by a live model.",
        overall_risk_level="medium",
        severity="medium",
        identified_hazards=[
            SafetyHazard(
                hazard="Demo hazard placeholder",
                category="demo",
                severity="medium",
                observable=False,
                observation="This is a deterministic demo response. Replace with live AI output.",
            )
        ],
        supporting_visual_observations=[
            "Demo mode: no visual observations were made."
        ],
        recommended_ppe=["Hard hat", "Safety boots", "High-visibility vest"],
        corrective_actions=["Review site conditions with a qualified safety officer."],
        preventive_guidelines=["Conduct regular site safety walkthroughs."],
        uncertainty_notes="Demo response. All observations are placeholders.",
        disclaimer=(
            "AI-assisted preliminary assessment only. Not a certified safety "
            "inspection and not a substitute for a qualified safety professional."
        ),
    )


def _fallback_result(limitation: str) -> SafetyAnalysisResponseData:
    return SafetyAnalysisResponseData(
        summary="Safety assessment could not be completed: %s" % limitation,
        overall_risk_level="medium",
        severity="medium",
        identified_hazards=[],
        supporting_visual_observations=[],
        recommended_ppe=[],
        corrective_actions=["Engage a qualified safety professional to inspect the site."],
        preventive_guidelines=["Follow applicable site safety procedures and regulations."],
        uncertainty_notes=limitation,
        disclaimer=(
            "AI-assisted preliminary assessment only. Not a certified safety "
            "inspection and not a substitute for a qualified safety professional."
        ),
    )


def analyze_safety(
    *,
    observation_log: Optional[str],
    image_bytes: Optional[bytes],
    image_content_type: Optional[str],
) -> dict:
    user_text = "Observation log: %s" % (observation_log or "Not provided.")

    result = invoke_with_schema(
        system_prompt=SYSTEM_PROMPT,
        user_text=user_text,
        feature=FEATURE,
        schema_class=SafetyAnalysisResponseData,
        image_bytes=image_bytes,
        image_content_type=image_content_type,
        require_vision=True,
    )

    if result["mode"] == "demo":
        result["result"] = _demo_result()
        result["error"] = None
    elif result["error"] or result["result"] is None:
        limitation = (
            result["error"]["message"]
            if result["error"]
            else "AI analysis unavailable."
        )
        result["result"] = _fallback_result(limitation)
        result["mode"] = "fallback"
        result["error"] = None

    result["meta"] = request_metadata(FEATURE, result["mode"], result["model"])
    return result
