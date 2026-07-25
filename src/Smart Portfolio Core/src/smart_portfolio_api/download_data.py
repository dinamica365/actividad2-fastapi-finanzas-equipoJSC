"""Command-line utility for exporting Yahoo Finance history to CSV."""

from __future__ import annotations

import argparse
from pathlib import Path

VALID_PERIODS = ("1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download daily market history from Yahoo Finance as CSV."
    )
    parser.add_argument("ticker", help="Yahoo Finance symbol, for example AAPL or BTC-USD")
    parser.add_argument(
        "--period",
        choices=VALID_PERIODS,
        default="5y",
        help="History window to download (default: 5y)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Destination file (default: data/raw/<TICKER>_<PERIOD>.csv)",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    from smart_portfolio_api.services.yahoo_services import get_history

    symbol = args.ticker.strip().upper()
    output = args.output or Path("data/raw") / f"{symbol}_{args.period}.csv"

    history = get_history(symbol, period=args.period)
    output.parent.mkdir(parents=True, exist_ok=True)
    history.to_csv(output, index_label="Date")

    print(f"Saved {len(history)} rows for {symbol} to {output}")


if __name__ == "__main__":
    main()
