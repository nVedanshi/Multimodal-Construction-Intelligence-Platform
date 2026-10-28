from __future__ import annotations

from typing import List, Optional

from app.services.ai_service import (
    call_llm,
    invoke_with_schema,
    request_metadata,
)
from app.schemas.knowledge import (
    KnowledgeRequest,
    KnowledgeResponseData,
    ChatMessage,
)

FEATURE = "construction_knowledge_assistant"

SYSTEM_PROMPT = (
    "You are a construction knowledge assistant. Answer questions about "
    "construction materials, building practices, terminology, planning, basic "
    "estimation methods, maintenance, and safety procedures. Keep responses "
    "concise, informative, and actionable. Explain assumptions where relevant "
    "and recommend qualified professional advice for structural, regulatory, "
    "or safety-critical decisions. If the user asks about documents they have "
    "not provided, say you have not seen those documents. Return ONLY a JSON "
    "object with these exact fields: \"response\" (string: the assistant's "
    "answer), \"sources\" (array of strings: sources referenced, empty array "
    "if none), \"disclaimer\" (string: standard disclaimer about consulting "
    "qualified professionals). Output format: json"
)


def _demo_result(message: str) -> KnowledgeResponseData:
    return KnowledgeResponseData(
        response=(
            "Demo response: I can help with construction-related questions. "
            "Your question was: '%s'. Configure GROQ_API_KEY and disable "
            "DEMO_MODE for live AI assistance." % message
        ),
        sources=[],
    )


def _fallback_result(message: str, limitation: str) -> KnowledgeResponseData:
    return KnowledgeResponseData(
        response=(
            "Knowledge assistant unavailable: %s. Your question was: '%s'. "
            "Please consult a qualified construction professional for "
            "safety-critical or structural decisions." % (limitation, message)
        ),
        sources=[],
    )


def answer_question(
    *,
    message: str,
    history: Optional[List[dict]] = None,
) -> dict:
    context = ""
    if history:
        recent = history[-6:]
        lines = []
        for item in recent:
            role = item.get("role", "user")
            content = item.get("content", "")
            lines.append("%s: %s" % (role.capitalize(), content))
        context = "Recent conversation:\n%s\n\n" % "\n".join(lines)

    user_text = context + "User question: %s" % message

    result = invoke_with_schema(
        system_prompt=SYSTEM_PROMPT,
        user_text=user_text,
        feature=FEATURE,
        schema_class=KnowledgeResponseData,
    )

    if result["mode"] == "demo":
        result["result"] = _demo_result(message)
        result["error"] = None
    elif result["error"] or result["result"] is None:
        limitation = (
            result["error"]["message"]
            if result["error"]
            else "Knowledge assistant unavailable."
        )
        result["result"] = _fallback_result(message, limitation)
        result["mode"] = "fallback"
        result["error"] = None

    result["meta"] = request_metadata(FEATURE, result["mode"], result["model"])
    return result
