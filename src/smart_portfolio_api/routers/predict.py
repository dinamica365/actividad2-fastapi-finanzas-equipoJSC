from __future__ import annotations

from fastapi import APIRouter, HTTPException

from smart_portfolio_api.schemas import PredictionRequest, PredictionResponse
from smart_portfolio_api.services.model_service import predict_symbol

router = APIRouter(tags=["predict"])


@router.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest) -> PredictionResponse:
    try:
        payload = predict_symbol(
            symbol=request.symbol,
            horizon=request.prediction_horizon,
            use_cached_data=request.use_cached_data,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Prediction failed.") from exc

    return PredictionResponse(**payload)
