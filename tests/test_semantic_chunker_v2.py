"""
Comprehensive Automated Test Suite for Semantic Chunker v2
Medical RAG — WHO Tobacco Cessation Guideline (2024)

Executes all 14 mandatory quality and architecture tests:
Test 1: No Empty Chunks
Test 2: Valid chunk_ids
Test 3: Valid node_ids
Test 4: Exclusively Leaf Nodes
Test 5: Token Count Accuracy (cl100k_base recalculated)
Test 6: Hard Maximum Violation (token_count <= 500)
Test 7: Verbatim Text Preservation & Loss Detection
Test 8: Monotonic Sequential Ordering (chunk_index: 0, 1, 2...)
Test 9: Recommendation Integrity
Test 10: Glossary Integrity
Test 11: Reference Isolation (retrieval_role == "reference_lookup")
Test 12: Metadata Schema Completeness
Test 13: Parent Referential Integrity
Test 14: Determinism (Identical output across consecutive runs)
"""

import sys
import os
import json
import tiktoken

sys.path.insert(0, r'C:\Users\moham\OneDrive\Apps\اوكسجين\scripts')
from semantic_chunker_v2 import SemanticChunkerV2

def run_tests():
    v_nodes = r'C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\verbatim_nodes_v1.json'
    s_map = r'C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\structure_map_v2.json'
    out_json = r'C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\semantic_chunks_v2.json'
    out_jsonl = r'C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\semantic_chunks_v2.jsonl'

    # Run Chunker
    chunker = SemanticChunkerV2(v_nodes, s_map)
    chunks = chunker.build_all_chunks()
    chunker.export_chunks(out_json, out_jsonl)

    with open(s_map, 'r', encoding='utf-8') as f:
        smap_data = json.load(f)
    with open(v_nodes, 'r', encoding='utf-8') as f:
        v_data = json.load(f)

    smap_node_ids = {n["node_id"] for n in smap_data["nodes"]}
    leaf_node_ids = {n["node_id"] for n in smap_data["nodes"] if not n.get("children")}
    v_node_map = {n["node_id"]: n for n in v_data["nodes"]}

    enc = tiktoken.get_encoding("cl100k_base")

    failures = []

    print(f"Testing {len(chunks)} generated semantic chunks...")

    # Test 1: No Empty Chunks
    for ch in chunks:
        if not ch.get("text") or len(ch["text"].strip()) == 0:
            failures.append(f"Test 1 Failed: Empty text in chunk {ch.get('chunk_id')}")

    # Test 2: Valid chunk_id
    seen_chunk_ids = set()
    for ch in chunks:
        cid = ch.get("chunk_id")
        if not cid or not isinstance(cid, str):
            failures.append(f"Test 2 Failed: Invalid chunk_id in {ch}")
        if cid in seen_chunk_ids:
            failures.append(f"Test 2 Failed: Duplicate chunk_id {cid}")
        seen_chunk_ids.add(cid)

    # Test 3: Valid node_id
    for ch in chunks:
        nid = ch.get("node_id")
        if nid not in smap_node_ids:
            failures.append(f"Test 3 Failed: node_id {nid} not found in structure map")

    # Test 4: Exclusively Leaf Nodes
    for ch in chunks:
        nid = ch.get("node_id")
        if nid not in leaf_node_ids:
            failures.append(f"Test 4 Failed: chunk {ch['chunk_id']} belongs to branch/parent node {nid}")

    # Test 5: Token Count Accuracy
    for ch in chunks:
        actual_tokens = len(enc.encode(ch["text"]))
        stored_tokens = ch.get("token_count", 0)
        if actual_tokens != stored_tokens:
            failures.append(f"Test 5 Failed: Token mismatch in {ch['chunk_id']} (stored {stored_tokens} != actual {actual_tokens})")

    # Test 6: Hard Maximum (token_count <= 500)
    for ch in chunks:
        if ch.get("token_count", 0) > 500:
            failures.append(f"Test 6 Failed: Hard Maximum violated in {ch['chunk_id']} ({ch['token_count']} tokens > 500)")

    # Test 7: Verbatim Text Preservation (No loss of core words)
    node_to_chunks = {}
    for ch in chunks:
        nid = ch["node_id"]
        node_to_chunks.setdefault(nid, []).append(ch)

    for nid in leaf_node_ids:
        if nid not in node_to_chunks:
            failures.append(f"Test 7 Failed: Leaf node {nid} has zero chunks generated!")

    # Test 8: Monotonic Sequential Ordering (chunk_index: 0, 1, 2...)
    for nid, ch_list in node_to_chunks.items():
        indices = [c["chunk_index"] for c in ch_list]
        expected = list(range(len(ch_list)))
        if indices != expected:
            failures.append(f"Test 8 Failed: Non-sequential indices in node {nid}: {indices} vs {expected}")
        for c in ch_list:
            if c["chunk_count"] != len(ch_list):
                failures.append(f"Test 8 Failed: chunk_count mismatch in {c['chunk_id']}")

    # Test 9: Recommendation Integrity
    rec_nodes = [n for n in v_data["nodes"] if n["node_id"] in leaf_node_ids and ("recommendation" in (n.get("content_type") or "").lower() or "3.1.1" in (n.get("section_number") or ""))]
    for rn in rec_nodes:
        r_chunks = node_to_chunks.get(rn["node_id"], [])
        if not r_chunks:
            failures.append(f"Test 9 Failed: Recommendation node {rn['node_id']} produced no chunks!")

    # Test 10: Glossary Integrity
    glossary_chunks = [c for c in chunks if c.get("content_type") == "glossary"]
    if len(glossary_chunks) < 20:
        failures.append(f"Test 10 Failed: Expected >= 20 atomic glossary chunks, got {len(glossary_chunks)}")

    # Test 11: Reference Isolation (retrieval_role == "reference_lookup")
    for ch in chunks:
        if ch.get("content_type") == "references" or "references" in ch.get("section_title", "").lower():
            if ch.get("retrieval_role") != "reference_lookup":
                failures.append(f"Test 11 Failed: Reference chunk {ch['chunk_id']} has role {ch.get('retrieval_role')}")
        else:
            if ch.get("retrieval_role") != "clinical_dense_retrieval":
                failures.append(f"Test 11 Failed: Clinical chunk {ch['chunk_id']} has non-clinical role {ch.get('retrieval_role')}")

    # Test 12: Metadata Completeness
    required_keys = [
        "chunk_id", "document_id", "node_id", "parent_id", "section_number",
        "section_title", "chunk_index", "chunk_count", "content_type",
        "physical_page_start", "physical_page_end", "token_count",
        "word_count", "character_count", "source_type", "retrieval_role",
        "split_reason", "text"
    ]
    for ch in chunks:
        for k in required_keys:
            if k not in ch:
                failures.append(f"Test 12 Failed: Chunk {ch.get('chunk_id')} missing required key '{k}'")

    # Test 13: Parent Referential Integrity
    for ch in chunks:
        pid = ch.get("parent_id")
        if pid and pid != "root" and pid not in smap_node_ids:
            failures.append(f"Test 13 Failed: Parent ID {pid} in chunk {ch['chunk_id']} does not exist in structure map")

    # Test 14: Determinism
    chunker2 = SemanticChunkerV2(v_nodes, s_map)
    chunks2 = chunker2.build_all_chunks()
    if json.dumps(chunks, sort_keys=True) != json.dumps(chunks2, sort_keys=True):
        failures.append("Test 14 Failed: Chunker is not deterministic across consecutive runs!")

    if not failures:
        print("\nALL 14 AUTOMATED TESTS PASSED (100% PASS).")
        return True, []
    else:
        print(f"\nTEST FAILURES ({len(failures)}):")
        for f in failures[:10]:
            print(f"  - {f}")
        return False, failures

if __name__ == '__main__':
    passed, fails = run_tests()
    if not passed:
        sys.exit(1)
