# Root-level Dockerfile for Hugging Face
# This tells HF how to build the nested backend

# Build stage
FROM python:3.12-slim as builder

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy backend files from the subdirectory
COPY phase3-todo-ai-chatbot/backend/pyproject.toml phase3-todo-ai-chatbot/backend/uv.lock ./

# Install dependencies
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install --no-cache -r pyproject.toml

# Final stage
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment
COPY --from=builder /app/.venv /app/.venv

# Copy source code from the subdirectory
COPY phase3-todo-ai-chatbot/backend/src /app/src
COPY phase3-todo-ai-chatbot/backend/alembic /app/alembic
COPY phase3-todo-ai-chatbot/backend/alembic.ini /app/
COPY phase3-todo-ai-chatbot/backend/README.md /app/

# Set environment
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PORT=7860

EXPOSE 7860

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]
