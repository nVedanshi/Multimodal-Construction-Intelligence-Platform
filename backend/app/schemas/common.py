"""
Common schemas shared across all features.

Defines consistent success/error response conventions, response metadata, and
reusable field types. Every feature response embeds a ``meta`` block indicating
the feature, analysis mode, and whether the result came from a real AI request
or demo/fallback logic.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, Optional, TypeVar
from uuid import uuid4

from pydantic import BaseModel, Field

T = TypeVar("T")

MODE_REAL_AI = "real_ai"
MODE_DEMO = "demo"
MODE_FALLBACK = "fallback"


class ResponseMeta(BaseModel):
    """Metadata attached to every API response."""

    feature: str = Field(
        "unknown", description="Invoked feature identifier."
    )
    mode: str = Field(
        "fallback",
        description="Analysis mode: real_ai, demo, or fallback.",
        examples=["real_ai", "demo", "fallback"],
    )
    model: Optional[str] = Field(
        None, description="LLM model used (real_ai mode only)."
    )
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class ErrorDetail(BaseModel):
    """A single validation / error detail."""

    field: Optional[str] = None
    message: str


class ErrorResponse(BaseModel):
    """Consistent error response envelope."""

    success: bool = False
    error: str = Field(..., description="Error category/code.")
    message: str = Field(..., description="Human-readable error message.")
    details: Optional[list[ErrorDetail]] = Field(
        None, description="Field-level validation details when applicable."
    )
    meta: ResponseMeta = Field(default_factory=ResponseMeta)


class APIResponse(BaseModel, Generic[T]):
    """Generic success response envelope."""

    success: bool = True
    data: T
    meta: ResponseMeta = Field(default_factory=ResponseMeta)


class HealthResponse(BaseModel):
    """Health-check response."""

    status: str = "ok"
    name: str
    version: str
    environment: str
    groq_configured: bool
    vision_available: bool
    demo_mode: bool
    database: str = "sqlite"
