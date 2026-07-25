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
