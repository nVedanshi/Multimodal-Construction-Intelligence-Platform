from __future__ import annotations

from typing import Optional

from app.services.ai_service import (
    call_llm,
    invoke_with_schema,
    request_metadata,
)
from app.schemas.valuation import (
    ValuationRequest,
    ValuationResponseData,
    ValuationLLMResponse,
    ROICenario,
    PROPERTY_TYPES,
    CONDITIONS,
    AREA_UNITS,
)

FEATURE = "indian_real_estate_valuation"

# --------------------------------------------------------------------------- #
# Illustrative base rates (INR per sq ft) by city tier and property type.
# These are indicative assumptions, NOT verified live market rates.
# --------------------------------------------------------------------------- #
CITY_TIER_BASE = {
    "tier_1": 8500.0,   # e.g. Mumbai, Delhi NCR, Bangalore
    "tier_2": 4500.0,   # e.g. Pune, Hyderabad, Chennai
    "tier_3": 2200.0,   # smaller cities
}

TIER_BY_CITY = {
    "mumbai": "tier_1", "delhi": "tier_1", "new delhi": "tier_1",
    "bangalore": "tier_1", "bengaluru": "tier_1",
    "chennai": "tier_2", "hyderabad": "tier_2", "pune": "tier_2",
    "kolkata": "tier_2", "ahmedabad": "tier_2",
}

PROPERTY_TYPE_FACTOR = {
    "residential": 1.0,
    "commercial": 1.2,
    "industrial": 0.8,
    "land": 0.5,
    "other": 0.9,
}

CONDITION_MULTIPLIER = {
    "excellent": 1.10,
    "good": 1.00,
    "average": 0.90,
    "fair": 0.75,
    "poor": 0.60,
}

RENTAL_YIELD_BY_TYPE = {
    "residential": 3.0,
    "commercial": 5.0,
    "industrial": 4.0,
    "land": 0.0,
    "other": 2.5,
}

EXPENSE_SHARE_OF_RENT = 0.20  # maintenance, tax, insurance

SQFT_TO_SQM = 0.092903
SQM_TO_SQFT = 10.7639
SQYARD_TO_SQFT = 9.0
ACRE_TO_SQFT = 43560.0
HECTARE_TO_SQFT = 107639.0


def _to_sqft(value: float, unit: str) -> float:
    if unit == "sqm":
        return value * SQM_TO_SQFT
    if unit == "sqyard":
        return value * SQYARD_TO_SQFT
    if unit == "acre":
        return value * ACRE_TO_SQFT
    if unit == "hectare":
        return value * HECTARE_TO_SQFT
    return value  # sqft


def _round2(value: float) -> float:
    return round(value, 2)


def _city_tier(city: str) -> str:
    return TIER_BY_CITY.get(city.strip().lower(), "tier_3")


def _demo_result(request: ValuationRequest) -> ValuationResponseData:
    return _value(request, demo=True)


def _fallback_result(request: ValuationRequest, limitation: str) -> ValuationResponseData:
    result = _value(request, demo=False)
    result.data_limitations.insert(
        0,
        "Fallback mode: indicative estimate only because live valuation logic was unavailable (%s)." % limitation,
    )
    return result


def _value(request: ValuationRequest, demo: bool) -> ValuationResponseData:
    area_sqft = _round2(_to_sqft(request.area_value, request.area_unit))
    if area_sqft <= 0:
        area_sqft = 1.0  # avoid division by zero

    tier = _city_tier(request.city)
    base_rate = CITY_TIER_BASE[tier] * PROPERTY_TYPE_FACTOR[request.property_type]
    condition_mult = CONDITION_MULTIPLIER[request.condition]

    # Age depreciation: up to 1% per year, capped at 20%.
    age = request.property_age_years or 0
    age_multiplier = max(0.80, 1.0 - 0.01 * age)

    # Amenities / parking adjustment.
    amenity_mult = 1.0
    if request.amenities:
        amenity_mult += 0.03
    if request.parking:
        amenity_mult += 0.05

    # Floor adjustment for apartments.
    floor_mult = 1.0
    if request.property_type == "residential" and request.floor_number is not None and request.total_floors:
        if request.total_floors > 1:
            mid = request.total_floors / 2.0
            if abs(request.floor_number - mid) < 1:
                floor_mult = 1.05  # middle floors slight premium
            elif request.floor_number == request.total_floors:
                floor_mult = 0.95  # top floor slight discount

    price_per_sqft = _round2(base_rate * condition_mult * age_multiplier * amenity_mult * floor_mult)
    value_mid = _round2(price_per_sqft * area_sqft)
    value_min = _round2(value_mid * 0.90)
    value_max = _round2(value_mid * 1.10)

    # Rental & ROI (backend-computed).
    annual_yield_pct = RENTAL_YIELD_BY_TYPE[request.property_type]
    annual_rent = _round2(value_mid * annual_yield_pct / 100.0)
    monthly_rent = _round2(annual_rent / 12.0) if annual_rent else None
    annual_expenses = _round2(annual_rent * EXPENSE_SHARE_OF_RENT)
    yield_percent = _round2(annual_rent / value_mid * 100.0) if value_mid else None

    roi_scenarios = []
    for label, mult in [("conservative", 0.7), ("expected", 1.0), ("optimistic", 1.4)]:
        scen_rent = _round2(annual_rent * mult)
        scen_exp = _round2(scen_rent * EXPENSE_SHARE_OF_RENT)
        scen_net = _round2(scen_rent - scen_exp)
        scen_roi = _round2(scen_net / value_mid * 100.0) if value_mid else 0.0
        roi_scenarios.append(ROICenario(
            scenario=label,
            annual_rental_income_inr=scen_rent,
            annual_expenses_inr=scen_exp,
            net_annual_income_inr=scen_net,
            roi_percent=scen_roi,
        ))

    appreciation_outlook = (
        "Positive long-term outlook expected for tier_1 city." if tier == "tier_1"
        else "Moderate appreciation expected, subject to local infrastructure."
    ) if not demo else "Demo mode: appreciation outlook is illustrative."

    market_assumptions = [
        "Base rate for city tier '%s' is an illustrative assumption, not a verified market rate." % tier,
        "Condition and age adjustments are standard heuristics.",
        "No verified comparable transactions were used unless a data source is configured.",
    ]

    data_limitations = [
        "Indicative AI estimate only. Not a certified valuation.",
        "Base market rates are illustrative and may not reflect current local prices.",
    ]

    return ValuationResponseData(
        city=request.city,
        locality=request.locality,
        property_type=request.property_type,
        area_sqft=area_sqft,
        area_unit_input=request.area_unit,
        area_value_input=request.area_value,
        property_age_years=age,
        condition=request.condition,
        indicative_value_min_inr=value_min,
        indicative_value_max_inr=value_max,
        indicative_value_mid_inr=value_mid,
        estimated_price_per_sqft_inr=price_per_sqft,
        market_assumptions=market_assumptions,
        estimated_monthly_rent_inr=monthly_rent,
        estimated_annual_rental_yield_percent=yield_percent,
        estimated_annual_expenses_inr=annual_expenses,
        roi_scenarios=roi_scenarios,
        appreciation_outlook=appreciation_outlook,
        data_limitations=data_limitations,
        disclaimer=(
            "Indicative AI estimate only. Not a certified valuation and not based "
            "on verified live comparable transactions unless a data source is configured."
        ),
    )


def value_property(
    *,
    request: ValuationRequest,
) -> dict:
    result = invoke_with_schema(
        system_prompt=(
            "You are an Indian real estate valuation assistant. Provide qualitative "
            "market assumptions and an appreciation outlook for the property. Do NOT "
            "compute prices or returns; those are calculated by the backend using "
            "explicit formulas. Return ONLY a JSON object with these exact fields: "
            "\"market_assumptions\" (array of strings), \"appreciation_outlook\" "
            "(string), \"data_limitations\" (array of strings). Output format: json"
        ),
        user_text=(
            "City: %s\nLocality: %s\nType: %s\nArea: %s %s\nAge: %s years\n"
            "Condition: %s\nAmenities: %s\nParking: %s\nFloor: %s/%s"
            % (
                request.city, request.locality, request.property_type,
                request.area_value, request.area_unit,
                request.property_age_years or "Not provided",
                request.condition,
                request.amenities or "Not provided",
                request.parking,
                request.floor_number or "Not provided",
                request.total_floors or "Not provided",
            )
        ),
        feature=FEATURE,
        schema_class=ValuationLLMResponse,
    )

    valuation = _value(request, demo=(result["mode"] == "demo"))

    if result["mode"] == "demo":
        result["result"] = valuation
        result["error"] = None
    elif result["error"] or result["result"] is None:
        limitation = (
            result["error"]["message"]
            if result["error"]
            else "AI narrative unavailable."
        )
        result["result"] = _fallback_result(request, limitation)
        result["mode"] = "fallback"
        result["error"] = None
    else:
        try:
            llm = result["result"]
            if isinstance(llm, ValuationLLMResponse):
                if llm.market_assumptions:
                    valuation.market_assumptions = llm.market_assumptions
                if llm.appreciation_outlook:
                    valuation.appreciation_outlook = llm.appreciation_outlook
                if llm.data_limitations:
                    valuation.data_limitations = llm.data_limitations
            result["result"] = valuation
            result["error"] = None
        except Exception:
            result["result"] = valuation
            result["error"] = None
            result["mode"] = "fallback"

    result["meta"] = request_metadata(FEATURE, result["mode"], result["model"])
    return result
