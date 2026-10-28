from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.common import APIResponse, ErrorResponse


class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role: user or assistant.")
    content: str = Field(..., description="Message content.")


class KnowledgeResponseData(BaseModel):
    response: str = Field(..., description="Assistant response.")
    sources: List[str] = Field(
        default_factory=list, description="Sources referenced, if any."
    )
    disclaimer: str = Field(
        default=(
            "General construction information only. Not a substitute for qualified "
            "professional advice on structural, regulatory, or safety-critical matters."
        ),
        description="Standard knowledge-assistant disclaimer.",
    )


class KnowledgeResponse(APIResponse[KnowledgeResponseData]):
    pass


class KnowledgeError(ErrorResponse):
    pass


class KnowledgeRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User question.")
    history: Optional[List[ChatMessage]] = Field(
        default_factory=list, description="Bounded conversation history."
    )
