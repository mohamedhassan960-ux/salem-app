"""
BM25 Evaluation Benchmark & Comparative Analysis — Medical RAG: Oxygen (أوكسجين)
Source Document: WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)

Compares:
- Strategy A: verbatim_text indexing
- Strategy B: searchable_text (breadcrumb-enriched) indexing

Computes:
- Recall@5
- Recall@10
- MRR (Mean Reciprocal Rank)
- Per-query diagnostic analysis (successes vs failures)
"""

from __future__ import annotations

import os
import sys
import json
import logging
from dataclasses import dataclass
from typing import Dict, List, Any, Set, Tuple

sys.path.insert(0, r"C:\Users\moham\OneDrive\Apps\اوكسجين\scripts")
from bm25_retriever import BM25Retriever

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


# ─────────────────────────────────────────────────────────────────────────────
# Canonical Medical Evaluation Dataset
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class EvalQuery:
    query_id: str
    category: str
    query_text: str
    relevant_chunk_ids: List[str]
    description: str


EVALUATION_DATASET: List[EvalQuery] = [
    # 1. Medications & Drug Names
    EvalQuery(
        query_id="Q01_varenicline_rec",
        category="Medications",
        query_text="What does WHO recommend regarding Varenicline for tobacco cessation?",
        relevant_chunk_ids=["chunk_sec_3_3_1", "chunk_sec_3_3_3_3_p01", "chunk_sec_3_3_3_3_p02", "chunk_node_L1_glossary_of_terms_p27"],
        description="Varenicline clinical recommendation and evidence"
    ),
    EvalQuery(
        query_id="Q02_cytisine_evidence",
        category="Medications",
        query_text="Is Cytisine effective and recommended for smoking cessation?",
        relevant_chunk_ids=["chunk_sec_3_3_1", "chunk_sec_3_3_3_4", "chunk_node_L1_glossary_of_terms_p07"],
        description="Cytisine efficacy and clinical recommendation"
    ),
    EvalQuery(
        query_id="Q03_bupropion_sr",
        category="Medications",
        query_text="What is the evidence and recommendation for Bupropion sustained release?",
        relevant_chunk_ids=["chunk_sec_3_3_1", "chunk_sec_3_3_3_2", "chunk_node_L1_glossary_of_terms_p04"],
        description="Bupropion recommendation and evidence"
    ),
    EvalQuery(
        query_id="Q04_combo_nrt",
        category="Medications",
        query_text="Combination pharmacotherapy combining nicotine patch with short-acting NRT",
        relevant_chunk_ids=["chunk_sec_3_3_1", "chunk_sec_3_3_3_5", "chunk_node_L1_glossary_of_terms_p05"],
        description="Combination NRT evidence and definition"
    ),

    # 2. Recommendations & Behavioural Interventions
    EvalQuery(
        query_id="Q05_brief_advice",
        category="Recommendations",
        query_text="WHO recommendations for brief advice duration in health-care settings",
        relevant_chunk_ids=["chunk_sec_3_1_1", "chunk_sec_3_1_3_p01", "chunk_node_L1_glossary_of_terms_p03"],
        description="Brief advice (30s-3min) recommendation"
    ),
    EvalQuery(
        query_id="Q06_intensive_counselling",
        category="Recommendations",
        query_text="Intensive behavioural support options including individual and group counselling",
        relevant_chunk_ids=["chunk_sec_3_1_1", "chunk_sec_3_1_3_p02", "chunk_sec_3_1_3_p03", "chunk_node_L1_glossary_of_terms_p10", "chunk_node_L1_glossary_of_terms_p11", "chunk_node_L1_glossary_of_terms_p12"],
        description="Intensive behavioural support modalities"
    ),
    EvalQuery(
        query_id="Q07_digital_interventions",
        category="Recommendations",
        query_text="Digital interventions text messaging and smartphone apps for cessation",
        relevant_chunk_ids=["chunk_sec_3_2_1", "chunk_sec_3_2_3_p01", "chunk_node_L1_glossary_of_terms_p08", "chunk_node_L1_glossary_of_terms_p16", "chunk_node_L1_glossary_of_terms_p19"],
        description="Digital tools and apps for cessation"
    ),
    EvalQuery(
        query_id="Q08_smokeless_tobacco",
        category="Recommendations",
        query_text="Interventions for smokeless tobacco use cessation",
        relevant_chunk_ids=["chunk_sec_3_4_1", "chunk_sec_3_4_3_p01", "chunk_node_L1_glossary_of_terms_p20"],
        description="Smokeless tobacco treatment recommendations"
    ),
    EvalQuery(
        query_id="Q09_system_interventions",
        category="Recommendations",
        query_text="System-level interventions and financial coverage for cessation treatments",
        relevant_chunk_ids=["chunk_sec_3_7_1", "chunk_sec_3_7_3_p01", "chunk_node_L1_glossary_of_terms_p10"],
        description="Health system level policies and cost coverage"
    ),

    # 3. Clinical Terminology & Glossary
    EvalQuery(
        query_id="Q10_abstinence_definitions",
        category="Terminology",
        query_text="Definition of continuous abstinence versus point prevalence abstinence",
        relevant_chunk_ids=["chunk_node_L1_glossary_of_terms_p22", "chunk_sec_2_2_p01"],
        description="Definitions of tobacco cessation and abstinence"
    ),
    EvalQuery(
        query_id="Q11_grade_methodology",
        category="Terminology",
        query_text="GRADE criteria for certainty of evidence and strength of recommendations",
        relevant_chunk_ids=["chunk_sec_2_3_p01", "chunk_sec_2_3_p02", "chunk_node_L1_abbreviations_and_acronym"],
        description="GRADE methodology for evidence grading"
    ),
    EvalQuery(
        query_id="Q12_telephone_quitline",
        category="Terminology",
        query_text="Toll-free telephone quitline remote counselling support",
        relevant_chunk_ids=["chunk_node_L1_glossary_of_terms_p14", "chunk_sec_3_1_1", "chunk_sec_3_1_3_p04"],
        description="Quitline telephone counselling details"
    ),

    # 4. Paraphrased / Natural Clinical Questions (Wording Gap)
    EvalQuery(
        query_id="Q13_pregnant_management",
        category="Paraphrased",
        query_text="How should health providers manage tobacco cessation in pregnant women?",
        relevant_chunk_ids=["chunk_sec_3_3_4_p01", "chunk_sec_3_3_4_p02", "chunk_sec_3_1_4"],
        description="Pregnancy considerations for cessation"
    ),
    EvalQuery(
        query_id="Q14_non_nicotine_craving_pills",
        category="Paraphrased",
        query_text="What non-nicotine pills are approved to reduce cigarette cravings?",
        relevant_chunk_ids=["chunk_sec_3_3_1", "chunk_sec_3_3_3_2", "chunk_sec_3_3_3_3_p01", "chunk_sec_3_3_3_4", "chunk_node_L1_glossary_of_terms_p04", "chunk_node_L1_glossary_of_terms_p07"],
        description="Paraphrased request for non-nicotine pharmacotherapy"
    ),
    EvalQuery(
        query_id="Q15_alternative_therapies",
        category="Paraphrased",
        query_text="Is acupuncture or hypnosis recommended for stopping smoking?",
        relevant_chunk_ids=["chunk_sec_3_6_1", "chunk_sec_3_6_3_p01", "chunk_node_L1_glossary_of_terms_p26"],
        description="Alternative therapies (acupuncture, hypnotherapy) recommendation"
    ),
    EvalQuery(
        query_id="Q16_ai_chatbots",
        category="Paraphrased",
        query_text="Can chatbots and artificial intelligence help patients quit smoking?",
        relevant_chunk_ids=["chunk_sec_3_2_1", "chunk_sec_3_2_3_p02", "chunk_node_L1_glossary_of_terms_p01", "chunk_node_L1_glossary_of_terms_p06"],
        description="Conversational AI and chatbot cessation tools"
    ),

    # 5. Exact Acronyms & Frameworks
    EvalQuery(
        query_id="Q17_mpower_framework",
        category="Acronyms",
        query_text="MPOWER measures for tobacco control",
        relevant_chunk_ids=["chunk_node_L1_abbreviations_and_acronym", "chunk_sec_1_1"],
        description="MPOWER package definition"
    ),
    EvalQuery(
        query_id="Q18_pico_gdg_process",
        category="Acronyms",
        query_text="PICO questions and Guideline Development Group GDG decision making",
        relevant_chunk_ids=["chunk_sec_2_1", "chunk_sec_2_3_p01", "chunk_node_L1_abbreviations_and_acronym"],
        description="PICO questions and GDG role"
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
# Evaluation Engine
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_retriever(
    retriever: BM25Retriever,
    dataset: List[EvalQuery],
    top_k_max: int = 10,
) -> Dict[str, Any]:
    """
    Evaluates a BM25 retriever against the benchmark dataset.
    Computes Recall@5, Recall@10, MRR, and per-query logs.
    """
    recall_5_count = 0
    recall_10_count = 0
    mrr_sum = 0.0
    query_details: List[Dict[str, Any]] = []

    for eq in dataset:
        results = retriever.retrieve(eq.query_text, top_k=top_k_max)
        retrieved_ids = [r.chunk_id for r in results]
        relevant_set = set(eq.relevant_chunk_ids)

        # Check hits
        hit_at_5 = any(cid in relevant_set for cid in retrieved_ids[:5])
        hit_at_10 = any(cid in relevant_set for cid in retrieved_ids[:10])

        if hit_at_5:
            recall_5_count += 1
        if hit_at_10:
            recall_10_count += 1

        # Reciprocal Rank (position of first relevant hit)
        first_rank = None
        for rank, cid in enumerate(retrieved_ids, start=1):
            if cid in relevant_set:
                first_rank = rank
                break

        rr = 1.0 / first_rank if first_rank is not None else 0.0
        mrr_sum += rr

        query_details.append({
            "query_id": eq.query_id,
            "category": eq.category,
            "query_text": eq.query_text,
            "relevant_target_count": len(eq.relevant_chunk_ids),
            "retrieved_top_5": [
                {"chunk_id": r.chunk_id, "score": r.score, "section": r.section_number, "page": r.physical_page_start, "hit": r.chunk_id in relevant_set}
                for r in results[:5]
            ],
            "hit_at_5": hit_at_5,
            "hit_at_10": hit_at_10,
            "first_hit_rank": first_rank,
            "reciprocal_rank": rr,
        })

    num_queries = len(dataset)
    recall_at_5 = (recall_5_count / num_queries) if num_queries > 0 else 0.0
    recall_at_10 = (recall_10_count / num_queries) if num_queries > 0 else 0.0
    mrr = (mrr_sum / num_queries) if num_queries > 0 else 0.0

    return {
        "text_field": retriever.text_field,
        "total_queries": num_queries,
        "recall_at_5": round(recall_at_5, 4),
        "recall_at_10": round(recall_at_10, 4),
        "mrr": round(mrr, 4),
        "recall_5_hits": recall_5_count,
        "recall_10_hits": recall_10_count,
        "query_details": query_details,
    }


def run_comparative_benchmark(
    records_path: str = r"C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\retrieval_records_v2.json",
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Runs evaluation on both verbatim_text and searchable_text index strategies."""
    with open(records_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    records = data.get("records", [])

    # Strategy A: verbatim_text
    retriever_a = BM25Retriever(text_field="verbatim_text")
    retriever_a.index_records(records)
    eval_a = evaluate_retriever(retriever_a, EVALUATION_DATASET)

    # Strategy B: searchable_text
    retriever_b = BM25Retriever(text_field="searchable_text")
    retriever_b.index_records(records)
    eval_b = evaluate_retriever(retriever_b, EVALUATION_DATASET)

    return eval_a, eval_b


if __name__ == "__main__":
    eval_a, eval_b = run_comparative_benchmark()
    print("=" * 60)
    print("BM25 COMPARATIVE EVALUATION RESULTS")
    print("=" * 60)
    print(f"Strategy A (verbatim_text):   Recall@5 = {eval_a['recall_at_5']*100:.1f}%, Recall@10 = {eval_a['recall_at_10']*100:.1f}%, MRR = {eval_a['mrr']:.4f}")
    print(f"Strategy B (searchable_text): Recall@5 = {eval_b['recall_at_5']*100:.1f}%, Recall@10 = {eval_b['recall_at_10']*100:.1f}%, MRR = {eval_b['mrr']:.4f}")
    print("=" * 60)
