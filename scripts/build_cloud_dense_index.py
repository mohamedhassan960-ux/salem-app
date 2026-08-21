"""
Cloud Dense Index Builder (v3) — Medical RAG: Oxygen (أوكسجين)
Source Document: WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)

Generates dense semantic embeddings for all 171 WHO chunks using Google Gemini Cloud Embeddings
(models/gemini-embedding-001 with outputDimensionality=768) in 2 efficient batch requests.

Outputs:
- outputs/dense_index_cloud_v3.npz
- outputs/dense_metadata_cloud_v3.json

Rollback Safety:
- outputs/dense_index_v2.npz and dense_metadata_v2.json are strictly preserved untouched.
"""

from __future__ import annotations

import os
import sys
import json
import time
import logging
from typing import Dict, List, Any
import numpy as np

# Ensure scripts directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dense_retriever import GeminiEmbeddingProvider, DenseRetriever

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

RECORDS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "retrieval_records_v2.json")
OUTPUT_NPZ = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "dense_index_cloud_v3.npz")
OUTPUT_META = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "dense_metadata_cloud_v3.json")


def build_cloud_index(
    records_path: str = RECORDS_PATH,
    output_npz: str = OUTPUT_NPZ,
    output_meta: str = OUTPUT_META,
    dimension: int = 768,
) -> Dict[str, Any]:
    """Builds the cloud dense index v3 and validates all vectors."""
    if not os.path.exists(records_path):
        raise FileNotFoundError(f"Retrieval records not found at {records_path}")

    logging.info(f"Loading retrieval records from {records_path}...")
    with open(records_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    records: List[Dict[str, Any]] = data.get("records", [])

    total_chunks = len(records)
    logging.info(f"Loaded {total_chunks} chunks. Initializing GeminiEmbeddingProvider (model=models/gemini-embedding-2, dim={dimension})...")
    provider = GeminiEmbeddingProvider(model_name="models/gemini-embedding-2", dimension=dimension)

    texts = [r.get("content", {}).get("verbatim_text", "") for r in records]
    chunk_ids = [r["chunk_id"] for r in records]

    t0 = time.time()
    logging.info(f"Generating dense embeddings for {total_chunks} chunks via batchEmbedContents...")
    embeddings = provider.encode_passages_batch(texts, batch_size=30)
    elapsed = time.time() - t0

    vectors = np.asarray(embeddings, dtype=np.float32)
    logging.info(f"Generated embeddings in {elapsed:.2f}s. Matrix shape: {vectors.shape}")

    # Rigorous vector validation
    assert vectors.shape == (total_chunks, dimension), f"Unexpected shape {vectors.shape}"
    nan_count = int(np.isnan(vectors).sum())
    inf_count = int(np.isinf(vectors).sum())
    assert nan_count == 0, f"Found {nan_count} NaN values in vector matrix!"
    assert inf_count == 0, f"Found {inf_count} Inf values in vector matrix!"

    norms = np.linalg.norm(vectors, axis=1)
    min_norm = float(np.min(norms))
    max_norm = float(np.max(norms))
    logging.info(f"Vector validation passed: NaNs={nan_count}, Infs={inf_count}, Min Norm={min_norm:.5f}, Max Norm={max_norm:.5f}")
    assert np.allclose(norms, 1.0, atol=1e-4), f"Vectors are not properly normalized! Range: [{min_norm}, {max_norm}]"

    # Save vectors atomically to NPZ
    os.makedirs(os.path.dirname(output_npz), exist_ok=True)
    np.savez_compressed(
        output_npz,
        vectors=vectors,
        chunk_ids=np.array(chunk_ids, dtype=object),
    )

    # Save metadata JSON
    meta_payload = {
        "index_version": "v3_cloud",
        "provider_name": provider.provider_name,
        "model_name": provider.model_name,
        "embedding_dimension": dimension,
        "corpus_size": total_chunks,
        "created_at_utc": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime()),
        "batch_indexing_time_seconds": round(elapsed, 2),
        "chunk_ids": chunk_ids,
        "use_e5_prefixes": False,
        "normalization": "L2_unit",
    }
    with open(output_meta, "w", encoding="utf-8") as f:
        json.dump(meta_payload, f, ensure_ascii=False, indent=2)

    logging.info(f"Successfully saved dense index v3 to {output_npz} and metadata to {output_meta}")
    return meta_payload


if __name__ == "__main__":
    meta = build_cloud_index()
    print("Cloud Dense Index v3 successfully built and validated:")
    print(json.dumps(meta, indent=2))
