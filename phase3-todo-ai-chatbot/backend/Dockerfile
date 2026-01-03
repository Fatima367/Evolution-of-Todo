# Build stage: installer
FROM python:3.12-slim as builder

WORKDIR /app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual environment
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install --no-cache -r pyproject.toml

# Final stage: Runner
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy source code and other necessary files
COPY src /app/src
COPY alembic /app/alembic
COPY alembic.ini /app/
COPY README.md /app/

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PORT=7860

# Metadata for Hugging Face
LABEL maintainer="Evolution of Todo"
LABEL description="Todo AI Chatbot Backend for Hugging Face Spaces"

# Expose the default HF Spaces port
EXPOSE 7860

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]
