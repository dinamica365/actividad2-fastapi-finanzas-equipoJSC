from __future__ import annotations

import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "close",
    "return_1d",
    "return_5d",
    "ma_gap_5",
    "ma_gap_20",
    "volatility_10",
    "volume_change_5d",
]


def build_features(history: pd.DataFrame, horizon: int = 1) -> pd.DataFrame:
    if history.empty:
        raise ValueError("History dataset is empty.")

    if "Close" not in history.columns:
        raise ValueError("History dataset must include a 'Close' column.")

    df = history.copy().sort_index()
    close = df["Close"].astype(float)
    features = pd.DataFrame(index=df.index)
    features["close"] = close
    features["return_1d"] = close.pct_change(1)
    features["return_5d"] = close.pct_change(5)
    features["ma_gap_5"] = close.div(close.rolling(5).mean()) - 1.0
    features["ma_gap_20"] = close.div(close.rolling(20).mean()) - 1.0
    features["volatility_10"] = close.pct_change(1).rolling(10).std()

    if "Volume" in df.columns:
        volume = df["Volume"].astype(float)
        features["volume_change_5d"] = volume.pct_change(5)
    else:
        features["volume_change_5d"] = 0.0

    features["target"] = (close.shift(-horizon) > close).astype(int)
    features = features.replace([np.inf, -np.inf], np.nan).dropna()
    return features


def latest_feature_row(history: pd.DataFrame, horizon: int = 1) -> pd.Series:
    features = build_features(history, horizon=horizon)
    if features.empty:
        raise ValueError("Not enough data to build prediction features.")
    return features.iloc[-1]
