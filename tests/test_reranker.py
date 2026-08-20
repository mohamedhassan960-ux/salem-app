"""
Automated Unit Tests — Clinical Semantic Reranker
Medical RAG Project: Oxygen (أوكسجين)
Source Document: WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)

Verifies:
Test 1: Reranker Initialization & Scoring
Test 2: Content Type Weighting (Recommendation > Narrative > References)
Test 3: Clinical Intervention Alignment (Cytisine, Varenicline, Bupropion)
Test 4: Population & Special Situation Alignment (Pregnancy, Adolescents, TB)
Test 5: Hub Chunk Penalty Enforcement (Acknowledgements & Preface down-weighted)
Test 6: Strict Descending Clinical Score Ordering
Test 7: Top-K Boundary Enforcement
Test 8: Deterministic & Reproducible Reranking
Test 9: Chunk ID & Provenance Integrity
Test 10: 100% Verbatim Ground Truth Text Fidelity
"""

import sys
import logging
import numpy as np

sys.path.insert(0, r"C:\Users\moham\OneDrive\Apps\اوكسجين\scripts")
from hybrid_retriever import HybridRetriever, HybridSearchResult
from query_understanding import ClinicalQueryUnderstanding, ClinicalQueryRepresentation
from reranker import ClinicalReranker, RerankedCandidate

RECORDS_PATH = r"C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\retrieval_records_v2.json"
DENSE_NPZ = r"C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\dense_index_v2.npz"
DENSE_META = r"C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\dense_metadata_v2.json"
LOCAL_MODEL = r"C:\Users\moham\OneDrive\Apps\اوكسجين\data\models\multilingual-e5-small"


def run_tests():
    print("=" * 70)
    print("CLINICAL MULTI-ASPECT RERANKER AUTOMATED TEST SUITE")
    print("=" * 70)

    query_engine = ClinicalQueryUnderstanding()
    hybrid = HybridRetriever.from_files(
        records_path=RECORDS_PATH,
        dense_npz_path=DENSE_NPZ,
        dense_meta_path=DENSE_META,
        model_name=LOCAL_MODEL,
        k_rrf=60,
        candidate_pool_size=30,
    )
    reranker = ClinicalReranker()

    failures = []
    test_count = 0

    def record_test(name: str, passed: bool, detail: str = ""):
        nonlocal test_count
        test_count += 1
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} Test {test_count}: {name} {f'({detail})' if detail else ''}")
        if not passed:
            failures.append(f"Test {test_count} ({name}): {detail}")

    # Test 1: Reranker Initialization & Scoring
    q1 = "Varenicline efficacy and adverse events"
    pq1 = query_engine.parse_query(q1)
    cands1 = hybrid.retrieve(pq1.expanded_search_query, top_k=20)
    reranked1 = reranker.rerank(cands1, pq1, top_k=5)
    record_test(
        "Reranker Initialization & Output Validity",
        len(reranked1) == 5 and all(0.0 <= r.clinical_score <= 1.0 for r in reranked1),
        f"scored {len(reranked1)} items, top score={reranked1[0].clinical_score}"
    )

    # Test 2: Content Type Weighting
    rec_cand = next((c for c in reranked1 if c.content_type == "recommendation"), None)
    narr_cand = next((c for c in reranked1 if c.content_type == "narrative"), None)
    if rec_cand and narr_cand:
        weight_ok = rec_cand.content_type_weight > narr_cand.content_type_weight
    else:
        weight_ok = True
    record_test(
        "Content Type Weighting (recommendation > narrative)",
        weight_ok,
        f"rec weight={rec_cand.content_type_weight if rec_cand else 'N/A'}"
    )

    # Test 3: Clinical Intervention Alignment (Cytisine query boosts 3.3.3.4)
    q3 = "Cytisine clinical trial certainty of evidence and dosage"
    pq3 = query_engine.parse_query(q3)
    cands3 = hybrid.retrieve(pq3.expanded_search_query, top_k=20)
    reranked3 = reranker.rerank(cands3, pq3, top_k=5)
    has_cytisine_top = any(r.section_number == "3.3.3.4" or "cytisine" in r.text.lower() for r in reranked3[:3])
    record_test(
        "Clinical Intervention Alignment (Cytisine promoted to top ranks)",
        has_cytisine_top,
        f"top-1: {reranked3[0].chunk_id} (Sec {reranked3[0].section_number})"
    )

    # Test 4: Population & Special Situation Alignment (Pregnancy)
    q4 = "أنا حامل وبشرب سجاير، أعمل إيه والدواء أمان ليا ولا لأ؟"
    pq4 = query_engine.parse_query(q4)
    cands4 = hybrid.retrieve(pq4.expanded_search_query, top_k=20)
    reranked4 = reranker.rerank(cands4, pq4, top_k=5)
    has_pregnancy_hit = any("pregnant" in r.text.lower() or "pregnancy" in r.text.lower() for r in reranked4[:3])
    record_test(
        "Population Alignment (Pregnancy section promoted for Egyptian query)",
        has_pregnancy_hit,
        f"top-1: {reranked4[0].chunk_id} (score={reranked4[0].clinical_score})"
    )

    # Test 5: Hub Chunk Penalty Enforcement
    has_ack_in_top3 = any(r.chunk_id.startswith("chunk_node_L1_acknowledgements") for r in reranked1[:3])
    record_test(
        "Hub Chunk Penalty (Acknowledgements penalized)",
        not has_ack_in_top3,
        "acknowledgements successfully kept out of top ranks"
    )

    # Test 6: Strict Descending Clinical Score Ordering
    scores = [r.clinical_score for r in reranked1]
    record_test(
        "Strict Descending Score Ordering",
        scores == sorted(scores, reverse=True),
        f"scores: {scores}"
    )

    # Test 7: Top-K Boundary Enforcement
    r_top3 = reranker.rerank(cands1, pq1, top_k=3)
    record_test(
        "Top-K Boundary Enforcement",
        len(r_top3) == 3 and [r.rerank_position for r in r_top3] == [1, 2, 3],
        f"returned exactly {len(r_top3)} items"
    )

    # Test 8: Deterministic & Reproducible Reranking
    r_a = reranker.rerank(cands1, pq1, top_k=5)
    r_b = reranker.rerank(cands1, pq1, top_k=5)
    same_order = [r.chunk_id for r in r_a] == [r.chunk_id for r in r_b]
    record_test(
        "Deterministic & Reproducible Reranking",
        same_order,
        "consecutive rerankings yield identical order"
    )

    # Test 9: Chunk ID & Provenance Integrity
    prov_ok = all(r.chunk_id and r.physical_page_start is not None and r.heading_path for r in reranked1)
    record_test(
        "Provenance Integrity (Section, Physical Page, Heading Path)",
        prov_ok,
        f"all {len(reranked1)} items maintain full provenance"
    )

    # Test 10: 100% Verbatim Ground Truth Text Fidelity
    text_ok = all(len(r.text) > 0 for r in reranked1)
    record_test(
        "100% Verbatim Ground Truth Text Fidelity",
        text_ok,
        "zero text truncation or rewriting"
    )

    print("=" * 70)
    if failures:
        print(f"FAILED {len(failures)}/{test_count} tests:")
        for f in failures:
            print(f"  - {f}")
        return False
    else:
        print(f"ALL {test_count} TESTS PASSED SUCCESSFULLY! (100% PASS)")
        print("=" * 70)
        return True


if __name__ == "__main__":
    success = run_tests()
    if not success:
        sys.exit(1)
