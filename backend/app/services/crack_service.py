from __future__ import annotations

from typing import Optional

from app.services.ai_service import (
    call_llm,
    image_to_data_uri,
    invoke_with_schema,
    request_metadata,
)
from app.schemas.crack import (
    CrackAnalysisResponseData,
    CrackCharacteristic,
    CRACK_PATTERN_CATEGORIES,
    SEVERITY_LEVELS,
)

FEATURE = "structural_crack_detection"

SYSTEM_PROMPT = (
    "You are a structural crack analysis assistant. Analyse the provided "
    "photograph of a wall, concrete, column, beam, or similar surface. Assess "
    "visible crack patterns, orientation, continuity, and branching where "
    "visible. Classify the apparent crack pattern (hairline, vertical, "
    "diagonal, map cracking, potentially structural, or other). Do NOT invent "
    "physical measurements, crack widths, depths, or structural diagnoses. "
    "State clearly that an image alone cannot establish structural safety or "
    "the actual cause of a crack. Return ONLY a JSON object with these exact "
    "fields: \"crack_classification\" (string), "
    "\"observable_characteristics\" (array of objects with characteristic, "
    "description, confidence), \"continuity\" (string or null), "
    "\"apparent_orientation\" (string or null), \"preliminary_severity\" "
    "(string: low/moderate/high/severe), \"possible_causes\" (array of "
    "strings), \"uncertainty\" (string), \"potential_risks\" (array of "
    "strings), \"recommended_next_steps\" (array of strings), "
    "\"maintenance_suggestions\" (array of strings), "
    "\"needs_professional_inspection\" (boolean), \"disclaimer\" (string). "
    "Include a disclaimer that a qualified structural engineer should assess "
    "severe or potentially dangerous cracks. Output format: json"
)


def _demo_result() -> CrackAnalysisResponseData:
    return CrackAnalysisResponseData(
        image_id=None,
        crack_classification="other",
        observable_characteristics=[
            CrackCharacteristic(
                characteristic="Demo placeholder",
                description="No live crack analysis was performed.",
                confidence="low",
            )
        ],
        continuity=None,
        apparent_orientation=None,
        preliminary_severity="low",
        possible_causes=[],
        uncertainty=(
            "Demo response. Image-only analysis cannot confirm crack type, "
            "severity, or cause."
        ),
        potential_risks=[],
        recommended_next_steps=[
            "Consult a qualified structural engineer for any crack in a "
            "load-bearing element."
        ],
        maintenance_suggestions=["Monitor the crack for changes over time."],
        needs_professional_inspection=True,
        disclaimer=(
            "Image-only preliminary assessment. Cannot establish structural "
            "safety, actual crack cause, or physical measurements. Consult a "
            "qualified structural engineer for load-bearing or severe cracks."
        ),
    )


def _fallback_result(limitation: str) -> CrackAnalysisResponseData:
    return CrackAnalysisResponseData(
        image_id=None,
        crack_classification="other",
        observable_characteristics=[],
        continuity=None,
        apparent_orientation=None,
        preliminary_severity="low",
        possible_causes=[],
        uncertainty=limitation,
        potential_risks=[],
        recommended_next_steps=[
            "Engage a qualified structural engineer to assess the crack."
        ],
        maintenance_suggestions=[],
        needs_professional_inspection=True,
        disclaimer=(
            "Image-only preliminary assessment. Cannot establish structural "
            "safety, actual crack cause, or physical measurements. Consult a "
            "qualified structural engineer for load-bearing or severe cracks."
        ),
    )


def analyze_crack(
    *,
    image_bytes: Optional[bytes],
    image_content_type: Optional[str],
    surface_type: Optional[str] = None,
    element_type: Optional[str] = None,
    age_years: Optional[float] = None,
    noted_concerns: Optional[str] = None,
) -> dict:
    context_parts = []
    if surface_type:
        context_parts.append("Surface type: %s" % surface_type)
    if element_type:
        context_parts.append("Element type: %s" % element_type)
    if age_years is not None:
        context_parts.append("Approximate age: %s years" % age_years)
    if noted_concerns:
        context_parts.append("User-noted concerns: %s" % noted_concerns)
    context = "\n".join(context_parts) if context_parts else "No structural context provided."

    user_text = (
        "Structural context:\n%s\n\nPlease analyse the attached crack image."
        % context
    )

    result = invoke_with_schema(
        system_prompt=SYSTEM_PROMPT,
        user_text=user_text,
        feature=FEATURE,
        schema_class=CrackAnalysisResponseData,
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
