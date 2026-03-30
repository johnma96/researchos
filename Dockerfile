FROM python:3.11-slim AS base

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install production dependencies
RUN uv sync --no-dev --frozen

# Copy source code
COPY src/ src/
COPY configs/ configs/

# Expose API port
EXPOSE 8000

# Run API server
CMD ["uv", "run", "uvicorn", "researchos.infrastructure.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
