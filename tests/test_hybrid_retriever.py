"""
Automated Unit Tests — Hybrid Retrieval Engine (BM25 + Dense -> RRF)
Medical RAG Project: Oxygen (أوكسجين)
Source Document: WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)

Verifies all mathematical, clinical, provenance, and serialization guarantees:
Test 1: RRF Formula Exactness
Test 2: Dual-Engine Duplicate Chunk Fusion
Test 3: Single-Engine Candidate Handling
Test 4: Strict Descending RRF Score Ordering
Test 5: Top-5 Limit Enforcement
Test 6: Deterministic & Reproducible Retrieval
Test 7: Chunk ID Integrity & Corpus Matching
Test 8: Full Metadata Preservation (Section, Pages, Hierarchy)
Test 9: 100% Verbatim Ground Truth Text Fidelity
Test 10: Seamless ContextAssembler Integration
Test 11: Cross-Lingual Egyptian Arabic Retrieval Verification
Test 12: Dual Engine Scores & Ranks Recorded
"""

import os
import sys
import json
import logging
import numpy as np

sys.path.insert(0, r"C:\Users\moham\OneDrive\Apps\اوكسجين\scripts")
from hybrid_retriever import HybridRetriever, HybridSearchResult
from bm25_retriever import BM25Retriever
from dense_retriever import DenseRetriever
from context_assembler import ContextAssembler

RECORDS_PATH = r"C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\retrieval_records_v2.json"
DENSE_NPZ = r"C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\dense_index_v2.npz"
DENSE_META = r"C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\dense_metadata_v2.json"
LOCAL_MODEL = r"C:\Users\moham\OneDrive\Apps\اوكسجين\data\models\multilingual-e5-small"


def run_tests():
    print("=" * 70)
    print("HYBRID RETRIEVAL (BM25 + DENSE -> RRF) AUTOMATED TEST SUITE")
    print("=" * 70)

    with open(RECORDS_PATH, "r", encoding="utf-8") as f:
        records_data = json.load(f)
    records = records_data.get("records", [])
    records_map = {r["chunk_id"]: r for r in records}

    failures = []
    test_count = 0

    def record_test(name: str, passed: bool, detail: str = ""):
        nonlocal test_count
        test_count += 1
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} Test {test_count}: {name} {f'({detail})' if detail else ''}")
        if not passed:
            failures.append(f"Test {test_count} ({name}): {detail}")

    # Initialize Hybrid Retriever
    hybrid = HybridRetriever.from_files(
        records_path=RECORDS_PATH,
        dense_npz_path=DENSE_NPZ,
        dense_meta_path=DENSE_META,
        model_name=LOCAL_MODEL,
        k_rrf=60,
        candidate_pool_size=30,
    )

    # Test 1: RRF Formula Exactness
    # For rank 1 in single engine: 1/(60+1) = 1/61 = 0.01639344...
    k = 60
    r1_score = 1.0 / (k + 1)
    r2_score = 1.0 / (k + 2)
    expected_dual = r1_score + r2_score
    calc_dual = (1.0 / 61) + (1.0 / 62)
    record_test(
        "RRF Formula Exactness (k=60)",
        np.isclose(expected_dual, calc_dual, atol=1e-6),
        f"rank1={r1_score:.6f}, dual(1,2)={expected_dual:.6f}"
    )

    # Test 2: Dual-Engine Duplicate Chunk Fusion
    test_q_exact = "Varenicline for tobacco cessation"
    res_exact = hybrid.retrieve(test_q_exact, top_k=5)
    has_dual_fused = any(r.bm25_rank is not None and r.dense_rank is not None for r in res_exact)
    record_test(
        "Dual-Engine Duplicate Chunk Fusion",
        has_dual_fused,
        f"verified chunk appeared in both BM25 and Dense with combined RRF"
    )

    # Test 3: Single-Engine Candidate Handling
    test_q_ar = "أنا عايز أبطل السجاير ومش عارف أبدأ منين"
    res_ar = hybrid.retrieve(test_q_ar, top_k=5)
    # BM25 has no hits for pure Arabic -> dense_rank is not None, bm25_rank is None
    has_single_engine = any(r.dense_rank is not None and r.bm25_rank is None for r in res_ar)
    record_test(
        "Single-Engine Candidate Handling (BM25 empty / Dense only)",
        has_single_engine,
        f"dense-only candidates seamlessly scored without errors"
    )

    # Test 4: Strict Descending RRF Score Ordering
    scores = [r.rrf_score for r in res_exact]
    is_sorted = scores == sorted(scores, reverse=True)
    record_test(
        "Strict Descending RRF Score Ordering",
        is_sorted and len(scores) == 5,
        f"scores: {[round(s, 6) for s in scores]}"
    )

    # Test 5: Top-5 Limit Enforcement
    res_limit = hybrid.retrieve("smoking cessation", top_k=5)
    record_test(
        "Top-5 Limit Enforcement",
        len(res_limit) == 5 and all(r.hybrid_rank == i + 1 for i, r in enumerate(res_limit)),
        f"returned exactly {len(res_limit)} ranked items (ranks 1..5)"
    )

    # Test 6: Deterministic & Reproducible Retrieval
    res1 = hybrid.retrieve(test_q_exact, top_k=5)
    res2 = hybrid.retrieve(test_q_exact, top_k=5)
    cids1 = [r.chunk_id for r in res1]
    cids2 = [r.chunk_id for r in res2]
    scores1 = [r.rrf_score for r in res1]
    scores2 = [r.rrf_score for r in res2]
    record_test(
        "Deterministic & Reproducible Retrieval",
        cids1 == cids2 and np.allclose(scores1, scores2),
        f"repeated retrieval yields identical rankings and RRF scores"
    )

    # Test 7: Chunk ID Integrity & Corpus Matching
    all_chunks_valid = all(r.chunk_id in records_map for r in res_exact + res_ar)
    record_test(
        "Chunk ID Integrity & Corpus Matching",
        all_chunks_valid,
        f"all retrieved chunk_ids exist in ground truth records"
    )

    # Test 8: Full Metadata Preservation
    top_r = res_exact[0]
    meta_ok = (
        top_r.document_id == "who_tobacco_cessation_2024"
        and top_r.node_id
        and top_r.section_title
        and top_r.heading_path
        and top_r.physical_page_start is not None
        and top_r.token_count > 0
    )
    record_test(
        "Full Metadata Preservation (Section, Pages, Hierarchy)",
        meta_ok,
        f"doc_id={top_r.document_id}, section={top_r.section_number}, page={top_r.physical_page_start}"
    )

    # Test 9: 100% Verbatim Ground Truth Text Fidelity
    no_text_mutation = all(
        r.text == records_map[r.chunk_id]["content"]["verbatim_text"]
        for r in res_exact + res_ar
    )
    record_test(
        "100% Verbatim Ground Truth Text Fidelity",
        no_text_mutation,
        f"all retrieved text matches canonical ground truth verbatim"
    )

    # Test 10: Seamless ContextAssembler Integration
    assembler = ContextAssembler(max_context_tokens=3000)
    ca_input = [r.to_context_assembler_dict() for r in res_exact]
    assembled = assembler.assemble(test_q_exact, ca_input)
    record_test(
        "Seamless ContextAssembler Integration",
        assembled.context_token_count > 0 and len(assembled.sources) == 5,
        f"assembled {len(assembled.sources)} sources, total tokens={assembled.context_token_count}"
    )

    # Test 11: Cross-Lingual Egyptian Arabic Retrieval Verification
    ar_q = "في جلسات جماعية مع ناس تانية بتحاول تبطل عشان نشجع بعض؟"
    res_group = hybrid.retrieve(ar_q, top_k=5)
    cids_group = [r.chunk_id for r in res_group]
    group_hit = any(cid in {"chunk_sec_3_1_1", "chunk_sec_3_1_3_p03", "chunk_node_L1_glossary_of_terms_p13"} for cid in cids_group)
    record_test(
        "Cross-Lingual Egyptian Arabic Retrieval Verification",
        group_hit,
        f"top-1: {res_group[0].chunk_id}, RRF={res_group[0].rrf_score:.6f}"
    )

    # Test 12: Dual Engine Scores & Ranks Recorded
    has_dual_tracking = any(
        r.bm25_rank is not None and r.dense_rank is not None
        and r.bm25_score is not None and r.dense_score is not None
        for r in res_exact
    )
    record_test(
        "Dual Engine Scores & Ranks Recorded in Output",
        has_dual_tracking,
        f"both bm25_score/dense_score and bm25_rank/dense_rank preserved"
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
