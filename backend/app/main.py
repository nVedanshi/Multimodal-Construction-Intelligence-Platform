from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import init_db
from app.api.routers import health, safety, crack, planning, valuation, knowledge, daily, weather
from app.schemas.common import ErrorResponse, ResponseMeta

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Multimodal Construction Intelligence Platform backend.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN, "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return consistent error envelope for Pydantic validation errors."""
    details = []
    for err in exc.errors():
        details.append(
            {
                "field": ".".join(str(x) for x in err.get("loc", [])),
                "message": err.get("msg", "Invalid value"),
            }
        )
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="validation_error",
            message="Request validation failed.",
            details=details,
            meta=ResponseMeta(feature="unknown", mode="fallback"),
        ).model_dump(),
    )


@app.on_event("startup")
def _startup():
    init_db()


app.include_router(health.router, prefix="/api")
app.include_router(safety.router, prefix="/api")
app.include_router(crack.router, prefix="/api")
app.include_router(planning.router, prefix="/api")
app.include_router(valuation.router, prefix="/api")
app.include_router(knowledge.router, prefix="/api")
app.include_router(daily.router, prefix="/api")
app.include_router(weather.router, prefix="/api")


@app.get("/api", tags=["Root"])
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "demo_mode": settings.DEMO_MODE,
        "vision_available": settings.vision_available,
        "docs": "/docs",
    }
