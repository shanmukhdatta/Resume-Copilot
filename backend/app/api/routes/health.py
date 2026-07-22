"""Health check endpoint."""
from fastapi import APIRouter

from app.config import get_settings
from app.schemas.api_schema import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", app_name=settings.APP_NAME)
