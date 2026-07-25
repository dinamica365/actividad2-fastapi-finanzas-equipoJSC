from __future__ import annotations

from fastapi import FastAPI

from smart_portfolio_api.routers.charts import router as charts_router
from smart_portfolio_api.routers.forecast import router as forecast_7d

app = FastAPI(
    title="SmartPortfolio API",
    description="API for market charts and portfolio analytics",
    version="0.1.0",
)

app.include_router(charts_router)
app.include_router(forecast_7d)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "SmartPortfolio API is running"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}