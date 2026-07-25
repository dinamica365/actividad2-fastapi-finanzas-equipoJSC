from __future__ import annotations

from fastapi import APIRouter, HTTPException

from smart_portfolio_api.schemas import MarketDataRecord, MarketDataResponse
from smart_portfolio_api.services.feature_service import build_features
from smart_portfolio_api.services.market_data_service import get_recent_market_data, normalize_symbol

router = APIRouter(prefix="/market-data", tags=["market-data"])


@router.get("/{symbol}", response_model=MarketDataResponse)
def get_market_data(symbol: str, use_cached_data: bool = True) -> MarketDataResponse:
    normalized = normalize_symbol(symbol)
    try:
        history, source = get_recent_market_data(normalized, use_cached_data=use_cached_data)
        features = build_features(history, horizon=1).tail(len(history))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    records = []
    for index, row in features.iterrows():
        records.append(
            MarketDataRecord(
                date=index.date().isoformat(),
                close=float(row["close"]),
                return_1d=float(row["return_1d"]),
                return_5d=float(row["return_5d"]),
                ma_gap_5=float(row["ma_gap_5"]),
                ma_gap_20=float(row["ma_gap_20"]),
                volatility_10=float(row["volatility_10"]),
                volume_change_5d=float(row["volume_change_5d"]),
            )
        )

    return MarketDataResponse(symbol=normalized, source=source, records=records)
