from __future__ import annotations

import base64
import json
import logging
import re
import time
import uuid
from typing import Any, Optional

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger("construction_ai")

GROQ_CLIENT = None
GROQ_IMPORT_ERROR: Optional[str] = None


def _get_groq_client():
    global GROQ_CLIENT, GROQ_IMPORT_ERROR
    if GROQ_CLIENT is not None or GROQ_IMPORT_ERROR is not None:
        return GROQ_CLIENT

    if not settings.groq_configured:
        GROQ_IMPORT_ERROR = "GROQ_API_KEY not configured"
        logger.warning(GROQ_IMPORT_ERROR)
        return None

    try:
        from groq import Groq  # type: ignore

        GROQ_CLIENT = Groq(api_key=settings.GROQ_API_KEY)
        logger.info(
            "Groq client initialized (model_text=%s, model_vision=%s)",
            settings.GROQ_MODEL_TEXT,
            settings.GROQ_MODEL_VISION,
        )
    except ImportError as exc:
        GROQ_IMPORT_ERROR = "groq SDK not installed: %s" % exc
        logger.warning(GROQ_IMPORT_ERROR)
    except Exception as exc:
        GROQ_IMPORT_ERROR = "failed to initialize Groq client: %s" % exc
        logger.warning(GROQ_IMPORT_ERROR)
    return GROQ_CLIENT


def image_to_data_uri(file_bytes: bytes, content_type: str) -> str:
    encoded = base64.b64encode(file_bytes).decode("ascii")
    return "data:%s;base64,%s" % (content_type, encoded)


def extract_text_from_model_response(response: Any) -> str:
    try:
        choices = getattr(response, "choices", None) or []
        if choices:
            message = getattr(choices[0], "message", None)
            if message is not None:
                content = getattr(message, "content", None)
                if content:
                    return content
    except Exception:
        logger.exception("Failed to extract text from model response")
    return ""


JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)
BRACE_RE = re.compile(r"\{.*\}", re.DOTALL)


def parse_model_json(raw: str) -> Optional[dict]:
    if not raw or not raw.strip():
        return None

    text = raw.strip()

    match = JSON_FENCE_RE.search(text)
    if match:
        candidate = match.group(1).strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = BRACE_RE.search(text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return None


class AIServiceError(Exception):
    def __init__(self, message: str, code: str = "ai_service_error", status_code: int = 502):
        super().__init__(message)
        self.code = code
        self.status_code = status_code


def _build_messages(system_prompt: str, user_text: str, image_data_uri: Optional[str] = None) -> list:
    user_content: list = [{"type": "text", "text": user_text}]
    if image_data_uri:
        user_content.append(
            {
                "type": "image_url",
                "image_url": {"url": image_data_uri},
            }
        )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]


def call_llm(
    *,
    system_prompt: str,
    user_text: str,
    feature: str,
    image_bytes: Optional[bytes] = None,
    image_content_type: Optional[str] = None,
    request_json: bool = True,
    model_override: Optional[str] = None,
    require_vision: bool = False,
) -> dict:
    result: dict = {
        "result": None,
        "mode": "demo" if settings.DEMO_MODE else "fallback",
        "model": None,
        "raw_response": None,
        "error": None,
    }

    if settings.DEMO_MODE:
        result["mode"] = "demo"
        result["result"] = {
            "demo": True,
            "feature": feature,
            "note": "Deterministic demo response. No live AI provider was called.",
        }
        logger.info("Demo mode active for feature=%s", feature)
        return result

    client = _get_groq_client()
    if client is None:
        result["mode"] = "fallback"
        result["error"] = {
            "code": "ai_provider_unavailable",
            "message": (
                "Groq provider is unavailable (no client / no API key). "
                "Enable DEMO_MODE for deterministic sample responses."
            ),
        }
        logger.warning("Groq client unavailable for feature=%s", feature)
        return result

    model = model_override or (
        settings.GROQ_MODEL_VISION if (require_vision or image_bytes) else settings.GROQ_MODEL_TEXT
    )
    if require_vision and not settings.vision_available:
        result["mode"] = "fallback"
        result["error"] = {
            "code": "vision_unavailable",
            "message": "No compatible vision model is configured for image analysis.",
        }
        return result

    try:
        image_data_uri = None
        if image_bytes and image_content_type:
            image_data_uri = image_to_data_uri(image_bytes, image_content_type)
        # Some providers require the word "json" in messages when using
        # response_format=json_object.
        json_user_text = user_text
        if request_json:
            json_user_text = user_text + "\n\nOutput format: json"
        messages = _build_messages(system_prompt, json_user_text, image_data_uri)
    except Exception as exc:
        result["mode"] = "fallback"
        result["error"] = {
            "code": "request_build_error",
            "message": "Failed to build LLM request: %s" % exc,
        }
        return result

    last_error: Optional[Exception] = None
    for attempt in range(1, settings.LLM_MAX_RETRIES + 1):
        try:
            start = time.time()
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.2,
                max_tokens=1000,
                timeout=settings.LLM_REQUEST_TIMEOUT_SECONDS,
            )
            raw = extract_text_from_model_response(response)
            result["raw_response"] = raw
            result["model"] = model
            result["mode"] = "real_ai"

            if request_json:
                parsed = parse_model_json(raw)
                if parsed is not None:
                    result["result"] = parsed
                    logger.info(
                        "LLM success feature=%s model=%s attempt=%s duration_ms=%.0f",
                        feature, model, attempt, (time.time() - start) * 1000,
                    )
                    return result
                last_error = ValueError("model returned invalid JSON")
                logger.warning(
                    "Invalid JSON from model feature=%s attempt=%s", feature, attempt
                )
                continue
            else:
                result["result"] = {"text": raw}
                return result

        except Exception as exc:
            last_error = exc
            logger.warning(
                "LLM call failed feature=%s attempt=%s: %s", feature, attempt, exc
            )
            if attempt < settings.LLM_MAX_RETRIES:
                time.sleep(0.5 * attempt)
                continue
            break

    result["mode"] = "fallback"
    result["error"] = {
        "code": "ai_provider_failure",
        "message": "AI provider failed after retries. Last error: %s" % last_error,
    }
    logger.error("LLM provider failure feature=%s: %s", feature, last_error)
    return result


def invoke_with_schema(
    *,
    system_prompt: str,
    user_text: str,
    feature: str,
    schema_class: type,
    image_bytes: Optional[bytes] = None,
    image_content_type: Optional[str] = None,
    model_override: Optional[str] = None,
    require_vision: bool = False,
) -> dict:
    from pydantic import ValidationError

    llm_result = call_llm(
        system_prompt=system_prompt,
        user_text=user_text,
        feature=feature,
        image_bytes=image_bytes,
        image_content_type=image_content_type,
        request_json=True,
        model_override=model_override,
        require_vision=require_vision,
    )

    outcome: dict = {
        "result": None,
        "mode": llm_result["mode"],
        "model": llm_result["model"],
        "raw_response": llm_result.get("raw_response"),
        "error": llm_result.get("error"),
    }

    if outcome["mode"] == "demo":
        demo_base = llm_result.get("result") or {}
        try:
            outcome["result"] = schema_class(**demo_base)
            outcome["error"] = None
        except ValidationError as exc:
            outcome["error"] = {
                "code": "demo_schema_validation_failed",
                "message": "Demo response failed schema validation: %s" % exc,
            }
        return outcome

    if outcome["error"] or llm_result["result"] is None:
        return outcome

    try:
        outcome["result"] = schema_class(**llm_result["result"])
        outcome["error"] = None
    except ValidationError as exc:
        logger.warning(
            "Schema validation failed feature=%s: %s", feature, exc
        )
        outcome["error"] = {
            "code": "schema_validation_failed",
            "message": "AI output did not conform to the expected schema.",
            "details": [
                {"field": ".".join(str(x) for x in err.get("loc", [])), "message": err.get("msg")}
                for err in exc.errors()
            ],
        }
        outcome["result"] = None

    return outcome


def request_metadata(feature: str, mode: str, model: Optional[str] = None) -> dict:
    return {
        "feature": feature,
        "mode": mode,
        "model": model,
        "request_id": str(uuid.uuid4()),
    }
