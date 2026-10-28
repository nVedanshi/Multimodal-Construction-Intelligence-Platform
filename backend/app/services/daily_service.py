from __future__ import annotations

from typing import Optional

from app.services.ai_service import (
    call_llm,
    invoke_with_schema,
    request_metadata,
)
from app.schemas.daily import (
    DailySiteRequest,
    DailySiteResponseData,
    DailyLLMResponse,
    DailyTask,
)

FEATURE = "daily_site_assistant"


def _list_to_str(value) -> Optional[str]:
    """Convert a str or List[str] value to a single string."""
    if value is None:
        return None
    if isinstance(value, list):
        return "; ".join(str(v) for v in value)
    return str(value)

SYSTEM_PROMPT = (
    "You are a daily construction site planning assistant. Generate a "
    "practical daily action plan from the provided site inputs. Include "
    "prioritized tasks, workforce and equipment requirements, material "
    "preparation, safety checks, possible risks, coordination notes, and "
    "follow-up actions. Separate user-entered facts from AI-generated "
    "suggestions. Disclose assumptions. Do not replace a site engineer's "
    "professional judgment. Return ONLY a JSON object with these exact "
    "fields: \"prioritized_tasks\" (array of objects with id, title, priority, "
    "category, description, workforce_required, equipment_required, materials, "
    "safety_checks, risks, completed), \"workforce_requirements\" (string), "
    "\"equipment_requirements\" (string), \"material_preparation\" (string), "
    "\"safety_checks\" (array of strings), \"possible_risks\" (array of "
    "strings), \"coordination_notes\" (string), \"recommended_follow_up\" "
    "(array of strings), \"assumptions\" (array of strings). Output format: json"
)


def _demo_result(request: DailySiteRequest) -> DailySiteResponseData:
    return DailySiteResponseData(
        date=request.date,
        project_phase=request.project_phase,
        prioritized_tasks=[
            DailyTask(
                id="demo-1",
                title="Demo task placeholder",
                priority="medium",
                category="demo",
                description="No live daily plan was generated.",
                workforce_required="Not specified",
                equipment_required="Not specified",
                materials="Not specified",
                safety_checks="Not specified",
                risks="Not specified",
                completed=False,
            )
        ],
        workforce_requirements="Demo mode: not computed.",
        equipment_requirements="Demo mode: not computed.",
        material_preparation="Demo mode: not computed.",
        safety_checks=["Conduct a daily safety briefing."],
        possible_risks=["Demo mode: risks not assessed."],
        coordination_notes="Demo response. Replace with live output.",
        recommended_follow_up=["Confirm plan with site engineer."],
        assumptions=["Demo response. All task details are placeholders."],
    )


def _fallback_result(request: DailySiteRequest, limitation: str) -> DailySiteResponseData:
    return DailySiteResponseData(
        date=request.date,
        project_phase=request.project_phase,
        prioritized_tasks=[
            DailyTask(
                id="fallback-1",
                title="Review site plan with engineer",
                priority="high",
                category="coordination",
                description=("Fallback plan due to: %s" % limitation),
                workforce_available="As available",
                completed=False,
            )
        ],
        workforce_requirements=request.workforce_availability or "Not specified",
        equipment_requirements=request.equipment or "Not specified",
        material_preparation=request.materials or "Not specified",
        safety_checks=["Conduct daily safety briefing.", "Verify PPE availability."],
        possible_risks=["AI daily plan unavailable; manual coordination required."],
        coordination_notes="Fallback mode. Coordinate manually with the site team.",
        recommended_follow_up=["Confirm tasks with the site engineer."],
        assumptions=["Fallback response due to AI unavailability."],
    )


def plan_daily_site(
    *,
    request: DailySiteRequest,
) -> dict:
    user_text = (
        "Date: %s\nProject phase: %s\nPlanned activities: %s\n"
        "Workforce availability: %s\nMaterials: %s\nEquipment: %s\n"
        "Site conditions: %s\nConstraints: %s"
        % (
            request.date,
            request.project_phase,
            request.planned_activities or "Not provided",
            request.workforce_availability or "Not provided",
            request.materials or "Not provided",
            request.equipment or "Not provided",
            request.site_conditions or "Not provided",
            request.constraints or "Not provided",
        )
    )

    result = invoke_with_schema(
        system_prompt=SYSTEM_PROMPT,
        user_text=user_text,
        feature=FEATURE,
        schema_class=DailyLLMResponse,
    )

    if result["mode"] == "demo":
        result["result"] = _demo_result(request)
        result["error"] = None
    elif result["error"] or result["result"] is None:
        limitation = (
            result["error"]["message"]
            if result["error"]
            else "Daily planning unavailable."
        )
        result["result"] = _fallback_result(request, limitation)
        result["mode"] = "fallback"
        result["error"] = None
    else:
        # Merge LLM narrative with request data to build full response.
        try:
            llm = result["result"]
            tasks = []
            if llm.prioritized_tasks:
                for i, t in enumerate(llm.prioritized_tasks):
                    tasks.append(
                        DailyTask(
                            id=t.get("id") or "task-%d" % (i + 1),
                            title=t.get("title") or "Task %d" % (i + 1),
                            priority=t.get("priority") or "medium",
                            category=t.get("category"),
                            description=t.get("description") or "",
                            workforce_required=_list_to_str(t.get("workforce_required")),
                            equipment_required=_list_to_str(t.get("equipment_required")),
                            materials=_list_to_str(t.get("materials")),
                            safety_checks=_list_to_str(t.get("safety_checks")),
                            risks=_list_to_str(t.get("risks")),
                            completed=False,
                        )
                    )
            if not tasks:
                tasks = [
                    DailyTask(
                        id="task-1",
                        title="Review site plan with engineer",
                        priority="high",
                        category="coordination",
                        description="AI plan generated with backend defaults.",
                        workforce_available="As available",
                        completed=False,
                    )
                ]
            result["result"] = DailySiteResponseData(
                date=request.date,
                project_phase=request.project_phase,
                prioritized_tasks=tasks,
                workforce_requirements=llm.workforce_requirements
                or request.workforce_availability
                or "Not specified",
                equipment_requirements=llm.equipment_requirements
                or request.equipment
                or "Not specified",
                material_preparation=llm.material_preparation
                or request.materials
                or "Not specified",
                safety_checks=llm.safety_checks
                or ["Conduct daily safety briefing.", "Verify PPE availability."],
                possible_risks=llm.possible_risks
                or ["AI daily plan unavailable; manual coordination required."],
                coordination_notes=llm.coordination_notes
                or "Coordinate manually with the site team.",
                recommended_follow_up=llm.recommended_follow_up
                or ["Confirm tasks with the site engineer."],
                assumptions=llm.assumptions
                or ["AI-generated plan with backend-computed defaults."],
            )
            result["error"] = None
        except Exception:
            result["result"] = _fallback_result(request, "LLM response merge failed.")
            result["mode"] = "fallback"
            result["error"] = None

    result["meta"] = request_metadata(FEATURE, result["mode"], result["model"])
    return result
