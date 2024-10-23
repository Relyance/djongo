# Base image
FROM python:3.8-slim AS base

# Set working directory
WORKDIR /app
ENV POETRY_VIRTUALENVS_CREATE=false
# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy only the dependency files
COPY pkg /app

# Install production dependencies
RUN poetry install --no-dev


# Tester stage
FROM base AS tester

WORKDIR /app/tests/test_app

RUN poetry install

CMD ["python", "runtests.py"]

