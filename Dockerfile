# Oxygen Medical RAG — Production Lightweight Container Image
FROM python:3.11-slim

# Set non-interactive environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860 \
    EMBEDDING_PROVIDER=gemini \
    EMBEDDING_MODEL=models/gemini-embedding-2 \
    LLM_PROVIDER=gemini \
    GEMINI_MODEL=gemini-2.5-flash

WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy lightweight requirements and install python packages
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
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/v1/health || exit 1

# Expose standard container port (7860 default for Hugging Face / Koyeb / Render)
EXPOSE 7860

# Run FastAPI server with Uvicorn
CMD exec uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-7860} --workers 1 --timeout-keep-alive 30
