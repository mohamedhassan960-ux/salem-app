# Oxygen Medical RAG — Production Container Image (Cloud Run & Docker)
FROM python:3.11-slim

# Set non-interactive environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080 \
    LLM_PROVIDER=gemini \
    GEMINI_MODEL=gemini-2.5-flash

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application directories
COPY data/ /app/data/
COPY outputs/ /app/outputs/
COPY prompts/ /app/prompts/
COPY scripts/ /app/scripts/
COPY api/ /app/api/

# Create non-root user and set permissions
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check using lightweight liveness endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/v1/health || exit 1

# Expose standard Cloud Run port
EXPOSE 8080

# Run FastAPI server with Uvicorn
CMD exec uvicorn api.main:app --host 0.0.0.0 --port ${PORT} --workers 1 --timeout-keep-alive 30
