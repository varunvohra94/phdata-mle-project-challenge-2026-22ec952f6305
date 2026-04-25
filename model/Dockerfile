# Stage 1: Build stage
FROM ghcr.io/astral-sh/uv:latest AS uv_bin
FROM python:3.13-slim AS builder

WORKDIR /app
COPY --from=uv_bin /uv /bin/uv

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=0

# Install dependencies into a virtualenv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache --no-dev --no-install-project

# Stage 2: Runtime stage
FROM python:3.13-slim

WORKDIR /app

# Copy the virtualenv from the builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy the create_model script and data
COPY create_model.py .
COPY data ./data

CMD ["python", "create_model.py"]