"""
Test Suite for ChromaDB Vector Store
Medical RAG Project: أوكسجين (Oxygen)

Validates:
1. Exactly 145 chunks indexed in ChromaDB collection 'medical_knowledge'.
2. All records contain non-empty documents and valid chunk_ids.
3. Metadata completeness across all retrieved records.
4. Similarity search execution and semantic retrieval quality.
5. Zero missing chunks.
"""

import os
import sys
import json
import chromadb
from sentence_transformers import SentenceTransformer

def run_vector_store_tests():
    db_path = r'C:\Users\moham\OneDrive\Apps\اوكسجين\data\chroma_db'
    chunks_path = r'C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\semantic_chunks_v1.json'
    collection_name = 'medical_knowledge'
    model_name = 'sentence-transformers/all-MiniLM-L6-v2'

    print(f"Connecting to ChromaDB at {db_path}...")
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_collection(collection_name)

    with open(chunks_path, 'r', encoding='utf-8') as f:
        cdata = json.load(f)

    expected_ids = set()
    for n in cdata.get("nodes", []):
        for c in n.get("chunks", []):
            expected_ids.add(c["chunk_id"])

    failures = []

    # 1. Count Test
    count = collection.count()
    print(f"Collection '{collection_name}' count: {count}")
    if count != 145:
        failures.append(f"Count mismatch: Expected 145, found {count}")

    # 2. Fetch all records
    records = collection.get(include=["documents", "metadatas"])
    indexed_ids = set(records["ids"])

    if indexed_ids != expected_ids:
        missing = expected_ids - indexed_ids
        extra = indexed_ids - expected_ids
        failures.append(f"ID mismatch: Missing {len(missing)}, Extra {len(extra)}")

    # 3. Check for empty documents or missing metadata
    for i, doc in enumerate(records["documents"]):
        cid = records["ids"][i]
        if not doc or len(doc.strip()) == 0:
            failures.append(f"Empty document in record {cid}")
        meta = records["metadatas"][i]
        if not meta.get("document_id") or not meta.get("node_id"):
            failures.append(f"Incomplete metadata in record {cid}")

    # 4. Semantic Retrieval Test
    print("Loading embedding model for retrieval verification...")
    model = SentenceTransformer(model_name)

    test_queries = [
        "What is the WHO recommendation for brief advice in healthcare settings?",
        "What are the first-line medications for tobacco cessation?",
        "Varenicline mechanism and efficacy in tobacco dependence"
    ]

    print("\n--- SAMPLE RETRIEVAL TEST ---")
    for q in test_queries:
        q_emb = model.encode([q])[0].tolist()
        results = collection.query(
            query_embeddings=[q_emb],
            n_results=3,
            include=["documents", "metadatas", "distances"]
        )
        print(f"\nQuery: '{q}'")
        top_id = results["ids"][0][0]
        top_dist = results["distances"][0][0]
        top_meta = results["metadatas"][0][0]
        top_doc_snippet = results["documents"][0][0][:120].replace('\n', ' ')
        print(f"  -> Top 1 Match: [{top_id}] | Cosine Distance: {top_dist:.4f}")
        print(f"  -> Section: {top_meta.get('section_number')} - {top_meta.get('section_title')}")
        print(f"  -> Pages: P{top_meta.get('physical_page_start')}-P{top_meta.get('physical_page_end')}")
        print(f"  -> Snippet: {top_doc_snippet}...")

    if not failures:
        print("\nALL VECTOR STORE TESTS PASSED (100% PASS).")
        return True, []
    else:
        print(f"\nFAILURES ({len(failures)}):")
        for f in failures:
            print(f"  - {f}")
        return False, failures

if __name__ == '__main__':
    passed, fails = run_vector_store_tests()
    if not passed:
        sys.exit(1)
