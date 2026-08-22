"""
FastAPI Application Entry Point — Medical RAG: Oxygen (أوكسجين)
Provides stable HTTP endpoints, request tracking, configurable authentication, bounded lifecycle, and safe error handling.

Endpoints:
- POST /api/v1/chat    : Full grounded clinical dialogue or deterministic abstention
- GET  /api/v1/health  : Cheap liveness check (0 RAG calls, 0 models loaded)
- GET  /api/v1/ready   : Readiness probe verifying pipeline and vector store
- GET  /api/v1/meta    : Safe public metadata (No internal paths/secrets)
"""

from __future__ import annotations

import os
import sys
import uuid
import time
import logging
from typing import Optional

# Ensure scripts path is reachable
_SCRIPTS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
if _SCRIPTS_PATH not in sys.path:
    sys.path.insert(0, _SCRIPTS_PATH)

from fastapi import FastAPI, Request, Response, HTTPException, Security, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader, APIKeyQuery
from fastapi.responses import JSONResponse

from api.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    RAGHealthResponse,
    ReadyResponse,
    MetaResponse,
)
from api.rag_service import get_rag_service

# Structured Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [request_id=%(request_id)s] %(message)s",
)

class RequestIdFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, "request_id"):
            record.request_id = "system"
        return True

root_logger = logging.getLogger()
for handler in root_logger.handlers:
    handler.addFilter(RequestIdFilter())

logger = logging.getLogger("oxygen.api")

# Initialize FastAPI App
app = FastAPI(
    title="Oxygen Medical RAG API",
    description="Grounded clinical question-answering and deterministic circuit breaker for WHO Tobacco Cessation Guideline (2024).",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
# Supports explicit comma-separated list or '*' for development/tunnel UI clients
raw_cors = os.environ.get("CORS_ORIGINS") or os.environ.get("CORS_ALLOWED_ORIGINS") or "*"
if raw_cors.strip() == "*":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    ALLOWED_ORIGINS = [
        origin.strip()
        for origin in raw_cors.split(",")
        if origin.strip()
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Authentication Configuration (Header-Only: X-API-Key. Strictly NO query param auth)
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
AUTH_ENABLED_ENV = os.environ.get("AUTH_ENABLED", "false").strip().lower() in {"true", "1", "yes"}
EXPECTED_API_KEY = os.environ.get("OXYGEN_API_KEY") or os.environ.get("API_SECRET_KEY")


async def verify_authentication(
    header_key: Optional[str] = Security(API_KEY_HEADER),
) -> bool:
    """
    Verifies API Key from X-API-Key header.
    Enforced if AUTH_ENABLED=true or if EXPECTED_API_KEY is defined and AUTH_ENABLED is not explicitly false.
    Strictly forbids API keys in query parameters to prevent leakage in URLs, access logs, and proxies.
    """
    # Auth is active if AUTH_ENABLED_ENV is True or AUTH_ENABLED env var is set to true/1/yes
    auth_enabled = (
        AUTH_ENABLED_ENV
        or os.environ.get("AUTH_ENABLED", "false").strip().lower() in {"true", "1", "yes"}
    )
    
    if not auth_enabled:
        return True
    
    if not EXPECTED_API_KEY:
        # Auth requested but no key configured on server -> 500 configuration safety
        logger.error("Authentication is enabled but OXYGEN_API_KEY/API_SECRET_KEY is not set.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server authentication configuration error.",
        )

    if not header_key or header_key != EXPECTED_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key in X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return True


@app.middleware("http")
async def request_lifecycle_middleware(request: Request, call_next):
    """Injects X-Request-ID and tracks total HTTP roundtrip latency."""
    raw_req_id = request.headers.get("X-Request-ID")
    request_id = raw_req_id if (raw_req_id and len(raw_req_id) <= 64) else f"req_{uuid.uuid4().hex[:12]}"
    
    # Attach to request state
    request.state.request_id = request_id
    t0 = time.perf_counter()

    try:
        response: Response = await call_next(request)
        t1 = time.perf_counter()
        latency_ms = round((t1 - t0) * 1000.0, 2)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = str(latency_ms)
        return response
    except Exception as exc:
        t1 = time.perf_counter()
        latency_ms = round((t1 - t0) * 1000.0, 2)
        logger.error(f"Unhandled exception during request: {exc}", extra={"request_id": request_id})
        return JSONResponse(
            status_code=500,
            content={
                "request_id": request_id,
                "error": "Internal server error occurred while processing clinical request.",
                "latency_ms": latency_ms,
            },
            headers={"X-Request-ID": request_id},
        )


# ── 1. POST /api/v1/chat ───────────────────────────────────────────────────────
@app.post(
    "/api/v1/chat",
    response_model=ChatResponse,
    summary="Process clinical query through Oxygen RAG pipeline",
    dependencies=[Depends(verify_authentication)],
)
async def chat_endpoint(payload: ChatRequest, request: Request) -> ChatResponse:
    """
    Submits a query to the Dr. Salem clinical RAG pipeline.
    Executes deterministic circuit breaker for unsupported/out-of-scope queries (0 LLM calls).
    """
    req_id = getattr(request.state, "request_id", f"req_{uuid.uuid4().hex[:12]}")
    service = get_rag_service()

    # Convert conversation turns to dicts if provided
    history_dicts = None
    if payload.conversation_history:
        history_dicts = [t.model_dump() for t in payload.conversation_history]

    t0 = time.perf_counter()
    try:
        raw_result = service.process_query(
            query=payload.query,
            conversation_history=history_dicts,
            request_id=req_id,
        )
    except Exception as e:
        logger.error(f"RAG processing failed: {e}", extra={"request_id": req_id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing clinical query in RAG pipeline.",
        )

    t1 = time.perf_counter()
    total_ms = round((t1 - t0) * 1000.0, 2)

    return ChatResponse.from_pipeline_result(
        request_id=req_id,
        result=raw_result,
        latency_ms=total_ms,
    )


# ── 2. GET /api/v1/health & /health & /api/health ───────────────────────────
@app.get(
    "/health",
    response_model=HealthResponse,
    include_in_schema=False,
)
@app.get(
    "/api/health",
    response_model=HealthResponse,
    include_in_schema=False,
)
@app.get(
    "/api/v1/health",
    response_model=HealthResponse,
    summary="Liveness probe (fast, lightweight, 0 RAG calls)",
)
async def health_endpoint() -> HealthResponse:
    """Cheap liveness probe to verify HTTP process is responding."""
    service = get_rag_service()
    is_ready = service.is_ready
    provider_name = "unknown"
    if is_ready:
        provider_name = getattr(service._pipeline.llm_generator.provider, "provider_name", "unknown")
    
    return HealthResponse(
        status="ok",
        service="oxygen-medical-rag-api",
        rag_loaded=is_ready,
        retriever_loaded=is_ready,
        llm_provider=provider_name,
    )


# ── 3. GET /api/v1/health/rag & /health/rag ──────────────────────────────────
@app.get(
    "/health/rag",
    response_model=RAGHealthResponse,
    include_in_schema=False,
)
@app.get(
    "/api/v1/health/rag",
    response_model=RAGHealthResponse,
    summary="Diagnostic health check for all RAG subsystems (zero secrets)",
)
async def rag_health_endpoint() -> RAGHealthResponse:
    """Diagnostic probe verifying BM25, dense index, embedding model, and LLM configuration."""
    service = get_rag_service()
    unready = []

    pipeline = getattr(service, "_pipeline", None)
    retriever_ready = False
    dense_ready = False
    bm25_ready = False
    embed_ready = False
    chunks_count = 0

    if pipeline is not None and hasattr(pipeline, "hybrid_retriever") and pipeline.hybrid_retriever is not None:
        retriever_ready = True
        hr = pipeline.hybrid_retriever
        
        # Check dense retriever & NPZ chunks
        if hasattr(hr, "dense_retriever") and hr.dense_retriever is not None:
            dense_ready = len(hr.dense_retriever.chunk_ids) > 0
            chunks_count = len(hr.dense_retriever.chunk_ids)
            if hasattr(hr.dense_retriever, "_model") or hasattr(hr.dense_retriever, "model_name"):
                embed_ready = True
            else:
                unready.append("embedding_model")
        else:
            unready.append("dense_retriever")
        
        # Check BM25 retriever
        if hasattr(hr, "bm25_retriever") and hr.bm25_retriever is not None:
            bm25_ready = getattr(hr.bm25_retriever, "corpus_size", len(getattr(hr.bm25_retriever, "chunk_ids", []))) > 0
        else:
            unready.append("bm25_retriever")
    else:
        unready.append("hybrid_retriever")

    # Check LLM configuration
    llm_configured = False
    llm_provider_name = "unconfigured"
    if pipeline is not None and hasattr(pipeline, "llm_generator") and pipeline.llm_generator is not None:
        provider = pipeline.llm_generator.provider
        if provider is not None:
            llm_provider_name = getattr(provider, "provider_name", "unknown")
            # Check if required provider keys/settings exist
            if llm_provider_name == "mock":
                llm_configured = True
            elif llm_provider_name == "google_gemini":
                llm_configured = bool(getattr(provider, "api_key", None))
            elif llm_provider_name in {"groq", "nvidia", "openai_compatible"}:
                llm_configured = bool(getattr(provider, "api_key", None) or getattr(provider, "base_url", None))
            else:
                llm_configured = True
    
    if not llm_configured:
        unready.append("llm_configuration")

    overall_status = "ok" if (retriever_ready and dense_ready and bm25_ready and embed_ready and llm_configured) else "degraded"

    return RAGHealthResponse(
        status=overall_status,
        retriever=retriever_ready,
        dense_index=dense_ready,
        bm25=bm25_ready,
        embedding_model=embed_ready,
        llm_configured=llm_configured,
        llm_provider=llm_provider_name,
        vector_store_chunks=chunks_count,
        unready_components=unready,
    )


# ── 4. GET /api/v1/ready & /ready ───────────────────────────────────────────
@app.get(
    "/ready",
    response_model=ReadyResponse,
    include_in_schema=False,
)
@app.get(
    "/api/v1/ready",
    response_model=ReadyResponse,
    summary="Readiness probe verifying vector store and model initialization",
)
async def ready_endpoint() -> ReadyResponse:
    """Verifies that vector store and embedding models are loaded in memory."""
    service = get_rag_service()
    if not service.is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG pipeline is still initializing.",
        )
    
    total_chunks = len(service._pipeline.hybrid_retriever.dense_retriever.chunk_ids)
    return ReadyResponse(
        status="ready",
        pipeline_ready=True,
        vector_store_chunks=total_chunks,
    )


# ── 5. GET /api/v1/meta ────────────────────────────────────────────────────────
@app.get(
    "/api/v1/meta",
    response_model=MetaResponse,
    summary="Safe public metadata about active RAG version and provider",
)
async def meta_endpoint() -> MetaResponse:
    """Returns public safe metadata. Never exposes secrets or internal filesystem paths."""
    service = get_rag_service()
    provider_name = getattr(service._pipeline.llm_generator.provider, "provider_name", "unknown")
    model_name = getattr(service._pipeline.llm_generator.provider, "model_name", "unknown")

    return MetaResponse(
        api_version="1.0.0",
        rag_version="WHO-Tobacco-Cessation-2024-Phase5",
        provider=provider_name,
        model=model_name,
        circuit_breaker_enabled=True,
    )


@app.get("/api/v1/diagnostic", include_in_schema=False)
async def diagnostic_endpoint():
    """Safe diagnostic probe to inspect LLM provider connection error."""
    service = get_rag_service()
    gen = service._pipeline.llm_generator
    api_key = getattr(gen.provider, "api_key", None)
    has_key = bool(api_key)
    key_len = len(api_key) if api_key else 0
    key_prefix = api_key[:4] if (api_key and key_len >= 4) else ""
    provider_name = getattr(gen.provider, "provider_name", "unknown")
    model_name = getattr(gen.provider, "model_name", "unknown")
    
    test_error = None
    test_success = False
    try:
        res = gen.provider.complete(system_prompt="Say hi", messages=[{"role": "user", "content": "hi"}], max_tokens=10)
        test_success = bool(res)
    except Exception as e:
        test_error = str(e)
        
    return {
        "has_key": has_key,
        "key_len": key_len,
        "key_prefix": key_prefix,
        "provider": provider_name,
        "model": model_name,
        "test_success": test_success,
        "test_error": test_error,
    }

