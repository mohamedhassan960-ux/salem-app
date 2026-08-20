"""
Retrieval Pipeline — Dense Semantic Retrieval
Medical RAG Project: Oxygen (أوكسجين)

Receives a natural-language query (English or Arabic) and returns the top-k most
semantically relevant chunks from the ChromaDB local vector store.

Design principles:
- Document-Agnostic: zero hardcoded section titles or WHO-specific logic.
- Read-Only: does not modify ChromaDB, semantic_chunks_v1.json, or any prior output.
- Stateless per call: model is loaded once at class construction, reused across calls.
- Defensive: validates all inputs and raises informative exceptions.
"""

import os
from typing import List, Dict, Any, Optional
import chromadb
from sentence_transformers import SentenceTransformer


class RetrievalPipeline:
    """Dense semantic retrieval over a ChromaDB vector store."""

    DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    DEFAULT_COLLECTION_NAME = "medical_knowledge"
    DEFAULT_DB_PATH = r"C:\Users\moham\OneDrive\Apps\اوكسجين\data\chroma_db"

    def __init__(
        self,
        db_path: str = DEFAULT_DB_PATH,
        collection_name: str = DEFAULT_COLLECTION_NAME,
        model_name: str = DEFAULT_MODEL_NAME,
    ):
        self.db_path = db_path
        self.collection_name = collection_name
        self.model_name = model_name
        self._model: Optional[SentenceTransformer] = None
        self._collection = None
        self._total_chunks: Optional[int] = None

    # ------------------------------------------------------------------ #
    # Lazy initialisation                                                  #
    # ------------------------------------------------------------------ #

    def _load_model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def _get_collection(self):
        if self._collection is None:
            if not os.path.exists(self.db_path):
                raise FileNotFoundError(
                    f"ChromaDB path not found: '{self.db_path}'. "
                    "Run scripts/build_vector_store.py first."
                )
            client = chromadb.PersistentClient(path=self.db_path)
            try:
                self._collection = client.get_collection(self.collection_name)
            except Exception:
                available = [c.name for c in client.list_collections()]
                raise ValueError(
                    f"Collection '{self.collection_name}' not found in ChromaDB. "
                    f"Available collections: {available}"
                )
        return self._collection

    def _get_total_chunks(self) -> int:
        if self._total_chunks is None:
            self._total_chunks = self._get_collection().count()
        return self._total_chunks

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Execute a dense similarity search and return ranked results.

        Parameters
        ----------
        query  : Natural-language question (English or Arabic).
        top_k  : Number of top results to return (1 ≤ top_k ≤ collection size).

        Returns
        -------
        List of result dicts, sorted by cosine distance (ascending = most similar first).
        Each dict contains: chunk_id, node_id, parent_id, section_title,
        section_number, content_type, physical_page_start, physical_page_end,
        chunk_index, text, distance, and all other stored metadata.

        Raises
        ------
        ValueError  : Empty query, invalid top_k, or no results found.
        FileNotFoundError : ChromaDB path missing.
        """

        # --- Input validation ---
        if not query or not query.strip():
            raise ValueError("query must be a non-empty string.")

        if not isinstance(top_k, int) or top_k < 1:
            raise ValueError(f"top_k must be a positive integer (got {top_k!r}).")

        total = self._get_total_chunks()
        if top_k > total:
            raise ValueError(
                f"top_k={top_k} exceeds the number of indexed chunks ({total}). "
                f"Use top_k ≤ {total}."
            )

        # --- Embed query ---
        model = self._load_model()
        query_embedding = model.encode([query.strip()])[0].tolist()

        # --- Search ---
        collection = self._get_collection()
        raw = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        ids = raw["ids"][0]
        docs = raw["documents"][0]
        metas = raw["metadatas"][0]
        distances = raw["distances"][0]

        if not ids:
            raise ValueError("No results returned from ChromaDB.")

        # --- Build structured result list ---
        results: List[Dict[str, Any]] = []
        for i, chunk_id in enumerate(ids):
            meta = metas[i]
            result = {
                # Required fields
                "chunk_id": chunk_id,
                "node_id": meta.get("node_id", ""),
                "parent_id": meta.get("parent_id", ""),
                "section_title": meta.get("section_title", ""),
                "section_number": meta.get("section_number", ""),
                "content_type": meta.get("content_type", ""),
                "physical_page_start": meta.get("physical_page_start"),
                "physical_page_end": meta.get("physical_page_end"),
                "chunk_index": meta.get("chunk_index"),
                "text": docs[i],
                "distance": round(distances[i], 6),
                # Additional provenance fields
                "document_id": meta.get("document_id", ""),
                "document_title": meta.get("document_title", ""),
                "document_type": meta.get("document_type", ""),
                "token_count": meta.get("token_count"),
                "word_count": meta.get("word_count"),
                "is_split": meta.get("is_split"),
                "split_reason": meta.get("split_reason", ""),
            }
            results.append(result)

        # Guarantee ascending distance ordering (most similar first)
        results.sort(key=lambda r: r["distance"])
        return results
