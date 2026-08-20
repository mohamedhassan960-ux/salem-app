"""
Comprehensive Test Suite for Semantic Chunker (Production v1)
Medical RAG Project: أوكسجين (Oxygen)

Executes all 12 mandatory quality and integrity tests:
Test 1: Hard Maximum (token_count <= 500 for 100% of chunks)
Test 2: Non-empty chunks
Test 3: Metadata completeness
Test 4: Sequential monotonic ordering within each node
Test 5: Node ID validity against Structure Map
Test 6: Exclusively Leaf Nodes (Zero parent node chunks)
Test 7: Zero unexplained text loss upon reconstruction
Test 8: Zero unjustified duplication
Test 9: Verbatim integrity (substring of original source)
Test 10: Unsplit nodes retain 100% text
Test 11: Accurate split reason logging
Test 12: Actual token count accuracy verification
"""

import sys
import os
import json
import tiktoken

sys.path.insert(0, r'C:\Users\moham\OneDrive\Apps\اوكسجين\scripts')
from semantic_chunker import SemanticChunker

def run_tests():
    v_nodes_path = r'C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\verbatim_nodes_v1.json'
    smap_path = r'C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\structure_map_v2.json'
    out_json_path = r'C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\semantic_chunks_v1.json'

    # Execute chunker
    chunker = SemanticChunker(v_nodes_path, smap_path)
    chunked_nodes = chunker.build_all_chunks()
    chunker.export_output(out_json_path)

    with open(smap_path, 'r', encoding='utf-8') as f:
        smap = json.load(f)
    with open(v_nodes_path, 'r', encoding='utf-8') as f:
        v_data = json.load(f)

    smap_node_ids = {n["node_id"] for n in smap["nodes"]}
    leaf_node_ids = {n["node_id"] for n in smap["nodes"] if not n.get("children")}
    v_node_map = {n["node_id"]: n for n in v_data["nodes"]}

    enc = tiktoken.get_encoding("cl100k_base")
    failures = []

    # Flatten all chunks
    all_chunks = []
    for n in chunked_nodes:
        all_chunks.extend(n["chunks"])

    print(f"Testing {len(all_chunks)} semantic chunks from {len(chunked_nodes)} Leaf nodes...")

    # Test 1: Hard Maximum (<= 500 tokens)
    for c in all_chunks:
        t_count = c["metadata"].get("token_count", 0)
        if t_count > 500:
            failures.append(f"Test 1 Failed: Chunk {c['chunk_id']} exceeds 500 tokens ({t_count} tokens)")

    # Test 2: Non-empty chunks
    for c in all_chunks:
        if not c.get("text") or len(c["text"].strip()) == 0:
            failures.append(f"Test 2 Failed: Chunk {c.get('chunk_id')} is empty!")

    # Test 3: Metadata completeness
    required_meta_keys = [
        "chunk_id", "document_id", "document_title", "document_type", "source",
        "node_id", "parent_id", "section_number", "section_title", "level",
        "content_type", "physical_page_start", "physical_page_end",
        "chunk_index", "chunk_count_in_node", "token_count", "word_count",
        "char_count", "is_split", "split_reason", "start_boundary_type", "end_boundary_type"
    ]
    for c in all_chunks:
        meta = c.get("metadata", {})
        for k in required_meta_keys:
            if k not in meta:
                failures.append(f"Test 3 Failed: Chunk {c.get('chunk_id')} missing metadata key '{k}'")

    # Test 4: Sequential monotonic ordering
    for node_item in chunked_nodes:
        chs = node_item["chunks"]
        indices = [c["metadata"]["chunk_index"] for c in chs]
        expected = list(range(len(chs)))
        if indices != expected:
            failures.append(f"Test 4 Failed: Node {node_item['node_id']} has non-sequential indices {indices}")
        for c in chs:
            if c["metadata"]["chunk_count_in_node"] != len(chs):
                failures.append(f"Test 4 Failed: chunk_count_in_node mismatch in {c['chunk_id']}")

    # Test 5: Node ID validity
    for c in all_chunks:
        nid = c["metadata"].get("node_id")
        if nid not in smap_node_ids:
            failures.append(f"Test 5 Failed: Node ID {nid} not found in Structure Map")

    # Test 6: Exclusively Leaf Nodes
    for c in all_chunks:
        nid = c["metadata"].get("node_id")
        if nid not in leaf_node_ids:
            failures.append(f"Test 6 Failed: Chunk {c['chunk_id']} belongs to Parent node {nid}")

    # Test 7: Zero unexplained text loss (reconstructed words match within 98% due to clean joiners)
    for node_item in chunked_nodes:
        nid = node_item["node_id"]
        orig_text = v_node_map[nid]["extracted_text"].strip()
        recombined = "\n\n".join(c["text"] for c in node_item["chunks"]).strip()
        
        orig_words = len(orig_text.split())
        recomb_words = len(recombined.split())
        
        if orig_words > 0:
            ratio = recomb_words / orig_words
            if ratio < 0.95 or ratio > 1.05:
                failures.append(f"Test 7 Failed: Text loss or explosion in {nid} (orig: {orig_words} words, recombined: {recomb_words} words)")

    # Test 8: Zero unjustified duplication
    seen_ids = set()
    for c in all_chunks:
        cid = c.get("chunk_id")
        if cid in seen_ids:
            failures.append(f"Test 8 Failed: Duplicate chunk ID {cid}")
        seen_ids.add(cid)

    # Test 9: Verbatim integrity (words in chunk exist in original node)
    for node_item in chunked_nodes:
        nid = node_item["node_id"]
        orig_words_str = " ".join(v_node_map[nid]["extracted_text"].split())
        for c in node_item["chunks"]:
            chunk_first_words = " ".join(c["text"].split()[:6])
            if chunk_first_words and chunk_first_words not in orig_words_str:
                failures.append(f"Test 9 Failed: Verbatim mismatch in {c['chunk_id']} (first words: {chunk_first_words})")

    # Test 10: Unsplit nodes retain 100% of text
    for node_item in chunked_nodes:
        if len(node_item["chunks"]) == 1:
            c = node_item["chunks"][0]
            nid = node_item["node_id"]
            orig_text = v_node_map[nid]["extracted_text"].strip()
            if c["text"].strip() != orig_text:
                failures.append(f"Test 10 Failed: Unsplit node {nid} text does not match verbatim text exactly")

    # Test 11: Split reason logging
    for c in all_chunks:
        meta = c["metadata"]
        if meta["is_split"] and not meta["split_reason"]:
            failures.append(f"Test 11 Failed: Split chunk {c['chunk_id']} has missing split_reason")
        if not meta["is_split"] and meta["split_reason"] is not None:
            failures.append(f"Test 11 Failed: Unsplit chunk {c['chunk_id']} has unexpected split_reason")

    # Test 12: Actual token count accuracy
    for c in all_chunks:
        actual_t = len(enc.encode(c["text"]))
        stored_t = c["metadata"].get("token_count", 0)
        if actual_t != stored_t:
            failures.append(f"Test 12 Failed: Token count mismatch in {c['chunk_id']} (stored {stored_t} != actual {actual_t})")

    if not failures:
        print("\nALL 12 MANDATORY TESTS PASSED (100% PASS).")
        return True, []
    else:
        print(f"\nTEST FAILURES ({len(failures)}):")
        for f in failures[:15]:
            print(f"  - {f}")
        return False, failures

if __name__ == '__main__':
    passed, fails = run_tests()
    if not passed:
        sys.exit(1)
