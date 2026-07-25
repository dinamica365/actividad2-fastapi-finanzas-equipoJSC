from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import math
import pickle

import numpy as np

from smart_portfolio_api.services.feature_service import FEATURE_COLUMNS, build_features, latest_feature_row
from smart_portfolio_api.services.market_data_service import (
    DEFAULT_PERIOD,
    load_history,
    normalize_symbol,
)

ARTIFACTS_DIR = Path("artifacts")
MODEL_PATH = ARTIFACTS_DIR / "model.joblib"
METADATA_PATH = ARTIFACTS_DIR / "model_metadata.json"
SUPPORTED_SYMBOLS = ["BTC-USD", "GC=F", "DX-Y.NYB"]
MODEL_VERSION = "logistic_momentum_v1"


@dataclass
class SimpleUpDownModel:
    feature_columns: list[str]
    feature_means: list[float]
    feature_stds: list[float]
    weights: list[float]
    model_version: str
    trained_at: str
    symbols_used: list[str]
    metric_name: str
    metric_value: float
    prediction_horizon: int

    def _vectorize(self, features: dict[str, float]) -> np.ndarray:
        values = np.array([float(features[column]) for column in self.feature_columns], dtype=float)
        means = np.array(self.feature_means, dtype=float)
        stds = np.array(self.feature_stds, dtype=float)
        stds = np.where(stds == 0.0, 1.0, stds)
        return (values - means) / stds

    def predict_probability_up(self, features: dict[str, float]) -> float:
        vector = self._vectorize(features)
        weights = np.array(self.weights[1:], dtype=float)
        intercept = float(self.weights[0])
        z = intercept + float(np.dot(vector, weights))
        probability = 1.0 / (1.0 + math.exp(-z))
        return float(probability)

    def predict_label(self, features: dict[str, float]) -> tuple[str, float]:
        probability_up = self.predict_probability_up(features)
        prediction = "up" if probability_up >= 0.5 else "down"
        return prediction, probability_up


def _sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-values))


def _train_logistic_regression(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    weights = np.zeros(X.shape[1] + 1, dtype=float)
    learning_rate = 0.1
    regularization = 0.001

    for _ in range(1200):
        linear = weights[0] + X @ weights[1:]
        predictions = _sigmoid(linear)
        error = predictions - y
        gradient_intercept = float(error.mean())
        gradient_weights = (X.T @ error) / len(X) + regularization * weights[1:]
        weights[0] -= learning_rate * gradient_intercept
        weights[1:] -= learning_rate * gradient_weights

    return weights


def _build_training_frames(horizon: int) -> tuple[list[np.ndarray], list[np.ndarray], list[np.ndarray], list[np.ndarray]]:
    train_features: list[np.ndarray] = []
    train_labels: list[np.ndarray] = []
    val_features: list[np.ndarray] = []
    val_labels: list[np.ndarray] = []

    for symbol in SUPPORTED_SYMBOLS:
        history, _ = load_history(symbol, use_cached_data=True, period=DEFAULT_PERIOD)
        feature_frame = build_features(history, horizon=horizon)
        if feature_frame.empty:
            continue

        split_index = max(int(len(feature_frame) * 0.8), 1)
        train_frame = feature_frame.iloc[:split_index]
        val_frame = feature_frame.iloc[split_index:]

        train_features.append(train_frame[FEATURE_COLUMNS].to_numpy(dtype=float))
        train_labels.append(train_frame["target"].to_numpy(dtype=int))
        if not val_frame.empty:
            val_features.append(val_frame[FEATURE_COLUMNS].to_numpy(dtype=float))
            val_labels.append(val_frame["target"].to_numpy(dtype=int))

    if not train_features:
        raise ValueError("No training data available.")

    return train_features, train_labels, val_features, val_labels


def train_model(horizon: int = 1) -> SimpleUpDownModel:
    train_features, train_labels, val_features, val_labels = _build_training_frames(horizon)

    X_train = np.vstack(train_features)
    y_train = np.concatenate(train_labels)

    feature_means = X_train.mean(axis=0)
    feature_stds = X_train.std(axis=0)
    feature_stds = np.where(feature_stds == 0.0, 1.0, feature_stds)
    X_train_scaled = (X_train - feature_means) / feature_stds

    weights = _train_logistic_regression(X_train_scaled, y_train)

    if val_features:
        X_val = np.vstack(val_features)
        y_val = np.concatenate(val_labels)
        X_val_scaled = (X_val - feature_means) / feature_stds
        probability_up = _sigmoid(weights[0] + X_val_scaled @ weights[1:])
        predictions = (probability_up >= 0.5).astype(int)
        metric_value = float((predictions == y_val).mean())
    else:
        probability_up = _sigmoid(weights[0] + X_train_scaled @ weights[1:])
        predictions = (probability_up >= 0.5).astype(int)
        metric_value = float((predictions == y_train).mean())

    model = SimpleUpDownModel(
        feature_columns=FEATURE_COLUMNS,
        feature_means=feature_means.tolist(),
        feature_stds=feature_stds.tolist(),
        weights=weights.tolist(),
        model_version=MODEL_VERSION,
        trained_at=datetime.now(timezone.utc).isoformat(),
        symbols_used=SUPPORTED_SYMBOLS,
        metric_name="accuracy",
        metric_value=metric_value,
        prediction_horizon=horizon,
    )

    save_model(model)
    save_metadata(model)
    return model


def save_model(model: SimpleUpDownModel) -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    with MODEL_PATH.open("wb") as handle:
        pickle.dump(model, handle)


def save_metadata(model: SimpleUpDownModel) -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    metadata = asdict(model)
    with METADATA_PATH.open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2, sort_keys=True)


def load_model() -> SimpleUpDownModel:
    if MODEL_PATH.exists():
        try:
            with MODEL_PATH.open("rb") as handle:
                model = pickle.load(handle)
            if isinstance(model, SimpleUpDownModel):
                return model
        except Exception:
            pass

    return train_model()


def load_metadata() -> dict[str, Any]:
    if METADATA_PATH.exists():
        try:
            with METADATA_PATH.open("r", encoding="utf-8") as handle:
                metadata = json.load(handle)
            if metadata:
                return metadata
        except Exception:
            pass

    model = load_model()
    return asdict(model)


def predict_symbol(symbol: str, horizon: int = 1, use_cached_data: bool = True) -> dict[str, Any]:
    model = load_model()
    if horizon != model.prediction_horizon:
        raise ValueError(
            f"The current model only supports prediction_horizon={model.prediction_horizon}."
        )

    normalized = normalize_symbol(symbol)
    history, _ = load_history(normalized, use_cached_data=use_cached_data, period=DEFAULT_PERIOD)
    features = latest_feature_row(history, horizon=horizon)
    payload = {column: float(features[column]) for column in model.feature_columns}
    prediction, probability_up = model.predict_label(payload)

    return {
        "symbol": normalized,
        "prediction": prediction,
        "probability_up": probability_up,
        "model_version": model.model_version,
        "prediction_horizon": "next_day" if horizon == 1 else f"next_{horizon}_days",
    }


def model_is_ready() -> bool:
    try:
        load_model()
        return True
    except Exception:
        return False


def get_model_metadata_response() -> dict[str, Any]:
    metadata = load_metadata()
    return {
        "model_version": metadata["model_version"],
        "trained_at": metadata["trained_at"],
        "symbols_used": metadata["symbols_used"],
        "metric_name": metadata["metric_name"],
        "metric_value": float(metadata["metric_value"]),
        "prediction_horizon": int(metadata["prediction_horizon"]),
        "feature_columns": metadata["feature_columns"],
    }
