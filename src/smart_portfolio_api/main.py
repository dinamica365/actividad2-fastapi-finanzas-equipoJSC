from __future__ import annotations

from fastapi import FastAPI

from smart_portfolio_api.routers.charts import router as charts_router
from smart_portfolio_api.routers.health import router as health_router
from smart_portfolio_api.routers.market_data import router as market_data_router
from smart_portfolio_api.routers.model import router as model_router
from smart_portfolio_api.routers.predict import router as predict_router

app = FastAPI(
    title="SmartPortfolio API",
    description="API for market charts and portfolio analytics",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(charts_router)
app.include_router(health_router)
app.include_router(market_data_router)
app.include_router(predict_router)
app.include_router(model_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "SmartPortfolio API is running"}
