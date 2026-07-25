# actividad2-fastapi-finanzas-equipoJSC

Estructura mínima del proyecto para FastAPI y finanzas.

## Estructura

```text
actividad2-fastapi-finanzas-equipoXX/
├── data/
│   ├── raw/
│   └── processed/
├── src/
│   └── financial_api/
│       ├── api.py
│       ├── schemas.py
│       ├── data.py
│       ├── features.py
│       ├── train.py
│       └── predict.py
│   └── Smart Portfolio Core/
│       └── src/
│           └── smart_portfolio_api/
│               ├── main.py
│               ├── routers/
│               └── services/
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
poetry run python -m financial_api.api
```

## Smart Portfolio Core

La carpeta `src/Smart Portfolio Core` contiene una API adicional para consultar Yahoo Finance y generar pronósticos simples. Su entrada principal está en `src/Smart Portfolio Core/src/smart_portfolio_api/main.py`.
