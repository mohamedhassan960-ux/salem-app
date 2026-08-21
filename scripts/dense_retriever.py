"""
Dense Semantic Retrieval Engine — Medical RAG: Oxygen (أوكسجين)
Source Document: WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)

Provides cross-lingual, semantic vector retrieval using multilingual dense embeddings:
- Embedding Model: intfloat/multilingual-e5-small (dim: 384, cross-lingual Arabic/English aligned)
- Prefix handling: Asymmetric 'query: ' and 'passage: ' mapping
- Vector Indexing: L2-normalized numpy dense matrix with fast cosine similarity search
- Serialization: Compressed .npz vector array + .json metadata mapping for fast reloading
"""

from __future__ import annotations

import os
import time
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Tuple

import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


# ─────────────────────────────────────────────────────────────────────────────
# Search Result Data Structure
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class DenseSearchResult:
    """Single ranked result returned by Dense Semantic retrieval."""
    chunk_id: str
    score: float                            # Cosine similarity (-1.0 to 1.0)
    rank: int                               # 1-indexed rank
    text: str                               # Verbatim ground truth evidence text
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
        """Produces exact dictionary consumed by ContextAssembler."""
        dist = max(0.0, 1.0 - self.score)
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
            "heading_path": self.heading_path,
            "score": self.score,
            "distance": round(dist, 4),
            "rank": self.rank,
            "text": self.text,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Embedding Provider Abstraction
# ─────────────────────────────────────────────────────────────────────────────

class BaseEmbeddingProvider(ABC):
    """Abstract interface for embedding generation."""
    @abstractmethod
    def encode_query(self, query: str) -> np.ndarray:
        """Encodes query string into normalized 1D float32 numpy array."""
        pass

    @abstractmethod
    def encode_passage(self, text: str) -> np.ndarray:
        """Encodes document passage into normalized 1D float32 numpy array."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        pass


class ONNXEmbeddingProvider(BaseEmbeddingProvider):
    """Lightweight ONNX Runtime inference provider (Serverless & Docker friendly)."""

    def __init__(self, onnx_model_path: str, tokenizer_path: str, use_e5_prefixes: bool = True):
        self.onnx_model_path = onnx_model_path
        self.tokenizer_path = tokenizer_path
        self.use_e5_prefixes = use_e5_prefixes
        self._session = None
        self._tokenizer = None
        self._dimension = 384

    def _init_runtime(self):
        if self._session is None:
            import onnxruntime as ort
            from transformers import AutoTokenizer

            logging.info(f"Initializing ONNX Inference Session from {self.onnx_model_path}...")
            opts = ort.SessionOptions()
            opts.intra_op_num_threads = 1
            opts.inter_op_num_threads = 1
            self._session = ort.InferenceSession(self.onnx_model_path, sess_options=opts)
            self._tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_path)

    @property
    def dimension(self) -> int:
        return self._dimension

    def _embed(self, text: str) -> np.ndarray:
        self._init_runtime()
        tokens = self._tokenizer([text], return_tensors="np", padding=True, truncation=True, max_length=512)
        ort_inputs = {
            "input_ids": tokens["input_ids"].astype(np.int64),
            "attention_mask": tokens["attention_mask"].astype(np.int64),
        }
        ort_outs = self._session.run(["last_hidden_state"], ort_inputs)[0]
        mask = np.expand_dims(tokens["attention_mask"], -1)
        sum_hidden = np.sum(ort_outs * mask, axis=1)
        sum_mask = np.clip(np.sum(mask, axis=1), a_min=1e-9, a_max=None)
        mean_pooled = sum_hidden / sum_mask
        norm = np.linalg.norm(mean_pooled, axis=-1, keepdims=True)
        return (mean_pooled / norm)[0].astype(np.float32)

    def encode_query(self, query: str) -> np.ndarray:
        formatted = f"query: {query.strip()}" if self.use_e5_prefixes else query.strip()
        return self._embed(formatted)

    def encode_passage(self, text: str) -> np.ndarray:
        formatted = f"passage: {text.strip()}" if self.use_e5_prefixes else text.strip()
        return self._embed(formatted)


class LocalE5EmbeddingProvider(BaseEmbeddingProvider):
    """SentenceTransformers PyTorch provider for local development."""

    def __init__(self, model_name: str, device: Optional[str] = None, use_e5_prefixes: bool = True):
        self.model_name = model_name
        self.device = device
        self.use_e5_prefixes = use_e5_prefixes
        self._model = None
        self._dimension = 384

    def _load_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            logging.info(f"Loading dense embedding model '{self.model_name}' via PyTorch...")
            self._model = SentenceTransformer(self.model_name, device=self.device)
            self._dimension = self._model.get_embedding_dimension()
        return self._model

    @property
    def dimension(self) -> int:
        return self._dimension

    def encode_query(self, query: str) -> np.ndarray:
        model = self._load_model()
        formatted = f"query: {query.strip()}" if self.use_e5_prefixes else query.strip()
        vec = model.encode(formatted, normalize_embeddings=True, show_progress_bar=False)
        return np.asarray(vec, dtype=np.float32)

    def encode_passage(self, text: str) -> np.ndarray:
        model = self._load_model()
        formatted = f"passage: {text.strip()}" if self.use_e5_prefixes else text.strip()
        vec = model.encode(formatted, normalize_embeddings=True, show_progress_bar=False)
        return np.asarray(vec, dtype=np.float32)


# ─────────────────────────────────────────────────────────────────────────────
# Dense Retriever Class
# ─────────────────────────────────────────────────────────────────────────────

class DenseRetriever:
    """
    Independent Dense Vector Retrieval Engine supporting English & Arabic queries.
    Uses EmbeddingProvider abstraction (defaults to ONNX if model.onnx exists, falls back to PyTorch).
    """

    DEFAULT_MODEL_NAME = "intfloat/multilingual-e5-small"
    FALLBACK_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL_NAME,
        device: Optional[str] = None,
        use_e5_prefixes: Optional[bool] = None,
        provider: Optional[BaseEmbeddingProvider] = None,
    ):
        self.model_name = model_name
        self.device = device

        if use_e5_prefixes is None:
            self.use_e5_prefixes = "e5" in model_name.lower()
        else:
            self.use_e5_prefixes = use_e5_prefixes

        # Setup Embedding Provider
        if provider is not None:
            self.provider = provider
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            onnx_path = os.path.join(base_dir, "outputs", "onnx_model", "model.onnx")
            tokenizer_dir = os.path.join(base_dir, "data", "models", "multilingual-e5-small")
            
            if os.path.exists(onnx_path) and os.path.exists(tokenizer_dir):
                self.provider = ONNXEmbeddingProvider(
                    onnx_model_path=onnx_path,
                    tokenizer_path=tokenizer_dir,
                    use_e5_prefixes=self.use_e5_prefixes,
                )
            else:
                self.provider = LocalE5EmbeddingProvider(
                    model_name=self.model_name,
                    device=self.device,
                    use_e5_prefixes=self.use_e5_prefixes,
                )

        self.embedding_dimension: int = self.provider.dimension
        self.corpus_size: int = 0
        self.chunk_ids: List[str] = []
        self.vectors: Optional[np.ndarray] = None  # Shape (N, D), L2-normalized
        self.records_by_id: Dict[str, Dict[str, Any]] = {}

    def encode_passage(self, text: str) -> np.ndarray:
        return self.provider.encode_passage(text)

    def encode_query(self, query: str) -> np.ndarray:
        return self.provider.encode_query(query)

    def index_records(self, records: List[Dict[str, Any]], batch_size: int = 32):
        """Generates dense embeddings for all records and builds the vector index."""
        self.corpus_size = len(records)
        self.chunk_ids = [r["chunk_id"] for r in records]
        self.records_by_id = {r["chunk_id"]: r for r in records}

        t0 = time.time()
        logging.info(f"Generating dense embeddings for {self.corpus_size} chunks...")
        embeddings = [self.encode_passage(r.get("content", {}).get("verbatim_text", "")) for r in records]
        self.vectors = np.asarray(embeddings, dtype=np.float32)
        elapsed = time.time() - t0
        logging.info(
            f"Successfully indexed {self.corpus_size} chunks in {elapsed:.2f}s. "
            f"Matrix shape: {self.vectors.shape}, Dim: {self.embedding_dimension}"
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = -1.0,
    ) -> List[DenseSearchResult]:
        """Performs cosine similarity search against the indexed corpus."""
        if not query or not query.strip():
            return []

        if self.vectors is None or self.corpus_size == 0:
            raise RuntimeError("DenseRetriever has no indexed documents. Call index_records() or load_index() first.")

        query_vec = self.encode_query(query)  # Shape (D,), normalized

        # Dot product with normalized matrix yields exact cosine similarity
        similarities = np.dot(self.vectors, query_vec)  # Shape (N,)

        # Top-K indices sorted descending
        candidate_indices = np.argsort(-similarities)[:top_k]

        results: List[DenseSearchResult] = []
        for rank_idx, doc_idx in enumerate(candidate_indices, start=1):
            score = float(similarities[doc_idx])
            if score < score_threshold:
                continue

            chunk_id = self.chunk_ids[doc_idx]
            rec = self.records_by_id[chunk_id]
            h = rec.get("hierarchy", {})
            p = rec.get("provenance", {})
            m = rec.get("medical_metadata", {})
            metrics = rec.get("metrics", {})
            content = rec.get("content", {})

            result = DenseSearchResult(
                chunk_id=chunk_id,
                score=round(score, 4),
                rank=rank_idx,
                text=content.get("verbatim_text", ""),
                document_id=rec.get("document_id", ""),
                node_id=h.get("node_id", ""),
                parent_id=h.get("parent_id", ""),
                section_number=h.get("section_number"),
                section_title=h.get("section_title", ""),
                heading_path=h.get("heading_path", ""),
                physical_page_start=p.get("physical_page_start"),
                physical_page_end=p.get("physical_page_end"),
                printed_page_start=p.get("printed_page_start"),
                printed_page_end=p.get("printed_page_end"),
                content_type=m.get("content_type", ""),
                retrieval_role=m.get("retrieval_role", ""),
                token_count=metrics.get("token_count", 0),
            )
            results.append(result)

        return results

    def save_index(self, output_npz_path: str, output_meta_path: str):
        """Serializes dense vectors to compressed .npz and metadata to .json."""
        if self.vectors is None:
            raise RuntimeError("No index to save. Run index_records() first.")

        os.makedirs(os.path.dirname(output_npz_path), exist_ok=True)
        os.makedirs(os.path.dirname(output_meta_path), exist_ok=True)

        np.savez_compressed(
            output_npz_path,
            vectors=self.vectors,
            chunk_ids=np.array(self.chunk_ids, dtype=object),
        )

        metadata_payload = {
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dimension,
            "use_e5_prefixes": self.use_e5_prefixes,
            "corpus_size": self.corpus_size,
            "chunk_ids": self.chunk_ids,
        }
        with open(output_meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata_payload, f, ensure_ascii=False, indent=2)

        logging.info(f"Saved dense index vectors to {output_npz_path} and metadata to {output_meta_path}")

    @classmethod
    def load_index(
        cls,
        npz_path: str,
        meta_path: str,
        records_path: str,
        device: Optional[str] = None,
        provider: Optional[BaseEmbeddingProvider] = None,
    ) -> DenseRetriever:
        """Loads precomputed vectors and metadata without re-indexing."""
        if not os.path.exists(npz_path):
            raise FileNotFoundError(f"Dense vector file not found: {npz_path}")
        if not os.path.exists(meta_path):
            raise FileNotFoundError(f"Dense metadata file not found: {meta_path}")
        if not os.path.exists(records_path):
            raise FileNotFoundError(f"Retrieval records not found: {records_path}")

        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        with open(records_path, "r", encoding="utf-8") as f:
            rec_data = json.load(f)

        records_list = rec_data.get("records", [])

        data = np.load(npz_path, allow_pickle=True)
        vectors = data["vectors"]
        chunk_ids = list(data["chunk_ids"])

        retriever = cls(
            model_name=meta.get("model_name", cls.DEFAULT_MODEL_NAME),
            device=device,
            use_e5_prefixes=meta.get("use_e5_prefixes", True),
            provider=provider,
        )
        retriever.embedding_dimension = meta.get("embedding_dimension", vectors.shape[1])
        retriever.corpus_size = len(chunk_ids)
        retriever.chunk_ids = chunk_ids
        retriever.vectors = vectors
        retriever.records_by_id = {r["chunk_id"]: r for r in records_list}

        logging.info(
            f"Successfully loaded DenseRetriever with {retriever.corpus_size} chunks. "
            f"Dim: {retriever.embedding_dimension}"
        )
        return retriever
