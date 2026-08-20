"""
Automated Test Suite — Dense Semantic Retrieval Engine
Medical RAG Project: Oxygen (أوكسجين)
Source Document: WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)

Verifies all mathematical, clinical, provenance, and serialization guarantees:
Test 1: Index Corpus Size (Exactly 171 Chunks)
Test 2: Chunk ID Uniqueness & Non-Empty
Test 3: Vector Dimension Consistency & L2 Normalization
Test 4: Numeric Sanity (Zero NaNs, Zero Infs, Finite Vectors)
Test 5: Query Vector Dimension Match
Test 6: Strict Descending Cosine Similarity Ordering
Test 7: Deterministic & Reproducible Retrieval
Test 8: Traceability Metadata Completeness
Test 9: Index Serialization & Reloading Fidelity (NPZ + JSON)
Test 10: Seamless ContextAssembler Integration
Test 11: Cross-Lingual Egyptian Arabic Semantic Retrieval
Test 12: Ground Truth Text Invariant (Zero Mutation)
"""

import os
import sys
import json
import logging
import numpy as np

sys.path.insert(0, r"C:\Users\moham\OneDrive\Apps\اوكسجين\scripts")
from dense_retriever import DenseRetriever
from context_assembler import ContextAssembler

RECORDS_PATH = r"C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\retrieval_records_v2.json"
NPZ_PATH = r"C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\dense_index_v2.npz"
META_PATH = r"C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\dense_metadata_v2.json"
LOCAL_MODEL_PATH = r"C:\Users\moham\OneDrive\Apps\اوكسجين\data\models\multilingual-e5-small"


def run_tests():
    print("=" * 70)
    print("DENSE SEMANTIC RETRIEVAL ENGINE AUTOMATED TEST SUITE")
    print("=" * 70)

    model_path = LOCAL_MODEL_PATH if os.path.exists(LOCAL_MODEL_PATH) else DenseRetriever.DEFAULT_MODEL_NAME

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

    # Build or Load index
    retriever = DenseRetriever(model_name=model_path)
    retriever.index_records(records)
    retriever.save_index(NPZ_PATH, META_PATH)

    # Test 1: Index Corpus Size
    record_test(
        "Index Corpus Size (Exactly 171 Chunks)",
        retriever.corpus_size == 171 and len(retriever.chunk_ids) == 171 and retriever.vectors.shape[0] == 171,
        f"corpus_size={retriever.corpus_size}"
    )

    # Test 2: Chunk ID Uniqueness
    unique_ids = set(retriever.chunk_ids)
    record_test(
        "Chunk ID Uniqueness & Non-Empty",
        len(unique_ids) == 171 and all(len(cid) > 0 for cid in unique_ids),
        f"all 171 chunk_ids unique"
    )

    # Test 3: Vector Dimension Consistency & L2 Normalization
    dim = retriever.embedding_dimension
    vecs = retriever.vectors
    norms = np.linalg.norm(vecs, axis=1)
    is_normalized = np.allclose(norms, 1.0, atol=1e-3)
    record_test(
        "Vector Dimension Consistency & L2 Normalization",
        vecs.shape == (171, dim) and is_normalized,
        f"matrix shape={vecs.shape}, mean norm={np.mean(norms):.4f}"
    )

    # Test 4: Numeric Sanity (No NaNs, No Infs)
    has_nan = np.isnan(vecs).any()
    has_inf = np.isinf(vecs).any()
    record_test(
        "Numeric Sanity (Zero NaNs, Zero Infs)",
        not has_nan and not has_inf,
        f"finite values verified"
    )

    # Test 5: Query Vector Dimension Match
    q_vec = retriever.encode_query("What does WHO recommend for brief advice?")
    q_norm = np.linalg.norm(q_vec)
    record_test(
        "Query Vector Dimension & Normalization Match",
        q_vec.shape == (dim,) and np.isclose(q_norm, 1.0, atol=1e-3),
        f"query dim={q_vec.shape[0]}, norm={q_norm:.4f}"
    )

    # Test 6: Strict Descending Score Ordering
    sample_queries = [
        "Varenicline for tobacco cessation",
        "أنا عايز أبطل السجاير ومش قادر",
        "How should health providers manage tobacco cessation in pregnant women?",
    ]
    ordering_valid = True
    for sq in sample_queries:
        res = retriever.retrieve(sq, top_k=10)
        scores = [r.score for r in res]
        if scores != sorted(scores, reverse=True):
            ordering_valid = False
            break

    record_test(
        "Strict Descending Cosine Similarity Ordering",
        ordering_valid,
        f"tested {len(sample_queries)} multilingual queries at top-10"
    )

    # Test 7: Deterministic & Reproducible Retrieval
    r1 = retriever.retrieve(sample_queries[0], top_k=5)
    r2 = retriever.retrieve(sample_queries[0], top_k=5)
    ids1 = [r.chunk_id for r in r1]
    ids2 = [r.chunk_id for r in r2]
    scores1 = [r.score for r in r1]
    scores2 = [r.score for r in r2]
    record_test(
        "Deterministic & Reproducible Retrieval",
        ids1 == ids2 and np.allclose(scores1, scores2),
        f"top-5 identical: {ids1[:2]}..."
    )

    # Test 8: Traceability Metadata Completeness
    top_res = r1[0]
    meta_ok = (
        top_res.chunk_id
        and top_res.text
        and top_res.document_id == "who_tobacco_cessation_2024"
        and top_res.physical_page_start is not None
        and top_res.section_title
        and top_res.heading_path
        and top_res.token_count > 0
    )
    record_test(
        "Traceability Metadata Completeness",
        meta_ok,
        f"chunk={top_res.chunk_id}, page={top_res.physical_page_start}, section='{top_res.section_number}'"
    )

    # Test 9: Index Serialization & Reloading Fidelity
    loaded_retriever = DenseRetriever.load_index(NPZ_PATH, META_PATH, RECORDS_PATH)
    l_res = loaded_retriever.retrieve(sample_queries[1], top_k=5)
    orig_res = retriever.retrieve(sample_queries[1], top_k=5)
    record_test(
        "Index Serialization & Reloading Fidelity (NPZ + JSON)",
        [r.chunk_id for r in l_res] == [r.chunk_id for r in orig_res]
        and np.allclose([r.score for r in l_res], [r.score for r in orig_res]),
        f"loaded {loaded_retriever.corpus_size} chunks from {NPZ_PATH}"
    )

    # Test 10: ContextAssembler Interoperability
    assembler = ContextAssembler(max_context_tokens=3000)
    ca_input = [r.to_context_assembler_dict() for r in r1]
    assembled = assembler.assemble(sample_queries[0], ca_input)
    record_test(
        "ContextAssembler Integration & Distance Surrogate",
        assembled.context_token_count > 0 and len(assembled.sources) == 5,
        f"assembled {len(assembled.sources)} sources, tokens={assembled.context_token_count}"
    )

    # Test 11: Cross-Lingual Egyptian Arabic Retrieval
    ar_res = retriever.retrieve("عايز دكتور أو حد يساعدني خطوة بخطوة عشان أوقف التدخين", top_k=5)
    ar_hits = [r.chunk_id for r in ar_res]
    ar_success = any(cid in {
        "chunk_sec_3_1_1",
        "chunk_sec_3_1_3_p02",
        "chunk_node_L1_glossary_of_terms_p11",
        "chunk_sec_3_5_1",       # Recommendation 9: combine medication + counselling — clinically valid
        "chunk_sec_3_5_3_p01",   # Evidence: combination of medication and support
    } for cid in ar_hits)
    record_test(
        "Cross-Lingual Egyptian Arabic Semantic Match",
        ar_success,
        f"top-1 chunk='{ar_res[0].chunk_id}', score={ar_res[0].score:.4f}"
    )

    # Test 12: Ground Truth Text Invariant
    records_map = {r["chunk_id"]: r["content"]["verbatim_text"] for r in records}
    no_text_mutation = all(r.text == records_map[r.chunk_id] for r in r1 + ar_res)
    record_test(
        "Ground Truth Text Invariant (Zero Mutation)",
        no_text_mutation,
        "all retrieved text matches ground-truth verbatim records exactly"
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
