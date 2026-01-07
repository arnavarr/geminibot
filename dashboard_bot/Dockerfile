# Dashboard Bot Dockerfile
# Multi-stage build for production deployment

FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN useradd --create-home --shell /bin/bash agent

# Copy installed packages from builder
COPY --from=builder /root/.local /home/agent/.local

# Ensure scripts in .local are usable
ENV PATH=/home/agent/.local/bin:$PATH

# Copy application code
COPY --chown=agent:agent . .

# Create necessary directories
RUN mkdir -p /app/artifacts /app/openspec

# Switch to non-root user
USER agent

# Default command
CMD ["python", "agent.py", "Create today's daily note with my tasks and emails"]
