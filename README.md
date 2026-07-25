# actividad2-fastapi-finanzas-equipoJSC

API de finanzas con FastAPI, datos cacheados localmente y predicción up/down.

## Estructura

```text
actividad2-fastapi-finanzas-equipoJSC/
├── data/
│   ├── raw/
│   └── processed/
├── src/
│   └── smart_portfolio_api/
│       ├── main.py
│       ├── download_data.py
│       ├── schemas.py
│       ├── routers/
│       └── services/
├── artifacts/
│   ├── model.joblib
│   └── model_metadata.json
├── tests/
├── reports/
├── Dockerfile
├── pyproject.toml
├── poetry.lock
├── README.md
├── TEAM.md
└── .gitignore
```

## Uso

```bash
poetry install
poetry run python -m smart_portfolio_api.main
```

## Smart Portfolio API

La API principal vive en `src/smart_portfolio_api` y expone:

- `GET /health`
- `GET /market-data/{symbol}`
- `POST /predict`
- `GET /model/metadata`
- `GET /docs`

La documentación Swagger está disponible en `/docs`.

## Contrato de predicción

Ejemplo de request:

```json
{
  "symbol": "BTC-USD",
  "prediction_horizon": 1,
  "use_cached_data": true
}
```

Ejemplo de respuesta:

```json
{
  "symbol": "BTC-USD",
  "prediction": "up",
  "probability_up": 0.63,
  "model_version": "logistic_momentum_v1",
  "prediction_horizon": "next_day"
}
```

### Descargar datos históricos en CSV

Desde la raíz del proyecto, descarga cinco años de datos diarios para Bitcoin, oro y el índice del dólar estadounidense con:

```bash
poetry run python -m smart_portfolio_api.download_data BTC-USD --period 5y
poetry run python -m smart_portfolio_api.download_data "GC=F" --period 5y
poetry run python -m smart_portfolio_api.download_data DX-Y.NYB --period 5y
```

Los símbolos corresponden a `BTC-USD` (Bitcoin/dólar), `GC=F` (futuros del oro) y `DX-Y.NYB` (índice del dólar estadounidense). Los archivos se guardan automáticamente en `data/raw/` con nombres como `BTC-USD_5y.csv`. Usa `--output ruta/archivo.csv` para elegir otra ubicación o reemplaza `5y` por un período admitido, por ejemplo `1y`, `10y` o `max`.

## Reproducibilidad

La API usa primero los CSV locales en `data/raw/`. Si no hay datos cacheados y `use_cached_data=false`, puede recurrir a `yfinance` y guardar la copia local. Esto permite ejecutar la API y las pruebas sin depender exclusivamente de internet.
