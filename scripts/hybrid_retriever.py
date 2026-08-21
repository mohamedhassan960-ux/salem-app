"""
Hybrid Retrieval Engine — Medical RAG: Oxygen (أوكسجين)
Source Document: WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)

Combines:
1. BM25 Sparse Keyword Retrieval (MedicalTokenizer + Okapi Robertson-Spärck Jones)
2. Dense Semantic Vector Retrieval (multilingual-e5-small + Cosine Similarity)
3. Reciprocal Rank Fusion (RRF):
   RRF_score(d) = Σ [ 1 / (k_rrf + rank_m(d)) ] for m in {BM25, Dense}
   with standard k_rrf = 60.

Architecture:
  User Query (English / Egyptian Arabic / Non-Medical)
         │
    ┌────┴────┐
    │         │
   BM25     Dense
    │         │
    └────┬────┘
         ▼
     RRF Fusion
         ▼
       Top-5
         ▼
  Context Assembler
"""

from __future__ import annotations

import os
import json
import logging
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Set, Tuple

from bm25_retriever import BM25Retriever, BM25SearchResult
from dense_retriever import DenseRetriever, DenseSearchResult
from context_assembler import ContextAssembler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


# ─────────────────────────────────────────────────────────────────────────────
# Hybrid Search Result Data Structure
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class HybridSearchResult:
    """Single ranked evidence result produced by RRF Hybrid Fusion."""
    chunk_id: str
    rrf_score: float                        # Reciprocal Rank Fusion score
    hybrid_rank: int                        # 1-indexed fused rank (1 to top_k)
    bm25_rank: Optional[int]                # Rank in BM25 candidates, or None if not present
    dense_rank: Optional[int]               # Rank in Dense candidates, or None if not present
    bm25_score: Optional[float]             # Raw BM25 score, or None
    dense_score: Optional[float]            # Raw Cosine Similarity score, or None
    text: str                               # Verbatim ground truth evidence text (100% untouched)
    document_id: str
    node_id: str
    parent_id: str
    section_number: Optional[str]
    section_title: str
    heading_path: str
    physical_page_start: Optional[int]
    physical_page_end: Optional[int]
    printed_page_start: Optional[int]
    printed_page_end: Optional[int]
    content_type: str
    retrieval_role: str
    token_count: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_context_assembler_dict(self) -> Dict[str, Any]:
        """Produces exact dictionary consumed by ContextAssembler for prompt injection."""
        # Convert RRF score (higher is better) to distance surrogate (lower is better)
        # Max RRF for k=60 with 2 engines at rank 1 is 2/(60+1) = 0.032787
        # Distance metric: 1.0 - (rrf_score / 0.033)
        dist = max(0.0, 1.0 - (self.rrf_score / 0.033))
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "node_id": self.node_id,
            "parent_id": self.parent_id,
            "section_number": self.section_number,
            "section_title": self.section_title,
            "chunk_index": 0,
            "chunk_count": 1,
            "content_type": self.content_type,
            "physical_page_start": self.physical_page_start,
            "physical_page_end": self.physical_page_end,
            "token_count": self.token_count,
            "word_count": len(self.text.split()),
            "character_count": len(self.text),
            "source_type": "verbatim",
            "retrieval_role": self.retrieval_role,
            "split_reason": None,
            "distance": round(dist, 4),
            "rrf_score": round(self.rrf_score, 6),
            "hybrid_rank": self.hybrid_rank,
            "bm25_rank": self.bm25_rank,
            "dense_rank": self.dense_rank,
            "bm25_score": round(self.bm25_score, 4) if self.bm25_score is not None else None,
            "dense_score": round(self.dense_score, 4) if self.dense_score is not None else None,
            "rank": self.hybrid_rank,
            "text": self.text,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Hybrid Retriever Engine
# ─────────────────────────────────────────────────────────────────────────────

class HybridRetriever:
    """
    Unified Hybrid Retrieval Engine combining BM25 Sparse and Dense Semantic search via RRF.
    """

    DEFAULT_K_RRF: int = 60
    DEFAULT_CANDIDATE_POOL: int = 30

    def __init__(
        self,
        bm25_retriever: BM25Retriever,
        dense_retriever: DenseRetriever,
        k_rrf: int = DEFAULT_K_RRF,
        candidate_pool_size: int = DEFAULT_CANDIDATE_POOL,
    ):
        self.bm25_retriever = bm25_retriever
        self.dense_retriever = dense_retriever
        self.k_rrf = k_rrf
        self.candidate_pool_size = candidate_pool_size

        if self.bm25_retriever.corpus_size != self.dense_retriever.corpus_size:
            logging.warning(
                f"Corpus size mismatch between BM25 ({self.bm25_retriever.corpus_size}) "
                f"and Dense ({self.dense_retriever.corpus_size})!"
            )

        self.corpus_size = self.bm25_retriever.corpus_size

    @classmethod
    def from_files(
        cls,
        records_path: Optional[str] = None,
        dense_npz_path: Optional[str] = None,
        dense_meta_path: Optional[str] = None,
        model_name: Optional[str] = None,
        k_rrf: int = DEFAULT_K_RRF,
        candidate_pool_size: int = DEFAULT_CANDIDATE_POOL,
        provider: Optional[Any] = None,
    ) -> HybridRetriever:
        """Loads and initializes both retrievers from disk records and precomputed dense index."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if records_path is None:
            records_path = os.path.join(base_dir, "outputs", "retrieval_records_v2.json")

        # Prioritize cloud v3 index, fall back to v2 for rollback
        v3_npz = os.path.join(base_dir, "outputs", "dense_index_cloud_v3.npz")
        v3_meta = os.path.join(base_dir, "outputs", "dense_metadata_cloud_v3.json")
        v2_npz = os.path.join(base_dir, "outputs", "dense_index_v2.npz")
        v2_meta = os.path.join(base_dir, "outputs", "dense_metadata_v2.json")

        if dense_npz_path is None:
            dense_npz_path = v3_npz if os.path.exists(v3_npz) else v2_npz
        if dense_meta_path is None:
            dense_meta_path = v3_meta if os.path.exists(v3_meta) else v2_meta

        with open(records_path, "r", encoding="utf-8") as f:
            records_data = json.load(f)
        records = records_data.get("records", [])

        # Initialize BM25
        bm25 = BM25Retriever(text_field="verbatim_text")
        bm25.index_records(records)

        # Initialize Dense
        if os.path.exists(dense_npz_path) and os.path.exists(dense_meta_path):
            dense = DenseRetriever.load_index(dense_npz_path, dense_meta_path, records_path, provider=provider)
        else:
            dense = DenseRetriever(model_name=model_name or "models/gemini-embedding-2", provider=provider)
            dense.index_records(records)
            dense.save_index(dense_npz_path, dense_meta_path)

        return cls(
            bm25_retriever=bm25,
            dense_retriever=dense,
            k_rrf=k_rrf,
            candidate_pool_size=candidate_pool_size,
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        k_rrf: Optional[int] = None,
        candidate_pool_size: Optional[int] = None,
        dimensions: Optional[List[str]] = None,
    ) -> List[HybridSearchResult]:
        """
        Executes parallel BM25 and Dense retrieval across original query and clinical dimensions,
        fusing results using Reciprocal Rank Fusion.

        Parameters:
        - query: User inquiry (English, Egyptian Colloquial Arabic, non-technical phrasing).
        - top_k: Final number of ranked evidence results to return (Default: 5).
        - k_rrf: Smoothing constant in RRF formula (Default: 60).
        - candidate_pool_size: Size of candidate list retrieved from each individual engine before fusion.
        - dimensions: Optional list of specific clinical dimension subqueries (e.g. ['pharmacotherapy', 'behavioural support']).

        Returns:
        - List[HybridSearchResult] sorted strictly descending by RRF score.
        """
        if not query or not query.strip():
            return []

        effective_k_rrf = k_rrf if k_rrf is not None else self.k_rrf
        pool_size = candidate_pool_size if candidate_pool_size is not None else self.candidate_pool_size
        # Ensure candidate pool is at least top_k
        pool_size = max(pool_size, top_k)

        # 1. Fetch Candidate Lists for Primary Query
        bm25_results = self.bm25_retriever.retrieve(query, top_k=pool_size)
        dense_results = self.dense_retriever.retrieve(query, top_k=pool_size)

        fused_map: Dict[str, Dict[str, Any]] = {}

        # Process BM25 candidates (Primary Query)
        for rank, b_res in enumerate(bm25_results, start=1):
            cid = b_res.chunk_id
            rrf_contrib = 1.0 / (effective_k_rrf + rank)

            if cid not in fused_map:
                fused_map[cid] = {
                    "rrf_score": 0.0,
                    "bm25_rank": rank,
                    "bm25_score": b_res.score,
                    "dense_rank": None,
                    "dense_score": None,
                    "doc_ref": b_res,
                }
            else:
                fused_map[cid]["bm25_rank"] = rank
                fused_map[cid]["bm25_score"] = b_res.score

            fused_map[cid]["rrf_score"] += rrf_contrib

        # Process Dense candidates (Primary Query)
        for rank, d_res in enumerate(dense_results, start=1):
            cid = d_res.chunk_id
            rrf_contrib = 1.0 / (effective_k_rrf + rank)

            if cid not in fused_map:
                fused_map[cid] = {
                    "rrf_score": 0.0,
                    "bm25_rank": None,
                    "bm25_score": None,
                    "dense_rank": rank,
                    "dense_score": d_res.score,
                    "doc_ref": d_res,
                }
            else:
                fused_map[cid]["dense_rank"] = rank
                fused_map[cid]["dense_score"] = d_res.score

            fused_map[cid]["rrf_score"] += rrf_contrib

        # 2. Process Additional Clinical Retrieval Dimensions (Subqueries)
        if dimensions:
            dim_pool = min(15, pool_size)
            for dim_query in dimensions:
                if not dim_query or not dim_query.strip():
                    continue
                dim_bm25 = self.bm25_retriever.retrieve(dim_query, top_k=dim_pool)
                dim_dense = self.dense_retriever.retrieve(dim_query, top_k=dim_pool)

                for rank, b_res in enumerate(dim_bm25, start=1):
                    cid = b_res.chunk_id
                    rrf_contrib = 0.5 * (1.0 / (effective_k_rrf + rank))
                    if cid in fused_map:
                        fused_map[cid]["rrf_score"] += rrf_contrib
                    else:
                        fused_map[cid] = {
                            "rrf_score": rrf_contrib,
                            "bm25_rank": rank + 100,
                            "bm25_score": b_res.score,
                            "dense_rank": None,
                            "dense_score": None,
                            "doc_ref": b_res,
                        }

                for rank, d_res in enumerate(dim_dense, start=1):
                    cid = d_res.chunk_id
                    rrf_contrib = 0.5 * (1.0 / (effective_k_rrf + rank))
                    if cid in fused_map:
                        fused_map[cid]["rrf_score"] += rrf_contrib
                    else:
                        fused_map[cid] = {
                            "rrf_score": rrf_contrib,
                            "bm25_rank": None,
                            "bm25_score": None,
                            "dense_rank": rank + 100,
                            "dense_score": d_res.score,
                            "doc_ref": d_res,
                        }

        # 3. Sort fused candidates by RRF score descending
        # Secondary sort key: -dense_rank (if exists), then -bm25_rank for absolute determinism
        sorted_candidates = sorted(
            fused_map.items(),
            key=lambda item: (
                item[1]["rrf_score"],
                -(item[1]["dense_rank"] if item[1]["dense_rank"] is not None else 9999),
                -(item[1]["bm25_rank"] if item[1]["bm25_rank"] is not None else 9999),
            ),
            reverse=True,
        )

        # 4. Construct Top-K HybridSearchResult objects
        hybrid_results: List[HybridSearchResult] = []
        for hybrid_rank, (cid, data) in enumerate(sorted_candidates[:top_k], start=1):
            doc = data["doc_ref"]
            result = HybridSearchResult(
                chunk_id=cid,
                rrf_score=round(data["rrf_score"], 6),
                hybrid_rank=hybrid_rank,
                bm25_rank=data["bm25_rank"],
                dense_rank=data["dense_rank"],
                bm25_score=data["bm25_score"],
                dense_score=data["dense_score"],
                text=doc.text,
                document_id=doc.document_id,
                node_id=doc.node_id,
                parent_id=doc.parent_id,
                section_number=doc.section_number,
                section_title=doc.section_title,
                heading_path=doc.heading_path,
                physical_page_start=doc.physical_page_start,
                physical_page_end=doc.physical_page_end,
                printed_page_start=doc.printed_page_start,
                printed_page_end=doc.printed_page_end,
                content_type=doc.content_type,
                retrieval_role=doc.retrieval_role,
                token_count=doc.token_count,
            )
            hybrid_results.append(result)

        return hybrid_results


if __name__ == "__main__":
    retriever = HybridRetriever.from_files()
    test_q = "أنا عايز أبطل السجاير ومش عارف أبدأ منين"
    res = retriever.retrieve(test_q, top_k=5)
    print(f"Hybrid retrieval test query: '{test_q}' -> {len(res)} results:")
    for r in res:
        print(f"  Rank #{r.hybrid_rank} | Chunk: {r.chunk_id} | RRF: {r.rrf_score:.6f} | DenseRank: {r.dense_rank} | BM25Rank: {r.bm25_rank} | Sec: {r.section_number}")
