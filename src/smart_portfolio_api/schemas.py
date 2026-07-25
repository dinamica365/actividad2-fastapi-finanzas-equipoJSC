from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PredictionRequest(BaseModel):
    symbol: str = Field(..., min_length=1, description="Market symbol, for example BTC-USD.")
    prediction_horizon: int = Field(
        default=1,
        ge=1,
        le=1,
        description="Forecast horizon in days. The current model supports next-day prediction only.",
    )
    use_cached_data: bool = Field(
        default=True,
        description="If true, only use local cached CSV data and never hit yfinance.",
    )

    model_config = ConfigDict(extra="forbid")


class PredictionResponse(BaseModel):
    symbol: str
    prediction: Literal["up", "down"]
    probability_up: float
    model_version: str
    prediction_horizon: str


class MarketDataRequest(BaseModel):
    symbol: str
    use_cached_data: bool = True

    model_config = ConfigDict(extra="forbid")


class MarketDataRecord(BaseModel):
    date: str
    close: float
    return_1d: float | None = None
    return_5d: float | None = None
    ma_gap_5: float | None = None
    ma_gap_20: float | None = None
    volatility_10: float | None = None
    volume_change_5d: float | None = None


class MarketDataResponse(BaseModel):
    symbol: str
    source: Literal["cache", "yfinance"]
    records: list[MarketDataRecord]


class ModelMetadataResponse(BaseModel):
    model_version: str
    trained_at: str
    symbols_used: list[str]
    metric_name: str
    metric_value: float
    prediction_horizon: int
    feature_columns: list[str]


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    api_alive: bool
    model_available: bool
    model_version: str | None = None
    trained_at: str | None = None
    details: str | None = None
