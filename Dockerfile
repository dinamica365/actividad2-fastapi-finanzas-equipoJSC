FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock README.md ./
COPY src ./src
COPY data ./data
COPY artifacts ./artifacts

RUN poetry install --no-interaction --no-ansi

EXPOSE 8080

CMD ["sh", "-c", "uvicorn smart_portfolio_api.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
