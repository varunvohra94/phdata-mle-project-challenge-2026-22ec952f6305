# Stage 1: Build stage
FROM ghcr.io/astral-sh/uv:latest AS uv_bin
FROM python:3.13-slim AS builder

WORKDIR /app
COPY --from=uv_bin /uv /bin/uv

# 1. Set uv environment variables
# UV_LINK_MODE=copy prevents broken symlinks in the final image
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=0

# Install dependencies into a virtualenv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache --no-dev --no-install-project

# Stage 2: Runtime stage
FROM python:3.13-slim

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Copy the virtualenv from the builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app:/app/src

COPY src ./src
COPY data ./data
COPY model ./model

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]