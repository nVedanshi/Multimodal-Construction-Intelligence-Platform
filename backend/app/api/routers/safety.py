from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, File, Form, UploadFile, HTTPException

from app.services.safety_service import analyze_safety
from app.schemas.safety import SafetyAnalysisResponseData, SafetyAnalysisError
from app.utils.file import validate_upload, save_upload
from app.utils.responses import error_response, success_response

router = APIRouter()


@router.post("/safety/analyze", tags=["Site Safety Monitoring"])
def analyze_safety_endpoint(
    observation_log: Optional[str] = Form(None),
    site_photo: Optional[UploadFile] = File(None),
    safety_doc: Optional[UploadFile] = File(None),
):
    """Analyze a construction site photograph for safety hazards.

    Accepts multipart form data: optional observation log text, optional site
    photo, optional safety document. Returns a validated JSON safety report.
    """
    image_bytes = None
    image_content_type = None

    if site_photo is not None:
        content = site_photo.file.read()
        err = validate_upload(site_photo.filename or "", len(content))
        if err:
            return error_response(
                code="invalid_upload",
                message=err,
                status_code=400,
                feature="site_safety_monitoring",
            )
        image_bytes = content
        image_content_type = site_photo.content_type or "application/octet-stream"

    try:
        result = analyze_safety(
            observation_log=observation_log,
            image_bytes=image_bytes,
            image_content_type=image_content_type,
        )
    except Exception as exc:
        return error_response(
            code="analysis_failed",
            message="Safety analysis failed: %s" % exc,
            status_code=500,
            feature="site_safety_monitoring",
            mode="fallback",
        )

    if result.get("error"):
        return error_response(
            code=result["error"].get("code", "analysis_failed"),
            message=result["error"].get("message", "Safety analysis unavailable."),
            status_code=502,
            feature="site_safety_monitoring",
            mode=result.get("mode", "fallback"),
            model=result.get("model"),
        )

    data = result["result"]
    if not isinstance(data, SafetyAnalysisResponseData):
        return error_response(
            code="invalid_response",
            message="Safety analysis returned an invalid response.",
            status_code=500,
            feature="site_safety_monitoring",
            mode="fallback",
        )

    return success_response(
        data=data.model_dump(),
        feature="site_safety_monitoring",
        mode=result.get("mode", "demo"),
        model=result.get("model"),
    )
