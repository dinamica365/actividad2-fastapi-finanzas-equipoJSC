from __future__ import annotations

from pathlib import Path
from typing import Final

import pandas as pd
import yfinance as yf

RAW_DATA_DIR: Final = Path("data/raw")
DEFAULT_PERIOD: Final = "5y"
DEFAULT_LOOKBACK_ROWS: Final = 30

SYMBOL_ALIASES: Final[dict[str, str]] = {
    "BTC": "BTC-USD",
    "BTC-USD": "BTC-USD",
    "BITCOIN": "BTC-USD",
    "GOLD": "GC=F",
    "XAU": "GC=F",
    "GC=F": "GC=F",
    "DOLLAR": "DX-Y.NYB",
    "DXY": "DX-Y.NYB",
    "DX-Y.NYB": "DX-Y.NYB",
}


def normalize_symbol(symbol: str) -> str:
    value = symbol.strip().upper()
    if not value:
        raise ValueError("Symbol must not be empty.")
    return SYMBOL_ALIASES.get(value, value)


def local_history_path(symbol: str, period: str = DEFAULT_PERIOD) -> Path:
    normalized = normalize_symbol(symbol)
    return RAW_DATA_DIR / f"{normalized}_{period}.csv"


def load_local_history(symbol: str, period: str = DEFAULT_PERIOD) -> pd.DataFrame:
    path = local_history_path(symbol, period)
    if not path.exists():
        raise FileNotFoundError(f"Cached dataset not found for symbol '{normalize_symbol(symbol)}'.")

    data = pd.read_csv(path, parse_dates=["Date"])
    if data.empty:
        raise ValueError(f"Cached dataset for '{normalize_symbol(symbol)}' is empty.")

    data = data.set_index("Date").sort_index()
    return data


def download_history(symbol: str, period: str = DEFAULT_PERIOD, persist: bool = True) -> pd.DataFrame:
    normalized = normalize_symbol(symbol)
    data = yf.Ticker(normalized).history(period=period, interval="1d")
    if data.empty:
        raise ValueError(f"No historical data found for ticker '{normalized}'.")

    if persist:
        path = local_history_path(normalized, period)
        path.parent.mkdir(parents=True, exist_ok=True)
        data.to_csv(path, index_label="Date")

    return data


def load_history(symbol: str, use_cached_data: bool = True, period: str = DEFAULT_PERIOD) -> tuple[pd.DataFrame, str]:
    normalized = normalize_symbol(symbol)
    path = local_history_path(normalized, period)

    if path.exists():
        return load_local_history(normalized, period), "cache"

    if use_cached_data:
        raise FileNotFoundError(f"Cached dataset not found for symbol '{normalized}'.")

    return download_history(normalized, period=period, persist=True), "yfinance"


def get_recent_market_data(
    symbol: str,
    use_cached_data: bool = True,
    period: str = DEFAULT_PERIOD,
    lookback: int = DEFAULT_LOOKBACK_ROWS,
) -> tuple[pd.DataFrame, str]:
    history, source = load_history(symbol, use_cached_data=use_cached_data, period=period)
    return history.tail(lookback).copy(), source
