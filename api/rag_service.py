"""
RAGService Boundary — Medical RAG: Oxygen (أوكسجين)
Encapsulates pipeline execution without modifying core RAG semantics or circuit breaker behavior.

Architectural Contract:
1. Pure thin wrapper over singleton get_pipeline().
2. ZERO RAG business logic, zero threshold manipulation, zero prompt rewriting.
3. Propagates existing GroundedAnswerContract decisions verbatim.
4. If is_generation_allowed == False (UNSUPPORTED / OUT_OF_SCOPE / ABSTAIN) -> Returns deterministic response; LLM calls == 0.
"""

from __future__ import annotations

import os
import sys
import time
import logging
from typing import Dict, List, Any, Optional

# Ensure scripts path is reachable
_SCRIPTS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
if _SCRIPTS_PATH not in sys.path:
    sys.path.insert(0, _SCRIPTS_PATH)

from llm_generation_pipeline import GenerationPipeline, get_pipeline

logger = logging.getLogger("oxygen.rag_service")


class RAGService:
    """Thin service wrapper around the frozen GenerationPipeline."""

    def __init__(self, pipeline: Optional[GenerationPipeline] = None):
        self._pipeline = pipeline or get_pipeline()

    @property
    def is_ready(self) -> bool:
        """Verifies if core pipeline and embedding models are initialized."""
        return (
            self._pipeline is not None
            and hasattr(self._pipeline, "hybrid_retriever")
            and self._pipeline.hybrid_retriever is not None
        )

    def process_query(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes end-to-end RAG query through the frozen pipeline.
        Measures total service latency and returns raw pipeline response dict.
        """
        t0 = time.perf_counter()
        
        # Invoke existing frozen pipeline directly
        result = self._pipeline.process(query=query, conversation_history=conversation_history)
        
        t1 = time.perf_counter()
        latency_ms = round((t1 - t0) * 1000.0, 2)
        result["service_latency_ms"] = latency_ms

        logger.info(
            "request_id=%s | contract_state=%s | provider=%s | latency_ms=%.2f",
            request_id or "untracked",
            result.get("contract_state"),
            result.get("provider"),
            latency_ms,
        )

        return result


# Global singleton instance
_SERVICE_INSTANCE: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Returns or lazily creates a shared RAGService instance."""
    global _SERVICE_INSTANCE
    if _SERVICE_INSTANCE is None:
        _SERVICE_INSTANCE = RAGService()
    return _SERVICE_INSTANCE
