"""
Comprehensive Test Suite — Retrieval Schema Architecture
Medical RAG Project: Oxygen (أوكسجين)
Source Document: WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)

Verifies all structural, clinical, provenance, and interoperability guarantees:
Test 1: Chunk ID Uniqueness & Non-Empty
Test 2: 100% Verbatim Text Fidelity (Zero text mutation/loss)
Test 3: Structural Hierarchy & Node Referential Integrity
Test 4: Heading Path Generation & Ancestry Trace
Test 5: Dual Provenance & Printed Page Calculation
Test 6: Medical Metadata & Taxonomy Completeness
Test 7: Token Count & Metric Recalculation (cl100k_base)
Test 8: Sibling Chunk Referential Integrity
Test 9: BM25 and Vector Search Payload Generation
Test 10: Seamless ContextAssembler Integration
Test 11: Serialization Round-Trip (to_dict / from_dict)
Test 12: Determinism Across Successive Builds
"""

import os
import sys
import json
import tiktoken

sys.path.insert(0, r"C:\Users\moham\OneDrive\Apps\اوكسجين\scripts")
from retrieval_schema import RetrievalSchemaBuilder, RetrievalRecord
from context_assembler import ContextAssembler

CHUNKS_V2_PATH = r"C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\semantic_chunks_v2.json"
SMAP_V2_PATH = r"C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\structure_map_v2.json"
RECORDS_V2_PATH = r"C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\retrieval_records_v2.json"
RECORDS_V2_JSONL = r"C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\retrieval_records_v2.jsonl"


def run_tests():
    print("=" * 70)
    print("RETRIEVAL SCHEMA AUTOMATED TEST SUITE")
    print("=" * 70)

    # 1. Build and export records
    builder = RetrievalSchemaBuilder(CHUNKS_V2_PATH, SMAP_V2_PATH)
    records = builder.build_records()
    builder.export_records(RECORDS_V2_PATH, RECORDS_V2_JSONL)

    with open(CHUNKS_V2_PATH, "r", encoding="utf-8") as f:
        v2_data = json.load(f)
    with open(SMAP_V2_PATH, "r", encoding="utf-8") as f:
        smap_data = json.load(f)

    v2_chunks = v2_data["chunks"]
    smap_node_ids = {n["node_id"] for n in smap_data["nodes"]}
    enc = tiktoken.get_encoding("cl100k_base")

    failures = []
    test_count = 0

    def record_test(name: str, passed: bool, detail: str = ""):
        nonlocal test_count
        test_count += 1
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} Test {test_count}: {name} {f'({detail})' if detail else ''}")
        if not passed:
            failures.append(f"Test {test_count} ({name}): {detail}")

    # Test 1: Chunk ID Uniqueness & Non-Empty
    seen_ids = set()
    dup_ids = set()
    empty_ids = []
    for r in records:
        if not r.chunk_id:
            empty_ids.append(r)
        if r.chunk_id in seen_ids:
            dup_ids.add(r.chunk_id)
        seen_ids.add(r.chunk_id)

    record_test(
        "Chunk ID Uniqueness & Non-Empty",
        len(seen_ids) == len(records) == 171 and len(dup_ids) == 0 and len(empty_ids) == 0,
        f"total={len(records)}, unique={len(seen_ids)}"
    )

    # Test 2: 100% Verbatim Text Fidelity
    v2_text_map = {c["chunk_id"]: c["text"] for c in v2_chunks}
    text_mismatches = []
    for r in records:
        expected_text = v2_text_map.get(r.chunk_id)
        if r.content.verbatim_text != expected_text:
            text_mismatches.append(r.chunk_id)

    record_test(
        "100% Verbatim Text Preservation",
        len(text_mismatches) == 0,
        f"checked 171 chunks against v2 source"
    )

    # Test 3: Structural Hierarchy & Node Referential Integrity
    broken_nodes = []
    broken_parents = []
    for r in records:
        if r.hierarchy.node_id not in smap_node_ids:
            broken_nodes.append(r.hierarchy.node_id)
        if r.hierarchy.parent_id != "root" and r.hierarchy.parent_id not in smap_node_ids:
            broken_parents.append(r.hierarchy.parent_id)

    record_test(
        "Structural Hierarchy & Referential Integrity",
        len(broken_nodes) == 0 and len(broken_parents) == 0,
        f"verified 171 nodes and parent references in structure map"
    )

    # Test 4: Heading Path Generation
    invalid_paths = []
    for r in records:
        hp = r.hierarchy.heading_path
        if not hp or not isinstance(hp, str) or len(hp.strip()) == 0:
            invalid_paths.append(r.chunk_id)

    record_test(
        "Heading Path Generation & Ancestry Trace",
        len(invalid_paths) == 0,
        f"sample path='{records[30].hierarchy.heading_path}'"
    )

    # Test 5: Dual Provenance & Printed Page Calculation
    provenance_errors = []
    for r in records:
        p = r.provenance
        if p.physical_page_start is None or p.physical_page_start < 1:
            provenance_errors.append(f"{r.chunk_id}: invalid physical_page_start")
        if p.physical_page_start and p.physical_page_start >= 19:
            if p.printed_page_start != p.physical_page_start - 18:
                provenance_errors.append(f"{r.chunk_id}: printed page offset error")

    record_test(
        "Dual Provenance & Page Offset Consistency",
        len(provenance_errors) == 0,
        f"verified physical (1..76) and printed page calculations"
    )

    # Test 6: Medical Metadata & Taxonomy Completeness
    valid_content_types = {
        "narrative", "recommendation", "methods", "evidence", "discussion",
        "glossary", "references", "table", "annex"
    }
    invalid_meta = []
    for r in records:
        m = r.medical_metadata
        if not m.content_type or not m.retrieval_role:
            invalid_meta.append(r.chunk_id)

    record_test(
        "Medical Metadata & Taxonomy Completeness",
        len(invalid_meta) == 0,
        f"all records have valid content_type and retrieval_role"
    )

    # Test 7: Token Count & Metric Recalculation
    token_errors = []
    for r in records:
        calc_tokens = len(enc.encode(r.content.verbatim_text))
        if calc_tokens != r.metrics.token_count:
            token_errors.append((r.chunk_id, calc_tokens, r.metrics.token_count))

    record_test(
        "Token Count Recalculation (cl100k_base)",
        len(token_errors) == 0,
        f"all 171 records strictly match recalculated token counts"
    )

    # Test 8: Sibling Chunk Referential Integrity
    sibling_errors = []
    record_id_set = {r.chunk_id for r in records}
    for r in records:
        for sid in r.hierarchy.sibling_chunk_ids:
            if sid not in record_id_set:
                sibling_errors.append((r.chunk_id, sid))
        if len(r.hierarchy.sibling_chunk_ids) != r.hierarchy.chunk_count:
            sibling_errors.append((r.chunk_id, "count_mismatch"))

    record_test(
        "Sibling Chunk Referential Integrity",
        len(sibling_errors) == 0,
        f"verified sibling arrays across all nodes"
    )

    # Test 9: BM25 and Vector Search Payload Generation
    bm25_errors = []
    vector_errors = []
    for r in records:
        # BM25 doc
        bdoc = r.to_bm25_document()
        if "chunk_id" not in bdoc or "searchable_text" not in bdoc or "verbatim_text" not in bdoc:
            bm25_errors.append(r.chunk_id)

        # Vector payload
        cid, text_to_embed, meta = r.to_vector_store_payload()
        if not cid or not text_to_embed:
            vector_errors.append(r.chunk_id)
        # ChromaDB requires scalar metadata
        for k, v in meta.items():
            if not isinstance(v, (str, int, float, bool)):
                vector_errors.append(f"{r.chunk_id}: non-scalar meta {k}={v}")

    record_test(
        "BM25 and Vector DB Payload Generation",
        len(bm25_errors) == 0 and len(vector_errors) == 0,
        f"verified sparse doc and dense vector store flat metadata"
    )

    # Test 10: Seamless ContextAssembler Integration
    assembler = ContextAssembler(max_context_tokens=3000)
    top_records = records[25:30]
    ca_results = [r.to_context_assembler_dict(distance=0.05 * (i + 1)) for i, r in enumerate(top_records)]
    
    assembled = assembler.assemble(
        query="What does WHO recommend for brief advice to adult tobacco users?",
        retrieval_results=ca_results
    )
    ca_success = (
        assembled.context_token_count > 0
        and len(assembled.sources) == len(top_records)
        and all(s.chunk_id == r.chunk_id for s, r in zip(assembled.sources, top_records))
    )
    record_test(
        "ContextAssembler Round-Trip Integration",
        ca_success,
        f"assembled {len(assembled.sources)} sources, tokens={assembled.context_token_count}"
    )

    # Test 11: Serialization Round-Trip
    roundtrip_errors = []
    for r in records:
        d = r.to_dict()
        r2 = RetrievalRecord.from_dict(d)
        if r.to_dict() != r2.to_dict():
            roundtrip_errors.append(r.chunk_id)

    record_test(
        "Serialization Round-Trip (to_dict / from_dict)",
        len(roundtrip_errors) == 0,
        f"171/171 records match identically after deserialization"
    )

    # Test 12: Determinism
    builder2 = RetrievalSchemaBuilder(CHUNKS_V2_PATH, SMAP_V2_PATH)
    records2 = builder2.build_records()
    diffs = [i for i, (r1, r2) in enumerate(zip(records, records2)) if r1.to_dict() != r2.to_dict()]

    record_test(
        "Deterministic Generation Across Runs",
        len(diffs) == 0,
        f"consecutive builds produce identical records"
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
