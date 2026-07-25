from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from smart_portfolio_api.services.yahoo_services import build_history_chart_png

router = APIRouter(prefix="/charts", tags=["charts"])


@router.get("/history/{ticker}")
def get_history_chart(ticker: str) -> StreamingResponse:
    """
    Return a PNG chart with one year of historical prices.
    """
    try:
        image_bytes = build_history_chart_png(ticker)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error generating chart.") from exc

    return StreamingResponse(
        content=iter([image_bytes]),
        media_type="image/png",
        headers={
            "Content-Disposition": f'inline; filename="{ticker.upper()}_1y.png"'
        },
    )