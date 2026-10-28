from __future__ import annotations

from fastapi import APIRouter

from app.services.valuation_service import value_property
from app.schemas.valuation import ValuationRequest, ValuationResponseData
from app.utils.responses import error_response, success_response

router = APIRouter()


@router.post("/valuation/property", tags=["Indian Real Estate Valuation"])
def value_property_endpoint(request: ValuationRequest):
    """Generate an indicative Indian real estate valuation.

    Accepts property details, normalizes area units, and returns an indicative
    market value range in INR, price per square foot, rental yield, and ROI
    scenarios. All numerical metrics are backend-computed using explicit
    formulas.
    """
    try:
        result = value_property(request=request)
    except Exception as exc:
        return error_response(
            code="valuation_failed",
            message="Property valuation failed: %s" % exc,
            status_code=500,
            feature="indian_real_estate_valuation",
            mode="fallback",
        )

    if result.get("error"):
        return error_response(
            code=result["error"].get("code", "valuation_failed"),
            message=result["error"].get("message", "Property valuation unavailable."),
            status_code=502,
            feature="indian_real_estate_valuation",
            mode=result.get("mode", "fallback"),
            model=result.get("model"),
        )

    data = result["result"]
    if not isinstance(data, ValuationResponseData):
        return error_response(
            code="invalid_response",
            message="Valuation returned an invalid response.",
            status_code=500,
            feature="indian_real_estate_valuation",
            mode="fallback",
        )

    return success_response(
        data=data.model_dump(),
        feature="indian_real_estate_valuation",
        mode=result.get("mode", "demo"),
        model=result.get("model"),
    )
