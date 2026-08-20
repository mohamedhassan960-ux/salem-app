"""
Pydantic Request & Response Schemas — Medical RAG: Oxygen (أوكسجين)
Validates inputs strictly without mutating clinical query texts.
Adapts raw pipeline response into a consistent, safe HTTP API schema.
"""

from __future__ import annotations

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class ConversationTurn(BaseModel):
    """Single turn in clinical conversation history."""
    role: str = Field(..., description="Role of the speaker: 'user' or 'assistant'")
    content: str = Field(..., min_length=1, max_length=4000, description="Message content")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        v_clean = v.strip().lower()
        if v_clean not in {"user", "assistant", "system"}:
            raise ValueError("Role must be 'user' or 'assistant'")
        return v_clean


class ChatRequest(BaseModel):
    """Inbound chat request from clinical client."""
    query: str = Field(..., min_length=2, max_length=2000, description="Patient medical query text")
    conversation_history: Optional[List[ConversationTurn]] = Field(
        default=None,
        description="Optional list of prior conversation turns"
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        v_clean = v.strip()
        if not v_clean:
            raise ValueError("Query string cannot be empty or whitespace only")
        return v_clean


class CitationItemSchema(BaseModel):
    """Citation metadata provenance for grounded WHO evidence."""
    source_id: int
    section_number: Optional[str] = None
    physical_page_start: Optional[int] = None
    title: str
    chunk_id: str


class ChatResponse(BaseModel):
    """Outbound grounded clinical response."""
    request_id: str
    answer: str
    contract_state: str
    grounded: bool
    safety_status: str
    provider: str
    model: str
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    latency_ms: float
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution and verification metadata")

    @classmethod
    def from_pipeline_result(cls, request_id: str, result: Dict[str, Any], latency_ms: float) -> ChatResponse:
        """Adapts raw pipeline dictionary into typed API response."""
        # Convert citation dataclasses or dicts if present
        raw_cits = result.get("citations", []) or []
        cit_dicts = []
        for c in raw_cits:
            if hasattr(c, "to_dict"):
                cit_dicts.append(c.to_dict())
            elif isinstance(c, dict):
                cit_dicts.append(c)
            elif hasattr(c, "__dict__"):
                cit_dicts.append(c.__dict__)

        meta_info = {
            "query_understanding": result.get("query_understanding", {}),
            "retrieval_metrics": result.get("retrieval_metrics", {}),
            "contract_reason": result.get("contract_reason"),
            "verification": result.get("verification", {}),
        }

        return cls(
            request_id=request_id,
            answer=result.get("answer", ""),
            contract_state=result.get("contract_state", "UNKNOWN"),
            grounded=bool(result.get("grounded", False)),
            safety_status=result.get("safety_status", "UNKNOWN"),
            provider=result.get("provider", "unknown"),
            model=result.get("model", "unknown"),
            citations=cit_dicts,
            latency_ms=latency_ms,
            metadata=meta_info,
        )


class HealthResponse(BaseModel):
    """Lightweight process liveness health status."""
    status: str = "ok"
    service: str = "oxygen-medical-rag-api"


class ReadyResponse(BaseModel):
    """Application readiness verification."""
    status: str
    pipeline_ready: bool
    vector_store_chunks: int


class MetaResponse(BaseModel):
    """Safe public metadata."""
    api_version: str = "1.0.0"
    rag_version: str = "WHO-Tobacco-Cessation-2024-Phase5"
    provider: str
    model: str
    circuit_breaker_enabled: bool = True
