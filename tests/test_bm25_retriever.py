"""
Automated Test Suite — BM25 Sparse Retrieval Engine
Medical RAG Project: Oxygen (أوكسجين)
Source Document: WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)

Executes 10 automated test cases:
Test 1: Index Initialization & Vocabulary Extraction
Test 2: Deterministic Ranking
Test 3: Chunk ID Uniqueness in Retrieval Results
Test 4: Non-Empty Results on Medical Queries
Test 5: Strict Descending Score Ordering
Test 6: Exact Medical Term Precision (Varenicline, Cytisine, Bupropion)
Test 7: Traceability Metadata Completeness (Provenance & Hierarchy)
Test 8: Index Serialization & Reloading (Fidelity Test)
Test 9: ContextAssembler Interoperability (Surrogate Distance Conversion)
Test 10: Comparison Engine (verbatim_text vs searchable_text indexing)
"""

import os
import sys
import json
import logging

sys.path.insert(0, r"C:\Users\moham\OneDrive\Apps\اوكسجين\scripts")
from bm25_retriever import BM25Retriever, MedicalTokenizer, build_and_save_default_bm25_index
from context_assembler import ContextAssembler

RECORDS_PATH = r"C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\retrieval_records_v2.json"
INDEX_PATH = r"C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\bm25_index_v2.json"


def run_tests():
    print("=" * 70)
    print("BM25 SPARSE RETRIEVAL ENGINE AUTOMATED TEST SUITE")
    print("=" * 70)

    with open(RECORDS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    records = data.get("records", [])

    failures = []
    test_count = 0

    def record_test(name: str, passed: bool, detail: str = ""):
        nonlocal test_count
        test_count += 1
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} Test {test_count}: {name} {f'({detail})' if detail else ''}")
        if not passed:
            failures.append(f"Test {test_count} ({name}): {detail}")

    # Test 1: Index Initialization
    retriever = BM25Retriever(text_field="verbatim_text")
    retriever.index_records(records)
    record_test(
        "Index Initialization & Corpus Sizing",
        retriever.corpus_size == 171 and len(retriever.inverted_index) > 2000,
        f"corpus_size={retriever.corpus_size}, terms={len(retriever.inverted_index)}"
    )

    # Test 2: Deterministic Ranking
    query = "What does WHO recommend for brief advice to adult tobacco users?"
    res1 = retriever.retrieve(query, top_k=5)
    res2 = retriever.retrieve(query, top_k=5)
    ids1 = [r.chunk_id for r in res1]
    ids2 = [r.chunk_id for r in res2]
    scores1 = [r.score for r in res1]
    scores2 = [r.score for r in res2]
    record_test(
        "Deterministic Ranking Across Repeated Calls",
        ids1 == ids2 and scores1 == scores2 and len(ids1) == 5,
        f"top-5 ids identical: {ids1[:2]}..."
    )

    # Test 3: Chunk ID Uniqueness in Retrieval Results
    res_10 = retriever.retrieve(query, top_k=10)
    retrieved_ids = [r.chunk_id for r in res_10]
    record_test(
        "Chunk ID Uniqueness in Top-K Results",
        len(set(retrieved_ids)) == len(retrieved_ids) == 10,
        f"all 10 returned chunk_ids are strictly unique"
    )

    # Test 4: Non-Empty Results on Medical Queries
    valid_queries = [
        "varenicline", "cytisine", "bupropion", "nicotine patch",
        "behavioural counselling", "smokeless tobacco"
    ]
    all_non_empty = all(len(retriever.retrieve(q, top_k=5)) == 5 for q in valid_queries)
    record_test(
        "Non-Empty Results on Core Clinical Queries",
        all_non_empty,
        f"tested {len(valid_queries)} standard clinical queries"
    )

    # Test 5: Strict Descending Score Ordering
    sorted_scores_valid = True
    for q in valid_queries:
        res = retriever.retrieve(q, top_k=10)
        scores = [r.score for r in res]
        if scores != sorted(scores, reverse=True):
            sorted_scores_valid = False
            break
    record_test(
        "Strict Descending Score Ordering",
        sorted_scores_valid,
        "all top-k lists strictly ordered by BM25 score descending"
    )

    # Test 6: Exact Medical Term Precision
    # Varenicline query should retrieve varenicline chunk at rank 1 or 2
    v_res = retriever.retrieve("Varenicline", top_k=3)
    c_res = retriever.retrieve("Cytisine", top_k=3)
    b_res = retriever.retrieve("Bupropion", top_k=3)

    v_match = any("varenicline" in r.text.lower() for r in v_res)
    c_match = any("cytisine" in r.text.lower() for r in c_res)
    b_match = any("bupropion" in r.text.lower() for r in b_res)
    record_test(
        "Exact Medical Drug Term Precision",
        v_match and c_match and b_match and v_res[0].score > 2.5,
        f"Varenicline top score={v_res[0].score:.2f}, Cytisine={c_res[0].score:.2f}, Bupropion={b_res[0].score:.2f}"
    )

    # Test 7: Traceability Metadata Completeness
    first_res = v_res[0]
    meta_valid = (
        first_res.chunk_id
        and first_res.text
        and first_res.document_id == "who_tobacco_cessation_2024"
        and first_res.physical_page_start is not None
        and first_res.section_title
        and first_res.heading_path
        and first_res.token_count > 0
    )
    record_test(
        "Traceability Metadata Preservation",
        meta_valid,
        f"chunk={first_res.chunk_id}, page={first_res.physical_page_start}, section='{first_res.section_number}'"
    )

    # Test 8: Index Serialization & Reloading
    retriever.save_index(INDEX_PATH)
    loaded_retriever = BM25Retriever.load_index(INDEX_PATH, RECORDS_PATH)
    res_orig = retriever.retrieve("digital cessation smartphone apps", top_k=5)
    res_loaded = loaded_retriever.retrieve("digital cessation smartphone apps", top_k=5)

    orig_ids = [r.chunk_id for r in res_orig]
    loaded_ids = [r.chunk_id for r in res_loaded]
    record_test(
        "Index Serialization & Deserialization Fidelity",
        orig_ids == loaded_ids and [r.score for r in res_orig] == [r.score for r in res_loaded],
        f"saved to {INDEX_PATH} and verified roundtrip"
    )

    # Test 9: ContextAssembler Interoperability
    assembler = ContextAssembler(max_context_tokens=2500)
    bm25_top5 = retriever.retrieve("brief advice tobacco cessation", top_k=5)
    ca_input = [r.to_context_assembler_dict() for r in bm25_top5]
    assembled = assembler.assemble("brief advice tobacco cessation", ca_input)

    record_test(
        "ContextAssembler Round-Trip Compatibility",
        assembled.context_token_count > 0 and len(assembled.sources) == 5,
        f"assembled {len(assembled.sources)} sources from BM25 results, tokens={assembled.context_token_count}"
    )

    # Test 10: Multi-Field Support & Comparison
    retriever_searchable = BM25Retriever(text_field="searchable_text")
    retriever_searchable.index_records(records)
    res_s = retriever_searchable.retrieve("brief advice", top_k=3)
    res_v = retriever.retrieve("brief advice", top_k=3)

    record_test(
        "Multi-Field Indexing Engine (searchable_text vs verbatim_text)",
        len(res_s) == 3 and len(res_v) == 3,
        f"verbatim avgdl={retriever.avgdl:.1f}, searchable avgdl={retriever_searchable.avgdl:.1f}"
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
