FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Install uv for dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies using uv
RUN uv pip install --system -r pyproject.toml

# Copy notebook files
COPY *.py ./

# Expose marimo default port
EXPOSE 3001

# Run marimo in production mode (read-only notebooks)
CMD ["marimo", "run", "nba_analysis.py", "--host", "0.0.0.0", "--port", "3001"]
