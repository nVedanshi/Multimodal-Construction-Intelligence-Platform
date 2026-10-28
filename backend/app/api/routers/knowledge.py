from __future__ import annotations

from fastapi import APIRouter

from app.services.knowledge_service import answer_question
from app.schemas.knowledge import KnowledgeRequest, KnowledgeResponseData
from app.utils.responses import error_response, success_response

router = APIRouter()


@router.post("/knowledge/ask", tags=["Construction Knowledge Assistant"])
def knowledge_ask_endpoint(request: KnowledgeRequest):
    """Answer a construction-related question.

    Accepts a user question plus bounded conversation history. Returns an
    assistant response with sources and disclaimer.
    """
    try:
        result = answer_question(message=request.message, history=request.history)
    except Exception as exc:
        return error_response(
            code="knowledge_failed",
            message="Knowledge assistant failed: %s" % exc,
            status_code=500,
            feature="construction_knowledge_assistant",
            mode="fallback",
        )

    if result.get("error"):
        return error_response(
            code=result["error"].get("code", "knowledge_failed"),
            message=result["error"].get("message", "Knowledge assistant unavailable."),
            status_code=502,
            feature="construction_knowledge_assistant",
            mode=result.get("mode", "fallback"),
            model=result.get("model"),
        )

    data = result["result"]
    if not isinstance(data, KnowledgeResponseData):
        return error_response(
            code="invalid_response",
            message="Knowledge assistant returned an invalid response.",
            status_code=500,
            feature="construction_knowledge_assistant",
            mode="fallback",
        )

    return success_response(
        data=data.model_dump(),
        feature="construction_knowledge_assistant",
        mode=result.get("mode", "demo"),
        model=result.get("model"),
    )
