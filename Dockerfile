FROM python:3.11-slim AS base

WORKDIR /app
ENV POETRY_VIRTUALENVS_CREATE=false

RUN pip install --no-cache-dir poetry

COPY pkg /app

RUN poetry install --without dev


FROM base AS tester

WORKDIR /app/tests/test_app

RUN poetry install

CMD ["python", "runtests.py"]

