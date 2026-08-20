"""
BM25 Sparse Retrieval Engine — Medical RAG: Oxygen (أوكسجين)
Source Document: WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)

Provides a self-contained, mathematically rigorous BM25Okapi implementation tailored
specifically for medical information retrieval:
- MedicalTokenizer: Preserves drug names, clinical abbreviations, GRADE terms, and hyphenated compounds.
- BM25Index: Fast inverted index with Robertson-Spärck Jones IDF and Okapi term frequency saturation.
- Multi-field support: Enables side-by-side comparison between verbatim_text and searchable_text.
- Traceability: Returns full provenance and hierarchy metadata alongside BM25 scores.
"""

from __future__ import annotations

import os
import re
import math
import json
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Set, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


# ─────────────────────────────────────────────────────────────────────────────
# Medical Tokenizer & Preprocessor
# ─────────────────────────────────────────────────────────────────────────────

# Standard English stopwords that carry zero discriminative clinical signal.
# Noticeably excluded: words with clinical weight like "not", "no", "risk", "harm", "dose", "mg".
MEDICAL_STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll",
    "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's",
    "the", "their", "theirs", "them", "themselves", "then", "there", "there's",
    "these", "they", "they'd", "they'll", "they're", "they've", "this", "those",
    "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we",
    "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when",
    "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why",
    "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll",
    "you're", "you've", "your", "yours", "yourself", "yourselves"
}


class MedicalTokenizer:
    """
    Deterministic, clinical-aware tokenizer designed for medical RAG retrieval.
    
    Principles:
    1. Case folding (lowercase) to match query variants ('NRT' == 'nrt', 'Varenicline' == 'varenicline').
    2. Compound preservation: splits on whitespace and punctuation while extracting sub-tokens from
       hyphenated terms (e.g. 'face-to-face' yields 'face-to-face', 'face').
    3. Alphanumeric & Greek symbol support (e.g. 'α4β2', 'rec_01', '3.1.1').
    4. Conservative stopword filtering to retain clinical intent.
    """

    # Regex matching alphanumeric words, Greek letters, and hyphenated terms
    TOKEN_PATTERN = re.compile(r"[a-z0-9\u0370-\u03ff]+(?:[-_][a-z0-9\u0370-\u03ff]+)*", re.IGNORECASE)

    def __init__(self, filter_stopwords: bool = True):
        self.filter_stopwords = filter_stopwords

    def tokenize(self, text: str) -> List[str]:
        """Tokenizes medical text into normalized, filtered tokens."""
        if not text or not isinstance(text, str):
            return []

        # Find all valid token matches
        matches = self.TOKEN_PATTERN.findall(text.lower())
        tokens: List[str] = []

        for m in matches:
            # Skip single-character non-numeric tokens unless meaningful
            if len(m) == 1 and not m.isdigit() and m not in {"α", "β", "p"}:
                continue

            if self.filter_stopwords and m in MEDICAL_STOPWORDS:
                continue

            tokens.append(m)

            # If hyphenated, also add the constituent parts to allow partial matching
            if "-" in m:
                subparts = [p for p in m.split("-") if p]
                for p in subparts:
                    if len(p) > 1 and (not self.filter_stopwords or p not in MEDICAL_STOPWORDS):
                        tokens.append(p)

        return tokens


# ─────────────────────────────────────────────────────────────────────────────
# BM25 Engine Data Structures
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class BM25SearchResult:
    """Single ranked result returned by BM25 retrieval."""
    chunk_id: str
    score: float
    rank: int
    text: str                               # Full verbatim text for LLM / Context Assembler
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
        # Convert BM25 score to an inverse distance surrogate (lower is better for sort)
        # distance = 1.0 / (1.0 + score)
        surrogate_dist = 1.0 / (1.0 + max(0.0, self.score))
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
            "distance": surrogate_dist,
            "bm25_score": self.score,
            "rank": self.rank,
            "text": self.text,
        }


# ─────────────────────────────────────────────────────────────────────────────
# BM25 Index Implementation (BM25Okapi)
# ─────────────────────────────────────────────────────────────────────────────

class BM25Retriever:
    """
    Independent, reproducible BM25Okapi Sparse Retrieval Engine.

    Parameters:
    - k1 (float): Term frequency saturation parameter (default 1.5).
    - b (float): Document length normalization parameter (default 0.75).
    - text_field (str): Which field to index: 'searchable_text' or 'verbatim_text'.
    - filter_stopwords (bool): Whether to apply medical stopword filtering.
    """

    def __init__(
        self,
        k1: float = 1.5,
        b: float = 0.75,
        text_field: str = "searchable_text",
        filter_stopwords: bool = True,
    ):
        self.k1 = k1
        self.b = b
        self.text_field = text_field
        self.tokenizer = MedicalTokenizer(filter_stopwords=filter_stopwords)

        self.corpus_size: int = 0
        self.avgdl: float = 0.0
        self.doc_lengths: List[int] = []
        self.chunk_ids: List[str] = []
        self.records_by_id: Dict[str, Dict[str, Any]] = {}

        # Inverted index: term -> {doc_idx: term_frequency}
        self.inverted_index: Dict[str, Dict[int, int]] = {}
        # Document frequencies: term -> count of docs containing term
        self.doc_frequencies: Dict[str, int] = {}
        # Precomputed IDFs: term -> idf_value
        self.idf: Dict[str, float] = {}

    def index_records(self, records: List[Dict[str, Any]]):
        """
        Builds the BM25 inverted index from a list of RetrievalRecord dictionaries.
        """
        self.corpus_size = len(records)
        self.doc_lengths = []
        self.chunk_ids = []
        self.records_by_id = {}
        self.inverted_index = {}
        self.doc_frequencies = {}
        self.idf = {}

        total_length = 0

        for doc_idx, rec in enumerate(records):
            chunk_id = rec["chunk_id"]
            self.chunk_ids.append(chunk_id)
            self.records_by_id[chunk_id] = rec

            # Determine text content based on text_field configuration
            if self.text_field == "searchable_text":
                content_text = rec.get("content", {}).get("searchable_text", "")
            else:
                content_text = rec.get("content", {}).get("verbatim_text", "")

            tokens = self.tokenizer.tokenize(content_text)
            doc_len = len(tokens)
            self.doc_lengths.append(doc_len)
            total_length += doc_len

            # Compute term frequencies for this document
            tf_map: Dict[str, int] = {}
            for t in tokens:
                tf_map[t] = tf_map.get(t, 0) + 1

            for t, tf in tf_map.items():
                if t not in self.inverted_index:
                    self.inverted_index[t] = {}
                self.inverted_index[t][doc_idx] = tf
                self.doc_frequencies[t] = self.doc_frequencies.get(t, 0) + 1

        self.avgdl = (total_length / self.corpus_size) if self.corpus_size > 0 else 0.0

        # Precompute Robertson-Spärck Jones IDF with smoothing
        for term, df in self.doc_frequencies.items():
            # BM25 standard smooth IDF: ln(1 + (N - df + 0.5) / (df + 0.5))
            self.idf[term] = math.log(1.0 + (self.corpus_size - df + 0.5) / (df + 0.5))

        logging.info(
            f"Indexed {self.corpus_size} chunks. Unique terms: {len(self.inverted_index)}. "
            f"Avg doc length: {self.avgdl:.2f} tokens. Field indexed: '{self.text_field}'."
        )

    def retrieve(self, query: str, top_k: int = 5) -> List[BM25SearchResult]:
        """
        Executes BM25 scoring for a query and returns top-k ranked results.

        Parameters:
        - query (str): Natural language clinical question or keywords.
        - top_k (int): Number of top documents to return.

        Returns:
        - List of BM25SearchResult sorted by score descending.
        """
        if not query or not query.strip():
            return []

        query_tokens = self.tokenizer.tokenize(query)
        if not query_tokens or self.corpus_size == 0:
            return []

        scores: Dict[int, float] = {}

        for t in query_tokens:
            if t not in self.inverted_index:
                continue

            term_idf = self.idf.get(t, 0.0)
            doc_tfs = self.inverted_index[t]

            for doc_idx, tf in doc_tfs.items():
                doc_len = self.doc_lengths[doc_idx]
                # Length normalization denominator
                denom = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avgdl))
                numerator = tf * (self.k1 + 1.0)
                term_score = term_idf * (numerator / denom)

                scores[doc_idx] = scores.get(doc_idx, 0.0) + term_score

        if not scores:
            return []

        # Sort candidate documents by score descending
        sorted_candidates = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:top_k]

        results: List[BM25SearchResult] = []
        for rank, (doc_idx, score) in enumerate(sorted_candidates, start=1):
            chunk_id = self.chunk_ids[doc_idx]
            rec = self.records_by_id[chunk_id]
            h = rec.get("hierarchy", {})
            p = rec.get("provenance", {})
            m = rec.get("medical_metadata", {})
            metrics = rec.get("metrics", {})
            content = rec.get("content", {})

            result = BM25SearchResult(
                chunk_id=chunk_id,
                score=round(score, 4),
                rank=rank,
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

    def save_index(self, output_path: str):
        """Serializes index state to JSON file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        # Convert inverted index keys for serialization
        payload = {
            "k1": self.k1,
            "b": self.b,
            "text_field": self.text_field,
            "corpus_size": self.corpus_size,
            "avgdl": self.avgdl,
            "doc_lengths": self.doc_lengths,
            "chunk_ids": self.chunk_ids,
            "doc_frequencies": self.doc_frequencies,
            "idf": self.idf,
            "inverted_index": {
                term: {str(d): tf for d, tf in doc_map.items()}
                for term, doc_map in self.inverted_index.items()
            },
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)
        logging.info(f"Saved BM25 index to {output_path}")

    @classmethod
    def load_index(
        cls,
        index_path: str,
        records_path: str,
    ) -> BM25Retriever:
        """Loads serialized BM25 index and binds to retrieval records."""
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"BM25 index not found: {index_path}")
        if not os.path.exists(records_path):
            raise FileNotFoundError(f"Retrieval records not found: {records_path}")

        with open(index_path, "r", encoding="utf-8") as f:
            idx_data = json.load(f)

        with open(records_path, "r", encoding="utf-8") as f:
            rec_data = json.load(f)

        records_list = rec_data.get("records", [])

        retriever = cls(
            k1=idx_data.get("k1", 1.5),
            b=idx_data.get("b", 0.75),
            text_field=idx_data.get("text_field", "searchable_text"),
        )
        retriever.corpus_size = idx_data["corpus_size"]
        retriever.avgdl = idx_data["avgdl"]
        retriever.doc_lengths = idx_data["doc_lengths"]
        retriever.chunk_ids = idx_data["chunk_ids"]
        retriever.doc_frequencies = idx_data["doc_frequencies"]
        retriever.idf = idx_data["idf"]
        retriever.inverted_index = {
            term: {int(d): tf for d, tf in doc_map.items()}
            for term, doc_map in idx_data["inverted_index"].items()
        }
        retriever.records_by_id = {r["chunk_id"]: r for r in records_list}

        logging.info(f"Successfully loaded BM25 index with {retriever.corpus_size} chunks.")
        return retriever


def build_and_save_default_bm25_index(
    records_path: str = r"C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\retrieval_records_v2.json",
    output_index_path: str = r"C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\bm25_index_v2.json",
    text_field: str = "searchable_text",
) -> BM25Retriever:
    """Builds and serializes the default BM25 retriever."""
    with open(records_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    records = data.get("records", [])

    retriever = BM25Retriever(text_field=text_field)
    retriever.index_records(records)
    retriever.save_index(output_index_path)
    return retriever


if __name__ == "__main__":
    build_and_save_default_bm25_index()
