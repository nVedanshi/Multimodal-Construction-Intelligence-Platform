from __future__ import annotations

from typing import Optional

from app.services.ai_service import (
    call_llm,
    invoke_with_schema,
    request_metadata,
)
from app.schemas.planning import (
    ProjectPlanningRequest,
    ProjectPlanningResponseData,
    PlanningLLMResponse,
    MaterialRequirement,
    CostCategory,
    SchedulePhase,
    Milestone,
    QUALITY_LEVELS,
)

FEATURE = "construction_project_planning"

# --------------------------------------------------------------------------- #
# Thumb-rule factors (documented assumptions, NOT engineering calculations).
# All quantities are per square metre of built-up area.
# --------------------------------------------------------------------------- #
MATERIAL_FACTORS = {
    "cement_bags_per_sqm": 4.0,
    "sand_cum_per_sqm": 0.025,
    "aggregate_cum_per_sqm": 0.035,
    "steel_kg_per_sqm": 25.0,
    "bricks_per_sqm": 55.0,
}

# Indicative unit rates in INR (illustrative only, not a quotation).
UNIT_RATES_INR = {
    "cement_per_bag": 400.0,
    "sand_per_cum": 1800.0,
    "aggregate_per_cum": 1500.0,
    "steel_per_kg": 75.0,
    "bricks_per_unit": 10.0,
}

# Indicative total construction cost per sqm built-up by quality (INR).
COST_PER_SQM = {
    "standard": 15000.0,
    "medium": 22000.0,
    "premium": 32000.0,
}

LABOUR_SHARE_OF_MATERIAL = 0.25
CONTINGENCY_SHARE = 0.10

SQFT_TO_SQM = 0.092903
ACRE_TO_SQM = 4046.86


def _to_sqm(value: Optional[float], unit: str) -> Optional[float]:
    if value is None:
        return None
    if unit == "sqft":
        return value * SQFT_TO_SQM
    if unit == "acre":
        return value * ACRE_TO_SQM
    return value  # sqm


def _round2(value: float) -> float:
    return round(value, 2)


def _demo_result(request: ProjectPlanningRequest) -> ProjectPlanningResponseData:
    return _build_plan(request, demo=True)


def _fallback_result(request: ProjectPlanningRequest, limitation: str) -> ProjectPlanningResponseData:
    plan = _build_plan(request, demo=False)
    plan.recommendations.insert(
        0,
        "Fallback mode: plan generated with standard thumb rules because AI recommendations were unavailable (%s)."
        % limitation,
    )
    return plan


def _build_plan(request: ProjectPlanningRequest, demo: bool) -> ProjectPlanningResponseData:
    plot_area_sqm = _to_sqm(request.plot_area, request.plot_area_unit)
    built_up_area_sqm = _to_sqm(request.built_up_area, request.built_up_area_unit)

    # Derive built-up area from plot area if not provided (thumb rule: 40% FSI).
    if built_up_area_sqm is None and plot_area_sqm is not None:
        built_up_area_sqm = plot_area_sqm * 0.40

    bua = built_up_area_sqm or 100.0  # avoid divide-by-zero in unit costs

    # --- Material requirements (backend-computed thumb rules) --------------- #
    cement_qty = _round2(bua * MATERIAL_FACTORS["cement_bags_per_sqm"])
    sand_qty = _round2(bua * MATERIAL_FACTORS["sand_cum_per_sqm"])
    aggregate_qty = _round2(bua * MATERIAL_FACTORS["aggregate_cum_per_sqm"])
    steel_qty = _round2(bua * MATERIAL_FACTORS["steel_kg_per_sqm"])
    bricks_qty = _round2(bua * MATERIAL_FACTORS["bricks_per_sqm"])

    cement_cost = _round2(cement_qty * UNIT_RATES_INR["cement_per_bag"])
    sand_cost = _round2(sand_qty * UNIT_RATES_INR["sand_per_cum"])
    aggregate_cost = _round2(aggregate_qty * UNIT_RATES_INR["aggregate_per_cum"])
    steel_cost = _round2(steel_qty * UNIT_RATES_INR["steel_per_kg"])
    bricks_cost = _round2(bricks_qty * UNIT_RATES_INR["bricks_per_unit"])

    material_requirements = [
        MaterialRequirement(material="Cement", quantity=cement_qty, unit="bags", estimated_cost_inr=cement_cost),
        MaterialRequirement(material="Sand", quantity=sand_qty, unit="cubic metres", estimated_cost_inr=sand_cost),
        MaterialRequirement(material="Aggregate", quantity=aggregate_qty, unit="cubic metres", estimated_cost_inr=aggregate_cost),
        MaterialRequirement(material="Steel", quantity=steel_qty, unit="kg", estimated_cost_inr=steel_cost),
        MaterialRequirement(material="Bricks/Blocks", quantity=bricks_qty, unit="units", estimated_cost_inr=bricks_cost),
    ]

    total_material_cost = _round2(
        cement_cost + sand_cost + aggregate_cost + steel_cost + bricks_cost
    )

    # --- Cost estimate (backend-computed) --------------------------------- #
    labour_cost = _round2(total_material_cost * LABOUR_SHARE_OF_MATERIAL)
    contingency = _round2((total_material_cost + labour_cost) * CONTINGENCY_SHARE)

    unit_rate = COST_PER_SQM.get(request.quality_level, COST_PER_SQM["medium"])
    total_estimated_cost = _round2(bua * unit_rate)

    cost_categories = [
        CostCategory(category="Materials", estimated_cost_inr=total_material_cost, notes="Thumb-rule quantities x indicative unit rates."),
        CostCategory(category="Labour", estimated_cost_inr=labour_cost, notes="Approx. %d%% of material cost." % int(LABOUR_SHARE_OF_MATERIAL * 100)),
        CostCategory(category="Contingency", estimated_cost_inr=contingency, notes="Approx. %d%% of materials + labour." % int(CONTINGENCY_SHARE * 100)),
    ]

    # --- Schedule (phase-wise / week-wise) --------------------------------- #
    weeks_per_floor = 4.0
    total_weeks = _round2(request.num_floors * weeks_per_floor)
    schedule_phases = [
        SchedulePhase(phase="Site preparation & foundation", week=1, activities=["Site clearing", "Setting out", "Foundation excavation", "Footings"], duration_weeks=2.0),
        SchedulePhase(phase="Structure", week=3, activities=["Column & beam work", "Slab casting", "Masonry"], duration_weeks=_round2(total_weeks - 6) if total_weeks > 6 else 2.0),
        SchedulePhase(phase="Finishing", week=int(total_weeks) - 1 if total_weeks > 2 else 2, activities=["Plastering", "Flooring", "Painting", "Fixtures"], duration_weeks=3.0),
    ]

    milestones = [
        Milestone(name="Foundation complete", target_week=2, description="Foundation and footings finished."),
        Milestone(name="Structure complete", target_week=int(total_weeks) - 3 if total_weeks > 3 else 2, description="Main structural frame finished."),
        Milestone(name="Project completion", target_week=int(total_weeks), description="Finishing and handover."),
    ]

    recommendations = [
        "Confirm plot dimensions and built-up area with a survey before procurement.",
        "Purchase materials in phases to reduce storage and wastage.",
        "Engage a structural engineer to validate the design for load-bearing elements.",
        "Obtain local building approvals before commencing construction.",
    ]

    assumptions = [
        "Quantities use documented thumb rules per square metre of built-up area.",
        "Unit rates are indicative and vary by city, supplier, and market conditions.",
        "Labour estimated as %d%% of material cost." % int(LABOUR_SHARE_OF_MATERIAL * 100),
        "Contingency estimated as %d%% of materials + labour." % int(CONTINGENCY_SHARE * 100),
        "If built-up area was not provided, it was approximated as 40%% of plot area (FSI assumption).",
    ]

    visualization = {
        "type": "conceptual_layout",
        "label": "Conceptual block layout (not an architectural drawing)",
        "plot_area_sqm": plot_area_sqm,
        "built_up_area_sqm": built_up_area_sqm,
        "num_floors": request.num_floors,
        "note": "Replace with a real architectural layout from a qualified professional.",
    }

    return ProjectPlanningResponseData(
        project_name=request.project_name,
        location=request.location,
        construction_type=request.construction_type,
        intended_use=request.intended_use,
        num_floors=request.num_floors,
        plot_area_sqm=_round2(plot_area_sqm) if plot_area_sqm else None,
        built_up_area_sqm=_round2(built_up_area_sqm) if built_up_area_sqm else None,
        quality_level=request.quality_level,
        material_requirements=material_requirements,
        total_material_cost_inr=total_material_cost,
        cost_categories=cost_categories,
        total_estimated_cost_inr=total_estimated_cost,
        labour_cost_inr=labour_cost,
        contingency_inr=contingency,
        cost_assumptions=assumptions,
        schedule_phases=schedule_phases,
        milestones=milestones,
        recommendations=recommendations,
        visualization=visualization,
        disclaimer=(
            "Indicative planning estimate based on standard thumb rules. Not an "
            "engineering calculation, contractor quotation, or binding cost estimate."
        ),
    )


def plan_project(
    *,
    request: ProjectPlanningRequest,
) -> dict:
    result = invoke_with_schema(
        system_prompt=(
            "You are a construction planning assistant. Provide practical, "
            "concise planning recommendations and assumptions for the given "
            "project parameters. Do not invent material quantities or costs; "
            "those are computed by the backend. Return ONLY a JSON object with "
            "these exact fields: \"recommendations\" (array of strings), "
            "\"assumptions\" (array of strings). Output format: json"
        ),
        user_text=(
            "Project: %s\nLocation: %s\nType: %s\nUse: %s\nFloors: %s\n"
            "Plot area: %s %s\nBuilt-up area: %s %s\nQuality: %s"
            % (
                request.project_name,
                request.location or "Not provided",
                request.construction_type,
                request.intended_use,
                request.num_floors,
                request.plot_area or "Not provided",
                request.plot_area_unit,
                request.built_up_area or "Not provided",
                request.built_up_area_unit,
                request.quality_level,
            )
        ),
        feature=FEATURE,
        schema_class=PlanningLLMResponse,
    )

    plan = _build_plan(request, demo=(result["mode"] == "demo"))

    if result["mode"] == "demo":
        result["result"] = plan
        result["error"] = None
    elif result["error"] or result["result"] is None:
        limitation = (
            result["error"]["message"]
            if result["error"]
            else "AI recommendations unavailable."
        )
        result["result"] = _fallback_result(request, limitation)
        result["mode"] = "fallback"
        result["error"] = None
    else:
        # Merge LLM narrative recommendations/assumptions if valid.
        try:
            llm_plan = result["result"]
            if isinstance(llm_plan, PlanningLLMResponse):
                if llm_plan.recommendations:
                    plan.recommendations = llm_plan.recommendations
                if llm_plan.assumptions:
                    plan.cost_assumptions = llm_plan.assumptions
            result["result"] = plan
            result["error"] = None
        except Exception:
            result["result"] = plan
            result["error"] = None
            result["mode"] = "fallback"

    result["meta"] = request_metadata(FEATURE, result["mode"], result["model"])
    return result
