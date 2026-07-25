# actividad2-fastapi-finanzas-equipoJSC

Estructura mínima del proyecto para FastAPI y finanzas.

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

La API principal vive en `src/smart_portfolio_api`. Incluye endpoints para charts, forecast y la base para los endpoints de salud, mercado, predicción y metadata del modelo.

### Descargar datos históricos en CSV

Desde la raíz del proyecto, descarga cinco años de datos diarios para Bitcoin, oro y el índice del dólar estadounidense con:

```bash
poetry run python -m smart_portfolio_api.download_data BTC-USD --period 5y
poetry run python -m smart_portfolio_api.download_data "GC=F" --period 5y
poetry run python -m smart_portfolio_api.download_data DX-Y.NYB --period 5y
```

Los símbolos corresponden a `BTC-USD` (Bitcoin/dólar), `GC=F` (futuros del oro) y `DX-Y.NYB` (índice del dólar estadounidense). Los archivos se guardan automáticamente en `data/raw/` con nombres como `BTC-USD_5y.csv`. Usa `--output ruta/archivo.csv` para elegir otra ubicación o reemplaza `5y` por un período admitido, por ejemplo `1y`, `10y` o `max`.
