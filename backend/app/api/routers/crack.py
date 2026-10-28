from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, File, Form, UploadFile

from app.services.crack_service import analyze_crack
from app.schemas.crack import CrackAnalysisResponseData, CrackRequestContext
from app.utils.file import validate_upload
from app.utils.responses import error_response, success_response

router = APIRouter()


@router.post("/crack/analyze", tags=["Structural Crack Detection"])
def analyze_crack_endpoint(
    image: Optional[UploadFile] = File(None),
    surface_type: Optional[str] = Form(None),
    element_type: Optional[str] = Form(None),
    age_years: Optional[str] = Form(None),
    noted_concerns: Optional[str] = Form(None),
):
    """Analyze a structural crack photograph.

    Accepts multipart form data: crack image plus optional structural context.
    Returns a validated JSON crack analysis report.
    """
    image_bytes = None
    image_content_type = None

    if image is not None:
        content = image.file.read()
        err = validate_upload(image.filename or "", len(content))
        if err:
            return error_response(
                code="invalid_upload",
                message=err,
                status_code=400,
                feature="structural_crack_detection",
            )
        image_bytes = content
        image_content_type = image.content_type or "application/octet-stream"

    age = None
    if age_years is not None and age_years.strip():
        try:
            age = float(age_years)
        except ValueError:
            return error_response(
                code="invalid_input",
                message="age_years must be a number.",
                status_code=400,
                feature="structural_crack_detection",
            )

    try:
        result = analyze_crack(
            image_bytes=image_bytes,
            image_content_type=image_content_type,
            surface_type=surface_type,
            element_type=element_type,
            age_years=age,
            noted_concerns=noted_concerns,
        )
    except Exception as exc:
        return error_response(
            code="analysis_failed",
            message="Crack analysis failed: %s" % exc,
            status_code=500,
            feature="structural_crack_detection",
            mode="fallback",
        )

    if result.get("error"):
        return error_response(
            code=result["error"].get("code", "analysis_failed"),
            message=result["error"].get("message", "Crack analysis unavailable."),
            status_code=502,
            feature="structural_crack_detection",
            mode=result.get("mode", "fallback"),
            model=result.get("model"),
        )

    data = result["result"]
    if not isinstance(data, CrackAnalysisResponseData):
        return error_response(
            code="invalid_response",
            message="Crack analysis returned an invalid response.",
            status_code=500,
            feature="structural_crack_detection",
            mode="fallback",
        )

    return success_response(
        data=data.model_dump(),
        feature="structural_crack_detection",
        mode=result.get("mode", "demo"),
        model=result.get("model"),
    )
