from __future__ import annotations

from fastapi import APIRouter

from smart_portfolio_api.schemas import ModelMetadataResponse
from smart_portfolio_api.services.model_service import get_model_metadata_response

router = APIRouter(prefix="/model", tags=["model"])


@router.get("/metadata", response_model=ModelMetadataResponse)
def model_metadata() -> ModelMetadataResponse:
    return ModelMetadataResponse(**get_model_metadata_response())
