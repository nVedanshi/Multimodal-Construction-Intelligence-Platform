from __future__ import annotations

from fastapi import APIRouter

from app.config import get_settings
from app.schemas.common import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """Health-check endpoint. Returns service status and configuration summary."""
    settings = get_settings()
    return HealthResponse(
        name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        groq_configured=settings.groq_configured,
        vision_available=settings.vision_available,
        demo_mode=settings.DEMO_MODE,
    )
