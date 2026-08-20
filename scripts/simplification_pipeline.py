"""
[DEPRECATED / COMPATIBILITY WRAPPER]
Medical & Simplification Pipeline — Medical RAG Project: Oxygen (أوكسجين)

ARCHITECTURAL UPDATE:
Simplification RAG runtime rule retrieval has been deprecated in favor of the
streamlined production architecture (Single Medical RAG + Strengthened System Prompt + Post-Generation Verifier).
This module is preserved for backward compatibility and historical benchmark testing.
"""

from __future__ import annotations

import os
import sys
import logging
from typing import Dict, List, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from llm_generation_pipeline import GenerationPipeline, get_pipeline, generate_answer
from llm_generator import LLMGenerator
from simplification_verifier import SimplificationVerifier

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class SimplificationIntegratedPipeline:
    """
    Backward-compatible wrapper routing to the streamlined GenerationPipeline.
    """

    def __init__(
        self,
        llm_generator: Optional[LLMGenerator] = None,
        verifier: Optional[SimplificationVerifier] = None,
        **kwargs,
    ):
        self.underlying_pipeline = GenerationPipeline(
            llm_generator=llm_generator,
            verifier=verifier,
        )

    def process(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        enable_simplification_rag: bool = False,
    ) -> Dict[str, Any]:
        """
        Processes query through streamlined single Medical RAG + System Prompt pipeline.
        """
        res = self.underlying_pipeline.process(query, conversation_history=conversation_history)
        # Populate legacy keys for backward-compatibility with older tests
        res["simplification_rag"] = {
            "enabled": False,
            "runtime_status": "DEPRECATED_INTERNALIZED_INTO_SYSTEM_PROMPT",
            "retrieved_rules_count": 0,
        }
        res["medical_rag_metrics"] = res.get("retrieval_metrics", {})
        return res


_DUAL_PIPELINE_INSTANCE: Optional[SimplificationIntegratedPipeline] = None


def get_simplification_pipeline() -> SimplificationIntegratedPipeline:
    """Returns or lazily creates a shared compatibility wrapper."""
    global _DUAL_PIPELINE_INSTANCE
    if _DUAL_PIPELINE_INSTANCE is None:
        _DUAL_PIPELINE_INSTANCE = SimplificationIntegratedPipeline()
    return _DUAL_PIPELINE_INSTANCE


def generate_simplified_answer(
    query: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    pipeline: Optional[SimplificationIntegratedPipeline] = None,
    generator: Optional[LLMGenerator] = None,
) -> Dict[str, Any]:
    """
    Public entry point for generating patient-facing answers.
    Routes to the streamlined GenerationPipeline.
    """
    pipe = pipeline or get_simplification_pipeline()
    if generator:
        pipe.underlying_pipeline.llm_generator = generator
    return pipe.process(query, conversation_history=conversation_history)
