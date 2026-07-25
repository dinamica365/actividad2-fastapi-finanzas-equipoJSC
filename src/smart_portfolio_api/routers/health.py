from __future__ import annotations

from fastapi import APIRouter

from smart_portfolio_api.schemas import HealthResponse
from smart_portfolio_api.services.model_service import load_model

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    try:
        model = load_model()
        return HealthResponse(
            status="ok",
            api_alive=True,
            model_available=True,
            model_version=model.model_version,
            trained_at=model.trained_at,
        )
    except Exception as exc:
        return HealthResponse(
            status="degraded",
            api_alive=True,
            model_available=False,
            details=str(exc),
        )
