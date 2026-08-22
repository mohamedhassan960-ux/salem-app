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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECORDS_PATH = os.path.join(BASE_DIR, "outputs", "retrieval_records_v2.json")
DENSE_NPZ_V3 = os.path.join(BASE_DIR, "outputs", "dense_index_cloud_v3.npz")
DENSE_META_V3 = os.path.join(BASE_DIR, "outputs", "dense_metadata_cloud_v3.json")
DENSE_NPZ_V2 = os.path.join(BASE_DIR, "outputs", "dense_index_v2.npz")
DENSE_META_V2 = os.path.join(BASE_DIR, "outputs", "dense_metadata_v2.json")

# Prioritize v3 cloud index if present, fallback to v2 for rollback
DENSE_NPZ = DENSE_NPZ_V3 if os.path.exists(DENSE_NPZ_V3) else DENSE_NPZ_V2
DENSE_META = DENSE_META_V3 if os.path.exists(DENSE_META_V3) else DENSE_META_V2
LOCAL_EMBED_MODEL = os.path.join(BASE_DIR, "data", "models", "multilingual-e5-small")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def extract_verified_evidence_highlight(original_text: str, query: str = "", parsed_query: Optional[Any] = None) -> Optional[str]:
    """
    Extracts a verified, verbatim supporting sentence/span from original_text.
    Guarantees:
    1. Returns a span ONLY if it is an exact verbatim substring of original_text.
    2. Matches clinical recommendations, interventions, or cessation actions.
    3. If no exact match can be rigorously proven, returns None.
    """
    if not original_text or not original_text.strip():
        return None

    import re
    raw_sentences = re.split(r'(?<=[.!?\n])\s+', original_text)
    
    guideline_markers = [
        "recommends", "recommendation", "effective", "efficacy", "evidence",
        "intervention", "treatment", "support", "cessation", "quitting",
        "cravings", "withdrawal", "advice", "counselling", "behavioral"
    ]
    
    keywords = set()
    if parsed_query:
        for ent in getattr(parsed_query, "detected_interventions", []):
            keywords.add(str(ent).lower())
        for intent in getattr(parsed_query, "detected_intents", []):
            keywords.add(str(intent).lower())
            
    best_span = None
    best_score = 0
    
    for s in raw_sentences:
        clean_s = s.strip()
        if len(clean_s) < 20 or len(clean_s) >= len(original_text) * 0.95:
            continue
        
        # Rigorous check: clean_s MUST BE an exact substring in original_text
        if clean_s not in original_text:
            continue
            
        score = 0
        s_lower = clean_s.lower()
        
        if any(m in s_lower for m in ["recommends", "suggests", "strong recommendation", "conditional recommendation"]):
            score += 3
        if any(m in s_lower for m in guideline_markers):
            score += 1
        for kw in keywords:
            if kw in s_lower:
                score += 2
                
        if score > best_score:
            best_score = score
            best_span = clean_s
            
    if best_score >= 2 and best_span and (best_span in original_text):
        return best_span
        
    return None


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

        # Build Citations Metadata with Real Evidence Store Verification
        citations_metadata = []
        records_lookup = getattr(self.hybrid_retriever.dense_retriever, "records_by_id", {})
        if assembled:
            for src in assembled.sources:
                rec = records_lookup.get(src.chunk_id, {})
                h = rec.get("hierarchy", {})
                p = rec.get("provenance", {})
                c = rec.get("content", {})
                
                original_text = c.get("verbatim_text", "")
                section_num = src.section_number or h.get("section_number")
                sec_title = src.title or h.get("section_title", "")
                page_start = src.physical_page_start or p.get("physical_page_start")
                page_end = p.get("physical_page_end")
                doc_title = rec.get("document_title") or "WHO clinical treatment guideline for tobacco cessation in adults"
                
                verified_highlight = extract_verified_evidence_highlight(original_text, query, parsed_q)
                if verified_highlight and (verified_highlight not in original_text):
                    verified_highlight = None
                
                citations_metadata.append({
                    "citation_id": str(src.source_id),
                    "source_id": src.source_id,
                    "chunk_id": src.chunk_id,
                    "section_number": section_num,
                    "physical_page_start": page_start,
                    "physical_page_end": page_end,
                    "title": sec_title,
                    "source": {
                        "title": doc_title,
                        "section_title": sec_title,
                        "organization": "منظمة الصحة العالمية (WHO)",
                        "year": "2024",
                        "section": section_num,
                        "page": str(page_start) if page_start is not None else None,
                        "url": "https://www.who.int/publications/i/item/9789240096493",
                    },
                    "evidence": {
                        "original_text": original_text,
                        "highlight_text": verified_highlight,
                    }
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
