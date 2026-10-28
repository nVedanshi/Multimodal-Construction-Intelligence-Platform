from __future__ import annotations

from app.schemas.planning import ProjectPlanningRequest
from app.schemas.valuation import ValuationRequest
from app.schemas.common import ErrorResponse


def test_planning_request_valid():
    req = ProjectPlanningRequest(
        project_name="Demo House",
        location="Pune",
        construction_type="residential",
        intended_use="house",
        num_floors=2,
        plot_area=200,
        plot_area_unit="sqm",
        quality_level="medium",
    )
    assert req.num_floors == 2
    assert req.construction_type == "residential"


def test_planning_request_invalid_type():
    try:
        ProjectPlanningRequest(
            project_name="X",
            construction_type="invalid_type",
            intended_use="house",
            num_floors=1,
        )
        assert False, "Should have raised validation error"
    except Exception:
        assert True


def test_valuation_area_units():
    req = ValuationRequest(
        city="Pune",
        locality="Kothrud",
        property_type="residential",
        area_value=100,
        area_unit="sqm",
        condition="good",
    )
    assert req.area_unit == "sqm"


def test_error_response_shape():
    err = ErrorResponse(error="test_error", message="Something went wrong")
    assert err.success is False
    assert err.error == "test_error"
