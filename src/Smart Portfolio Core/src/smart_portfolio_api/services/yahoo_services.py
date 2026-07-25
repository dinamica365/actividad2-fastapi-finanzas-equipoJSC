from __future__ import annotations

import io

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf


def get_one_year_history(ticker: str) -> pd.DataFrame:
    """
    Download one year of historical prices for a ticker.

    Parameters
    ----------
    ticker : str
        Market symbol, e.g. "AAPL".

    Returns
    -------
    pd.DataFrame
        Historical OHLCV data.
    """
    symbol = ticker.strip().upper()
    data = yf.Ticker(symbol).history(period="1y")

    if data.empty:
        raise ValueError(f"No historical data found for ticker '{symbol}'.")

    return data


def build_history_chart_png(ticker: str) -> bytes:
    """
    Build a PNG chart from one year of closing prices.

    Parameters
    ----------
    ticker : str
        Market symbol.

    Returns
    -------
    bytes
        PNG image bytes.
    """
    df = get_one_year_history(ticker)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df.index, df["Close"], linewidth=2)
    ax.set_title(f"{ticker.upper()} - 1 Year Close Price")
    ax.set_xlabel("Date")
    ax.set_ylabel("Close Price")
    ax.grid(True, alpha=0.3)

    buffer = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buffer, format="png", dpi=150)
    plt.close(fig)

    buffer.seek(0)
    return buffer.getvalue()