# actividad2-fastapi-finanzas-equipoJSC

API de finanzas con FastAPI, datos cacheados localmente y predicción `up/down`.

## Resumen

El proyecto expone una API pensada para operar con tres activos:

- Bitcoin
- Oro
- Dólar estadounidense

La API:

- sirve un endpoint raíz en `/`
- sirve documentación Swagger en `/docs`
- ofrece `health`, datos de mercado, predicción y metadata del modelo
- usa datos locales en `data/raw/` como fuente principal
- puede recurrir a `yfinance` si se habilita el uso de red y no existe caché local
- entrena un clasificador simple `up/down` con probabilidades

## Estructura

```text
actividad2-fastapi-finanzas-equipoJSC/
├── artifacts/
│   ├── model.joblib
│   └── model_metadata.json
├── data/
│   ├── raw/
│   └── processed/
├── src/
│   └── smart_portfolio_api/
│       ├── __init__.py
│       ├── download_data.py
│       ├── main.py
│       ├── schemas.py
│       ├── routers/
│       │   ├── health.py
│       │   ├── market_data.py
│       │   ├── model.py
│       │   ├── predict.py
│       │   └── charts.py
│       └── services/
│           ├── feature_service.py
│           ├── market_data_service.py
│           ├── model_service.py
│           └── yahoo_services.py
├── tests/
├── Dockerfile
├── pyproject.toml
├── poetry.lock
├── README.md
├── TEAM.md
└── .gitignore
```

## Instalación

```bash
poetry install
```

## Ejecución local

```bash
poetry run python -m smart_portfolio_api.main
```

La documentación Swagger queda disponible en:

```text
http://127.0.0.1:8000/docs
```

## Endpoints

### `GET /health`

Verifica que la API esté viva y que el modelo esté disponible.

Respuesta esperada:

```json
{
  "status": "ok",
  "api_alive": true,
  "model_available": true,
  "model_version": "logistic_momentum_v1",
  "trained_at": "2026-07-25T21:03:36.776413+00:00",
  "details": null
}
```

Si el modelo no puede cargarse, la respuesta cambia a `status: "degraded"` y `model_available: false`.

### `GET /`

Devuelve un mensaje simple para confirmar que la API arrancó.

Ejemplo:

```json
{
  "message": "SmartPortfolio API is running"
}
```

### `GET /market-data/{symbol}`

Devuelve datos recientes y features procesadas para un activo.

Parámetros:

- `symbol`: símbolo del activo
- `use_cached_data`: `true` por defecto; si es `false`, permite usar `yfinance` si no existe caché local

Ejemplo:

```bash
curl "http://127.0.0.1:8000/market-data/BTC-USD?use_cached_data=true"
```

Ejemplo de respuesta:

```json
{
  "symbol": "BTC-USD",
  "source": "cache",
  "records": [
    {
      "date": "2026-07-24",
      "close": 117000.12,
      "return_1d": 0.0123,
      "return_5d": 0.0345,
      "ma_gap_5": 0.0081,
      "ma_gap_20": 0.0217,
      "volatility_10": 0.0184,
      "volume_change_5d": 0.0912
    }
  ]
}
```

### `POST /predict`

Recibe un símbolo y parámetros de inferencia, y retorna una predicción `up/down`.

Contrato de entrada:

```json
{
  "symbol": "BTC-USD",
  "prediction_horizon": 1,
  "use_cached_data": true
}
```

Campos:

- `symbol`: símbolo del activo
- `prediction_horizon`: horizonte de predicción en días
- `use_cached_data`: si es `true`, la API solo usa datos locales

Respuesta esperada:

```json
{
  "symbol": "BTC-USD",
  "prediction": "up",
  "probability_up": 0.63,
  "model_version": "logistic_momentum_v1",
  "prediction_horizon": "next_day"
}
```

Notas:

- el modelo actual soporta `prediction_horizon = 1`
- la salida `prediction` solo puede ser `up` o `down`
- `probability_up` es un valor entre `0.0` y `1.0`

### `GET /model/metadata`

Retorna la metadata local del modelo.

Ejemplo de respuesta:

```json
{
  "model_version": "logistic_momentum_v1",
  "trained_at": "2026-07-25T21:03:36.776413+00:00",
  "symbols_used": ["BTC-USD", "GC=F", "DX-Y.NYB"],
  "metric_name": "accuracy",
  "metric_value": 0.5066,
  "prediction_horizon": 1,
  "feature_columns": [
    "close",
    "return_1d",
    "return_5d",
    "ma_gap_5",
    "ma_gap_20",
    "volatility_10",
    "volume_change_5d"
  ]
}
```

### `GET /charts/history/{ticker}`

Devuelve una imagen PNG con el histórico de cierres de un activo.

Ejemplo:

```bash
curl -o BTC-USD.png "http://127.0.0.1:8000/charts/history/BTC-USD"
```

## Símbolos soportados

El sistema normaliza estos alias:

- `BTC`, `BTC-USD`, `BITCOIN` -> `BTC-USD`
- `GOLD`, `XAU`, `GC=F` -> `GC=F`
- `DOLLAR`, `DXY`, `DX-Y.NYB` -> `DX-Y.NYB`

## Datos locales y reproducibilidad

La API no depende exclusivamente de internet para funcionar.

- Los CSV locales están en `data/raw/`
- La inferencia usa primero la caché local
- Si `use_cached_data=false`, la API puede consultar `yfinance` y guardar el resultado localmente
- Si ya hay datos locales, la API funciona sin red

Los archivos esperados para la evaluación son:

- `data/raw/BTC-USD_5y.csv`
- `data/raw/GC=F_5y.csv`
- `data/raw/DX-Y.NYB_5y.csv`

## Ingesta de datos

El módulo `download_data.py` permite descargar históricos con `yfinance`:

```bash
poetry run python -m smart_portfolio_api.download_data BTC-USD --period 5y
poetry run python -m smart_portfolio_api.download_data "GC=F" --period 5y
poetry run python -m smart_portfolio_api.download_data DX-Y.NYB --period 5y
```

Parámetros útiles:

- `--period`: ventana histórica a descargar, por ejemplo `1y`, `5y` o `max`
- `--output`: ruta de salida personalizada

Ejemplo:

```bash
poetry run python -m smart_portfolio_api.download_data BTC-USD --period 5y --output data/raw/BTC-USD_5y.csv
```

## Modelo

El modelo actual es un clasificador simple `logistic_momentum_v1` entrenado con features derivadas de precios y volumen.

Features usadas:

- `close`
- `return_1d`
- `return_5d`
- `ma_gap_5`
- `ma_gap_20`
- `volatility_10`
- `volume_change_5d`

La metadata se guarda en `artifacts/model_metadata.json` y el modelo serializado en `artifacts/model.joblib`.

## Pruebas

Las pruebas de integración están en `tests/test_api.py` y arrancan un servidor temporal de Uvicorn para validar:

- `GET /health`
- `GET /market-data/{symbol}`
- `GET /model/metadata`
- `POST /predict`

Ejecutar pruebas:

```bash
poetry run python -m unittest discover -s tests -p 'test_*.py'
```

## Docker

La imagen usa:

```bash
docker build -t smart-portfolio-api .
docker run -p 8000:8000 smart-portfolio-api
```

## Notas de implementación

- `GET /docs` está habilitado por defecto por FastAPI.
- El modelo se regenera automáticamente desde caché local si el artefacto no existe o no se puede cargar.
- El endpoint de predicción responde en formato validado por Pydantic, no con estructuras libres.
