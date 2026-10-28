from __future__ import annotations

from fastapi import HTTPException
from fastapi.responses import JSONResponse

from app.schemas.common import ErrorResponse, ResponseMeta


def error_response(
    *,
    code: str,
    message: str,
    status_code: int = 400,
    details=None,
    feature: str = "unknown",
    mode: str = "fallback",
    model=None,
) -> JSONResponse:
    meta = ResponseMeta(feature=feature, mode=mode, model=model)
    body = ErrorResponse(
        success=False,
        error=code,
        message=message,
        details=details,
        meta=meta,
    )
    return JSONResponse(status_code=status_code, content=body.model_dump())


def success_response(*, data, feature: str, mode: str, model=None) -> JSONResponse:
    from app.schemas.common import APIResponse

    meta = ResponseMeta(feature=feature, mode=mode, model=model)
    body = APIResponse(success=True, data=data, meta=meta)
    return JSONResponse(status_code=200, content=body.model_dump())


def raise_api_error(
    *,
    code: str,
    message: str,
    status_code: int = 400,
    feature: str = "unknown",
    mode: str = "fallback",
    model=None,
) -> None:
    raise HTTPException(status_code=status_code, detail={
        "success": False,
        "error": code,
        "message": message,
        "meta": ResponseMeta(feature=feature, mode=mode, model=model).model_dump(),
    })
