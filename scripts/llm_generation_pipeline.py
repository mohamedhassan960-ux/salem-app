"""
End-to-End Clinical Generation Pipeline — Medical RAG Project: Oxygen (أوكسجين)
Source Document: WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)

Streamlined Production Architecture:
1. Clinical Query Understanding (entity extraction, dialect mapping, intent recognition)
2. Hybrid Retrieval (BM25 sparse + Dense semantic embedding -> RRF fusion)
3. Clinical Reranker (multi-aspect clinical scoring & recommendation prioritization)
4. Evidence Quality Gate (safety filtering, negative control defense, quality tiers)
5. [PHASE 5] Grounded Answer Contract (deterministic circuit breaker — NO EVIDENCE -> NO LLM CALL)
6. Context Assembler (verbatim evidence token-budget assembly & provenance preservation)
7. LLM Generator Layer (with contract-state-aware prompt)
8. Post-Generation Verification Layer (auditing raw LLM output for dosage/meaning/uncertainty preservation)

Public API:
generate_answer(query, conversation_history=None) -> Dict[str, Any]
"""

from __future__ import annotations

import os
import sys
import logging
from typing import Dict, List, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from query_understanding import ClinicalQueryUnderstanding, ClinicalQueryRepresentation
from bm25_retriever import BM25Retriever
from dense_retriever import DenseRetriever
from hybrid_retriever import HybridRetriever
from reranker import ClinicalReranker, RerankedCandidate
from evidence_quality_gate import EvidenceQualityGate, EvidenceQualityGateResult
from claim_validator import ClaimCoverageValidator, ClaimCoverageReport
from grounded_answer_contract import GroundedAnswerContract, GroundedAnswerContractResult, ContractState
from context_assembler import ContextAssembler, AssembledContext
from llm_generator import LLMGenerator, LLMGenerationResponse, LLMProvider, MockLLMProvider
from simplification_verifier import SimplificationVerifier, VerificationResult

RECORDS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "retrieval_records_v2.json")
DENSE_NPZ = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "dense_index_v2.npz")
DENSE_META = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "dense_metadata_v2.json")
LOCAL_EMBED_MODEL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "models", "multilingual-e5-small")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class GenerationPipeline:
    """
    Streamlined production clinical generation pipeline.
    Maintains 100% frozen Medical RAG, uses strengthened System Prompt,
    and performs claim-level evidence validation without runtime rule retrieval.
    """

    def __init__(
        self,
        query_understanding: Optional[ClinicalQueryUnderstanding] = None,
        hybrid_retriever: Optional[HybridRetriever] = None,
        reranker: Optional[ClinicalReranker] = None,
        quality_gate: Optional[EvidenceQualityGate] = None,
        claim_validator: Optional[ClaimCoverageValidator] = None,
        context_assembler: Optional[ContextAssembler] = None,
        llm_generator: Optional[LLMGenerator] = None,
        verifier: Optional[SimplificationVerifier] = None,
    ):
        self.query_understanding = query_understanding or ClinicalQueryUnderstanding()
        self.hybrid_retriever = hybrid_retriever or HybridRetriever.from_files(
            records_path=RECORDS_PATH,
            dense_npz_path=DENSE_NPZ,
            dense_meta_path=DENSE_META,
            model_name=LOCAL_EMBED_MODEL,
            k_rrf=60,
            candidate_pool_size=30,
        )
        self.reranker = reranker or ClinicalReranker()
        self.quality_gate = quality_gate or EvidenceQualityGate()
        self.claim_validator = claim_validator or ClaimCoverageValidator()
        self.context_assembler = context_assembler or ContextAssembler(max_context_tokens=3000)
        self.llm_generator = llm_generator or LLMGenerator()
        self.verifier = verifier or SimplificationVerifier()

    def process(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Processes a query end-to-end through the RAG pipeline and generates a response."""
        # ── 1. Query Understanding ─────────────────────────────────────────
        parsed_q = self.query_understanding.parse_query(query)

        # ── 2. Hybrid Retrieval (Top-20 candidates) ────────────────────────
        candidates = self.hybrid_retriever.retrieve(parsed_q.expanded_search_query, top_k=20)

        # ── 3. Clinical Reranker ───────────────────────────────────────────
        reranked = self.reranker.rerank(candidates, parsed_q, top_k=20)

        # ── 4. Evidence Quality Gate ───────────────────────────────────────
        gate_res = self.quality_gate.evaluate_candidates(reranked, parsed_q, final_budget_k=5)

        # ── 5. Claim-Level Evidence Coverage Validation ────────────────────
        claim_report = self.claim_validator.validate_query(
            query=query,
            admitted_evidence=gate_res.admitted_candidates,
            safety_flag=gate_res.safety_flag,
            parsed_query=parsed_q,
        )

        # ── PHASE 5: Grounded Answer Contract (CIRCUIT BREAKER) ───────────
        # Deterministic decision: SUPPORTED / PARTIALLY_SUPPORTED / UNSUPPORTED / OUT_OF_SCOPE / ABSTAIN
        # If is_generation_allowed == False → return deterministic response; LLM provider is NEVER called.
        contract = GroundedAnswerContract.evaluate(gate_res, claim_report)

        logging.info(
            "[Phase5-Contract] state=%s | allowed=%s | coverage=%.2f | flag=%s",
            contract.state.value,
            contract.is_generation_allowed,
            contract.claim_coverage_ratio,
            contract.safety_flag,
        )

        if not contract.is_generation_allowed:
            # ── CIRCUIT BREAKER: deterministic abstention — no LLM call ────
            return {
                "answer": contract.deterministic_response,
                "citations": [],
                "grounded": False,
                "safety_status": contract.safety_flag or contract.state.value,
                "contract_state": contract.state.value,
                "contract_reason": contract.reason,
                "provider": "deterministic",
                "model": "grounded_answer_contract_v1",
                "verification": {"safety_status": contract.safety_flag or contract.state.value, "llm_called": False},
                "claim_coverage_report": claim_report.to_dict(),
                "query_understanding": {
                    "is_arabic": parsed_q.is_arabic,
                    "is_egyptian_dialect": parsed_q.is_egyptian_dialect,
                    "detected_intents": parsed_q.detected_intents,
                    "detected_interventions": parsed_q.detected_interventions,
                    "detected_populations": parsed_q.detected_populations,
                    "is_out_of_scope": parsed_q.is_out_of_scope,
                },
                "retrieval_metrics": {
                    "candidates_reranked": len(reranked),
                    "admitted_evidence_count": len(gate_res.admitted_candidates),
                    "direct_evidence_count": gate_res.direct_evidence_count,
                    "claim_coverage_ratio": claim_report.claim_coverage_ratio,
                    "grounding_decision": claim_report.grounding_decision,
                    "total_required_claims": claim_report.total_required_claims,
                    "supported_claims_count": claim_report.supported_claims_count,
                    "is_grounded_in_guideline": False,
                },
            }

        # ── 6. Context Assembly (only reached when generation is allowed) ──
        ca_sources = gate_res.to_context_assembler_sources()
        assembled: Optional[AssembledContext] = None
        if ca_sources:
            assembled = self.context_assembler.assemble(query, ca_sources)

        # Build Citations Metadata
        citations_metadata = []
        if assembled:
            for src in assembled.sources:
                citations_metadata.append({
                    "source_id": src.source_id,
                    "section_number": src.section_number,
                    "physical_page_start": src.physical_page_start,
                    "title": src.title,
                    "chunk_id": src.chunk_id,
                })

        # ── 7. LLM Generation (contract-state-aware prompt) ───────────────
        context_str = assembled.context if assembled else ""
        safety_flag = gate_res.safety_flag
        is_claim_grounded = contract.state in {ContractState.SUPPORTED, ContractState.PARTIALLY_SUPPORTED}

        gen_resp = self.llm_generator.generate(
            query=query,
            context=context_str,
            citations_metadata=citations_metadata,
            conversation_history=conversation_history,
            safety_flag=safety_flag,
            is_grounded=is_claim_grounded,
            contract_state=contract.state.value,
            unsupported_claims=contract.unsupported_claims,
        )

        # ── 8. Post-Generation Verification ───────────────────────────────
        raw_answer = gen_resp.answer
        verif_res = self.verifier.verify(
            generated_answer=raw_answer,
            medical_evidence=context_str,
            user_query=query,
            safety_flag=safety_flag,
        )

        # Gate flag takes absolute priority as final safety status
        final_safety_status = (
            gate_res.safety_flag
            if gate_res.safety_flag
            else verif_res.safety_status
        )

        direct_count = gate_res.direct_evidence_count
        total_admitted = len(gate_res.admitted_candidates)

        return {
            "answer": raw_answer,
            "citations": gen_resp.citations,
            "grounded": gen_resp.grounded and (final_safety_status != "NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE"),
            "safety_status": final_safety_status,
            "contract_state": contract.state.value,
            "contract_reason": contract.reason,
            "provider": gen_resp.provider,
            "model": gen_resp.model,
            "verification": verif_res.to_dict(),
            "claim_coverage_report": claim_report.to_dict(),
            "query_understanding": {
                "is_arabic": parsed_q.is_arabic,
                "is_egyptian_dialect": parsed_q.is_egyptian_dialect,
                "detected_intents": parsed_q.detected_intents,
                "detected_interventions": parsed_q.detected_interventions,
                "detected_populations": parsed_q.detected_populations,
                "is_out_of_scope": parsed_q.is_out_of_scope,
            },
            "retrieval_metrics": {
                "candidates_reranked": len(reranked),
                "admitted_evidence_count": total_admitted,
                "direct_evidence_count": direct_count,
                "claim_coverage_ratio": claim_report.claim_coverage_ratio,
                "grounding_decision": claim_report.grounding_decision,
                "total_required_claims": claim_report.total_required_claims,
                "supported_claims_count": claim_report.supported_claims_count,
                "is_grounded_in_guideline": is_claim_grounded,
            },
        }


# Global singleton instance for easy import
_PIPELINE_INSTANCE: Optional[GenerationPipeline] = None


def get_pipeline() -> GenerationPipeline:
    """Returns or lazily creates a shared GenerationPipeline instance."""
    global _PIPELINE_INSTANCE
    if _PIPELINE_INSTANCE is None:
        _PIPELINE_INSTANCE = GenerationPipeline()
    return _PIPELINE_INSTANCE


def generate_answer(
    query: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    generator: Optional[LLMGenerator] = None,
    pipeline: Optional[GenerationPipeline] = None,
) -> Dict[str, Any]:
    """
    Public entry point for generating clinical answers.

    Parameters
    ----------
    query : str
        Patient's query or message.
    conversation_history : Optional[List[Dict[str, str]]]
        Previous conversation turns [{'role': 'user'|'assistant', 'content': '...'}].
    generator : Optional[LLMGenerator]
        Custom generator (e.g. with MockLLMProvider for unit testing).
    pipeline : Optional[GenerationPipeline]
        Custom pipeline instance.

    Returns
    -------
    Dict[str, Any] with answer, citations, grounded, safety_status, provider, model, verification.
    """
    pipe = pipeline or get_pipeline()
    if generator:
        pipe.llm_generator = generator
    return pipe.process(query, conversation_history=conversation_history)
