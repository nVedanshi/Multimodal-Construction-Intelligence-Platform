"""
Application configuration.

All provider credentials and external service configuration are read exclusively
from environment variables (via python-dotenv). Secrets are never hard-coded and
never exposed through the frontend, logs, or API responses.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

try:  # python-dotenv is optional at import time; load if available
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except Exception:  # pragma: no cover - dotenv may not be installed
    pass


def _get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)).strip())
    except (TypeError, ValueError):
        return default


def _get_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)).strip())
    except (TypeError, ValueError):
        return default


class Settings:
    """Centralized application settings."""

    # ------------------------------------------------------------------ #
    # Application
    # ------------------------------------------------------------------ #
    APP_NAME: str = "AI-Powered Multimodal Construction Intelligence Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = _get_bool("DEBUG", False)
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # ------------------------------------------------------------------ #
    # Server
    # ------------------------------------------------------------------ #
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = _get_int("PORT", 8000)
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

    # ------------------------------------------------------------------ #
    # Security / files
    # ------------------------------------------------------------------ #
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    MAX_UPLOAD_SIZE_MB: int = _get_int("MAX_UPLOAD_SIZE_MB", 10)
    ALLOWED_IMAGE_EXTENSIONS: set[str] = {
        ext.strip().lower() for ext in os.getenv(
            "ALLOWED_IMAGE_EXTENSIONS", "jpg,jpeg,png,webp"
        ).split(",") if ext.strip()
    }
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    REPORTS_DIR: str = os.getenv("REPORTS_DIR", "reports")

    # ------------------------------------------------------------------ #
    # Database (SQLite)
    # ------------------------------------------------------------------ #
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./construction_intelligence.db")

    # ------------------------------------------------------------------ #
    # Groq / LLM
    # ------------------------------------------------------------------ #
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    GROQ_MODEL_TEXT: str = os.getenv("GROQ_MODEL_TEXT", "llama-3.1-8b-instant")
    GROQ_MODEL_VISION: Optional[str] = os.getenv("GROQ_MODEL_VISION")
    # Whether vision/image analysis is enabled for the configured vision model.
    VISION_ENABLED: bool = _get_bool("VISION_ENABLED", False)
    # Timeout in seconds for LLM requests.
    LLM_REQUEST_TIMEOUT_SECONDS: int = _get_int("LLM_REQUEST_TIMEOUT_SECONDS", 60)
    LLM_MAX_RETRIES: int = _get_int("LLM_MAX_RETRIES", 2)
    # Demo mode: when True, deterministic sample responses are returned instead
    # of calling the LLM provider. Clearly labelled in every response.
    DEMO_MODE: bool = _get_bool("DEMO_MODE", True)

    # ------------------------------------------------------------------ #
    # Weather (optional external provider)
    # ------------------------------------------------------------------ #
    WEATHER_API_KEY: Optional[str] = os.getenv("WEATHER_API_KEY")
    WEATHER_BASE_URL: str = os.getenv(
        "WEATHER_BASE_URL",
        "https://api.openweathermap.org/data/2.5/weather",
    )
    WEATHER_REQUEST_TIMEOUT_SECONDS: int = _get_int(
        "WEATHER_REQUEST_TIMEOUT_SECONDS", 10
    )
    WEATHER_ENABLED: bool = _get_bool("WEATHER_ENABLED", False)

    # ------------------------------------------------------------------ #
    # Derived helpers
    # ------------------------------------------------------------------ #
    @property
    def groq_configured(self) -> bool:
        """Whether Groq credentials are present."""
        return bool(self.GROQ_API_KEY and self.GROQ_API_KEY.strip())

    @property
    def vision_available(self) -> bool:
        """Whether a compatible vision model is configured and enabled."""
        return bool(
            self.groq_configured
            and self.GROQ_MODEL_VISION
            and self.GROQ_MODEL_VISION.strip()
            and self.VISION_ENABLED
        )


@lru_cache()
def get_settings() -> Settings:
    """Cached settings accessor."""
    return Settings()


settings = get_settings()
