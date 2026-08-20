"""
Clinical Multi-Aspect Semantic Reranker — Medical RAG: Oxygen (أوكسجين)
Source Document: WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)

Takes Top-20 Candidates from Hybrid Retrieval and scores them along multiple clinical dimensions:
1. Deep Cross-Lingual Semantic Similarity (Query Vector vs Document Vector)
2. Clinical Intervention Alignment (Target Drug / Therapy match)
3. Population & Special Situation Alignment (Pregnancy, Adolescents, TB, Comorbidities)
4. Content-Type Weighting (Prioritizes 'recommendation' and 'evidence' over 'acknowledgements'/'references')
5. Generic Hub Chunk Penalty (Down-weights preface/glossary boilerplate for specific clinical questions)

Guarantees:
- 100% Deterministic & Local CPU execution.
- Calibrated Clinical Relevance Score in range [0.0, 1.0].
- Preserves full provenance and verbatim text without mutation.
"""

from __future__ import annotations

import os
import re
import json
import logging
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Set, Tuple

import numpy as np

from hybrid_retriever import HybridSearchResult
from query_understanding import ClinicalQueryRepresentation, ClinicalQueryUnderstanding
from dense_retriever import DenseRetriever

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


@dataclass
class RerankedCandidate:
    """A candidate chunk enriched with detailed multi-aspect clinical reranker scores."""
    chunk_id: str
    clinical_score: float                   # Calibrated unified clinical relevance score [0.0, 1.0]
    rerank_position: int                    # 1-indexed final reranked position
    initial_hybrid_rank: int                # Original rank from Hybrid Top-20
    semantic_score: float                   # Raw cosine similarity score
    intervention_match_score: float         # [0.0, 1.0]
    population_match_score: float           # [0.0, 1.0]
    content_type_weight: float              # Multiplier / bonus for clinical content type
    text: str                               # Verbatim ground truth text (100% untouched)
    section_number: Optional[str]
    section_title: str
    heading_path: str
    physical_page_start: Optional[int]
    physical_page_end: Optional[int]
    printed_page_start: Optional[int]
    printed_page_end: Optional[int]
    content_type: str
    retrieval_role: str
    document_id: str
    node_id: str
    parent_id: str
    token_count: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Intervention key to relevant section prefixes / chunk IDs mapping
INTERVENTION_SECTION_MAP: Dict[str, Set[str]] = {
    "varenicline": {"3.3.1", "3.3.3.3", "3.3.3.6", "3.3.4", "chunk_sec_3_3_1", "chunk_sec_3_3_3_3_p01", "chunk_sec_3_3_3_6_p02", "chunk_sec_3_3_4_p01"},
    "bupropion_sr": {"3.3.1", "3.3.3.2", "3.3.3.6", "3.3.4", "chunk_sec_3_3_1", "chunk_sec_3_3_3_2", "chunk_sec_3_3_4_p01"},
    "cytisine": {"3.3.1", "3.3.3.4", "chunk_sec_3_3_1", "chunk_sec_3_3_3_4"},
    "nrt_transdermal_patch": {"3.3.1", "3.3.3.1", "3.3.3.5", "chunk_sec_3_3_1", "chunk_sec_3_3_3_1_p01", "chunk_sec_3_3_3_5", "chunk_sec_3_3_3_6_p03"},
    "nrt_gum": {"3.3.1", "3.3.3.1", "3.3.3.5", "chunk_sec_3_3_1", "chunk_sec_3_3_3_1_p01", "chunk_sec_3_3_3_5", "chunk_sec_3_3_3_6_p03"},
    "nicotine_replacement_therapy": {"3.3.1", "3.3.3.1", "3.3.3.5", "chunk_sec_3_3_1", "chunk_sec_3_3_3_1_p01", "chunk_sec_3_3_3_5", "chunk_sec_3_3_3_6_p03"},
    "combination_behavioural_pharmacotherapy": {"3.5.1", "3.5.3", "chunk_sec_3_5_1", "chunk_sec_3_5_3_p01", "chunk_sec_3_5_3_p02"},
    "combination_therapy": {"3.3.1", "3.3.3.5", "3.5.1", "3.5.3", "chunk_sec_3_3_1", "chunk_sec_3_3_3_5", "chunk_sec_3_5_1", "chunk_sec_3_5_3_p01"},
    "oral_pharmacotherapy": {"3.3.1", "3.3.3.2", "3.3.3.3", "3.3.3.4", "3.3.3.6", "chunk_sec_3_3_1"},
    "brief_advice": {"3.1.1", "3.1.3", "chunk_sec_3_1_1", "chunk_sec_3_1_3_p01"},
    "physician_brief_advice_or_counselling": {"3.1.1", "3.1.3", "chunk_sec_3_1_1", "chunk_sec_3_1_3_p01"},
    "individual_intensive_counselling": {"3.1.1", "3.1.3", "chunk_sec_3_1_1", "chunk_sec_3_1_3_p02"},
    "group_behavioural_counselling": {"3.1.1", "3.1.3", "chunk_sec_3_1_1", "chunk_sec_3_1_3_p03"},
    "toll_free_quitline": {"3.1.1", "3.1.3", "chunk_sec_3_1_1", "chunk_sec_3_1_3_p04"},
    "mobile_text_messaging_sms": {"3.2.1", "3.2.3", "chunk_sec_3_2_1", "chunk_sec_3_2_3_p01"},
    "digital_smartphone_interventions": {"3.2.1", "3.2.3", "chunk_sec_3_2_1", "chunk_sec_3_2_3_p01"},
    "ai_chatbot_interventions": {"3.2.1", "3.2.3", "chunk_sec_3_2_1", "chunk_sec_3_2_3_p02"},
    "smokeless_tobacco": {"3.4.1", "3.4.3", "chunk_sec_3_4_1", "chunk_sec_3_4_3_p01"},
    "acupuncture_unproven": {"3.6.1", "3.6.3", "chunk_sec_3_6_1", "chunk_sec_3_6_3_p01"},
    "hypnotherapy_unproven": {"3.6.1", "3.6.3", "chunk_sec_3_6_1", "chunk_sec_3_6_3_p01"},
}

POPULATION_SECTION_MAP: Dict[str, Set[str]] = {
    "pregnant_women": {"3.1.4", "3.3.4", "chunk_sec_3_1_4", "chunk_sec_3_3_4_p01"},
    "adolescents_young_people": {"3.1.4", "3.3.4", "chunk_sec_3_1_4", "chunk_sec_3_3_4_p01"},
    "tuberculosis_patients": {"3.1.4", "3.3.4", "chunk_sec_3_1_4", "chunk_sec_3_3_4_p01"},
    "seizure_disorder_patients": {"3.3.3.2", "3.3.4", "chunk_sec_3_3_3_2", "chunk_sec_3_3_4_p01"},
    "heavy_smokers": {"3.3.1", "3.3.3.5", "3.5.1", "chunk_sec_3_3_1", "chunk_sec_3_3_3_5", "chunk_sec_3_5_1"},
    "relapse_smokers": {"3.1.1", "3.3.1", "3.5.1", "chunk_sec_3_1_1", "chunk_sec_3_3_1", "chunk_sec_3_5_1"},
}


class ClinicalReranker:
    """
    Multi-aspect clinical cross-scorer combining semantic embeddings, clinical taxonomy alignment,
    content-type scoring, and penalty filtering.
    """

    def __init__(self, dense_retriever: Optional[DenseRetriever] = None):
        self.dense_retriever = dense_retriever

    def score_candidate(
        self,
        candidate: HybridSearchResult,
        parsed_query: ClinicalQueryRepresentation,
        query_vector: Optional[np.ndarray] = None,
    ) -> RerankedCandidate:
        """Scores a single candidate chunk against the parsed clinical query."""
        text_lower = candidate.text.lower()
        sec = candidate.section_number or ""
        cid = candidate.chunk_id
        ctype = candidate.content_type

        # 1. Direct Question-Chunk Relevance Base
        # Combines dense semantic cosine similarity with normalized hybrid rank consensus (RRF)
        dense_rel = candidate.dense_score if candidate.dense_score is not None else 0.5
        rrf_norm = min(1.0, candidate.rrf_score / 0.035) if candidate.rrf_score else 0.5
        relevance_score = (dense_rel * 0.70) + (rrf_norm * 0.30)

        # 2. Content Type Calibrated Prior
        # Bounded clinical prior: recommendation (+0.04) > evidence (+0.03) > narrative/discussion (0.00)
        # Prevents metadata tags from crushing high-relevance chunks for non-treatment queries.
        if ctype == "recommendation":
            ctype_weight = 1.04
            ctype_bonus = 0.04
        elif ctype == "evidence":
            ctype_weight = 1.03
            ctype_bonus = 0.03
        elif ctype in {"discussion", "implementation", "context", "narrative"}:
            ctype_weight = 1.00
            ctype_bonus = 0.00
        elif ctype == "glossary":
            ctype_weight = 0.98
            ctype_bonus = -0.02
        elif ctype in {"references", "appendix"}:
            ctype_weight = 0.94
            ctype_bonus = -0.06
        else:
            ctype_weight = 1.00
            ctype_bonus = 0.00

        # 3. Clinical Intervention Match Score
        intervention_score = 0.5  # Neutral if no specific drug/therapy in query
        if parsed_query.detected_interventions:
            matches = 0
            for intv_key in parsed_query.detected_interventions:
                expected_secs = INTERVENTION_SECTION_MAP.get(intv_key, set())
                # Check section number or chunk_id match
                if sec in expected_secs or cid in expected_secs:
                    matches += 1.0
                elif any(sec.startswith(es) for es in expected_secs if "." in es):
                    matches += 0.8
                # Lexical check in text
                elif intv_key.replace("_", " ") in text_lower:
                    matches += 0.5

            intervention_score = min(1.0, matches / max(1, len(parsed_query.detected_interventions)))

        # 4. Population / Constraint Match Score
        population_score = 0.5  # Neutral if general adult population
        if parsed_query.detected_populations:
            pop_matches = 0
            for pop_key in parsed_query.detected_populations:
                expected_pop_secs = POPULATION_SECTION_MAP.get(pop_key, set())
                if sec in expected_pop_secs or cid in expected_pop_secs:
                    pop_matches += 1.0
                elif pop_key.replace("_", " ") in text_lower:
                    pop_matches += 0.7
                elif pop_key == "pregnant_women" and ("pregnant" in text_lower or "pregnancy" in text_lower):
                    pop_matches += 1.0
                elif pop_key == "adolescents_young_people" and ("adolescent" in text_lower or "young" in text_lower or "children" in text_lower):
                    pop_matches += 1.0
                elif pop_key == "tuberculosis_patients" and ("tuberculosis" in text_lower or "tb" in text_lower):
                    pop_matches += 1.0
                elif pop_key == "seizure_disorder_patients" and ("seizure" in text_lower or "epilepsy" in text_lower):
                    pop_matches += 1.0

            population_score = min(1.0, pop_matches / max(1, len(parsed_query.detected_populations)))

        # 5. Generic Hub Chunk Penalty (acknowledgements / preface / table of contents)
        hub_penalty = 0.0
        if cid.startswith("chunk_node_L1_acknowledgements") or cid.startswith("chunk_node_L1_preface"):
            hub_penalty = 0.20
        elif ctype == "references" and not ("reference" in parsed_query.raw_query.lower()):
            hub_penalty = 0.15

        # 6. Unified Calibrated Clinical Score
        # Direct evidence relevance dominates; entity alignment modulates when present
        if parsed_query.detected_interventions or parsed_query.detected_populations:
            base_score = (
                (relevance_score * 0.50)
                + (intervention_score * 0.30)
                + (population_score * 0.20)
            )
        else:
            base_score = relevance_score

        final_clinical_score = max(0.0, min(1.0, base_score + ctype_bonus - hub_penalty))

        return RerankedCandidate(
            chunk_id=cid,
            clinical_score=round(float(final_clinical_score), 4),
            rerank_position=0,  # assigned after sorting
            initial_hybrid_rank=candidate.hybrid_rank,
            semantic_score=round(float(dense_rel), 4),
            intervention_match_score=round(float(intervention_score), 4),
            population_match_score=round(float(population_score), 4),
            content_type_weight=round(float(ctype_weight), 2),
            text=candidate.text,
            section_number=candidate.section_number,
            section_title=candidate.section_title,
            heading_path=candidate.heading_path,
            physical_page_start=candidate.physical_page_start,
            physical_page_end=candidate.physical_page_end,
            printed_page_start=candidate.printed_page_start,
            printed_page_end=candidate.printed_page_end,
            content_type=candidate.content_type,
            retrieval_role=candidate.retrieval_role,
            document_id=candidate.document_id,
            node_id=candidate.node_id,
            parent_id=candidate.parent_id,
            token_count=candidate.token_count,
        )

    def rerank(
        self,
        candidates: List[HybridSearchResult],
        parsed_query: ClinicalQueryRepresentation,
        top_k: int = 5,
    ) -> List[RerankedCandidate]:
        """
        Reranks candidates and selects a complementary, diversified evidence set
        using Maximal Marginal Relevance (MMR) over clinical relevance and section redundancy.
        """
        if not candidates:
            return []

        scored: List[RerankedCandidate] = []
        for cand in candidates:
            sc = self.score_candidate(cand, parsed_query)
            scored.append(sc)

        # Sort pool initially strictly descending by clinical_score
        candidate_pool = sorted(
            scored,
            key=lambda item: (item.clinical_score, -item.initial_hybrid_rank),
            reverse=True,
        )

        if not top_k or top_k <= 1:
            for i, item in enumerate(candidate_pool, start=1):
                item.rerank_position = i
        # Greedy Query-Aware Coverage Selection for Evidence-Set Diversification
        selected: List[RerankedCandidate] = []
        remaining = list(candidate_pool)

        # Track covered intervention concepts in selected evidence set
        covered_concepts: Set[str] = set()

        def get_chunk_covered_concepts(cand: RerankedCandidate) -> Set[str]:
            covered = set()
            cand_text = cand.text.lower()
            cand_sec = cand.section_number or ""
            for intv in parsed_query.detected_interventions:
                expected_secs = INTERVENTION_SECTION_MAP.get(intv, set())
                if cand_sec in expected_secs or cand.chunk_id in expected_secs:
                    covered.add(intv)
                elif any(cand_sec.startswith(es) for es in expected_secs if "." in es):
                    covered.add(intv)
                elif intv.replace("_", " ") in cand_text:
                    covered.add(intv)
            return covered

        # First slot: Highest-relevance clinical leader
        leader = remaining.pop(0)
        selected.append(leader)
        covered_concepts.update(get_chunk_covered_concepts(leader))

        target_size = min(top_k, len(candidate_pool))
        while remaining and len(selected) < target_size:
            best_idx = 0
            best_utility_score = -999.0

            for idx, cand in enumerate(remaining):
                relevance = cand.clinical_score

                # 1. Coverage Gain: Bonus if candidate covers a query dimension not yet covered
                cand_concepts = get_chunk_covered_concepts(cand)
                novel_concepts = cand_concepts - covered_concepts
                coverage_gain = 0.08 * len(novel_concepts) if novel_concepts else 0.0

                # 2. Evidence Role Complementarity: Bonus if candidate provides quantitative evidence/conclusions
                # when leader was recommendation, or vice versa
                selected_roles = {sel.retrieval_role for sel in selected}
                if cand.retrieval_role not in selected_roles and cand.retrieval_role in {"primary_evidence", "statistical_support", "recommendation"}:
                    coverage_gain += 0.03

                # 3. Redundancy: Penalize near-duplicate text / exact section overlap only if no novel concepts covered
                cand_sec = cand.section_number or cand.chunk_id
                cand_title = cand.section_title or ""

                max_redundancy = 0.0
                for sel in selected:
                    sel_sec = sel.section_number or sel.chunk_id
                    sel_title = sel.section_title or ""

                    if cand_sec == sel_sec:
                        # If candidate brings a novel concept or distinct content type (e.g. table vs recommendation), mild penalty
                        if novel_concepts or cand.content_type != sel.content_type:
                            redundancy = 0.03
                        else:
                            redundancy = 0.08
                    elif cand_title and cand_title == sel_title:
                        redundancy = 0.04
                    else:
                        redundancy = 0.0

                    if redundancy > max_redundancy:
                        max_redundancy = redundancy

                utility_score = relevance + coverage_gain - max_redundancy

                if utility_score > best_utility_score:
                    best_utility_score = utility_score
                    best_idx = idx

            chosen = remaining.pop(best_idx)
            selected.append(chosen)
            covered_concepts.update(get_chunk_covered_concepts(chosen))

        # Assign 1-indexed rerank position
        for i, item in enumerate(selected, start=1):
            item.rerank_position = i

        return selected
