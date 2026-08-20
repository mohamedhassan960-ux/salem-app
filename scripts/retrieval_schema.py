"""
Retrieval Schema & Record Architecture — Medical RAG: Oxygen (أوكسجين)
Source Document: WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)

Defines the unified, canonical Retrieval Record contract serving all retrieval layers:
- BM25 Sparse Keyword Retrieval
- Dense Semantic Vector Search
- Reciprocal Rank Fusion (RRF)
- Cross-Encoder / LLM Reranker
- Context Assembler (LLM prompt grounding)

Design Principles:
1. Zero Modification: Verbatim evidence text is 100% preserved with zero summarization.
2. Separation of Concerns: Clear isolation between searchable text, verbatim text,
   structural hierarchy, provenance, and medical metadata.
3. Dual Provenance: Tracks physical PDF pages and printed document pages.
4. Graph Integrity: Maintains parent-child and sibling chunk relationships.
5. Document-Agnostic: Easily adaptable to any structured medical guidelines or papers.
"""

from __future__ import annotations

import os
import json
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Tuple

import tiktoken

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


# ─────────────────────────────────────────────────────────────────────────────
# Sub-Schemas (Components of a Retrieval Record)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class HierarchyMetadata:
    """Structural tree position and relationships."""
    node_id: str
    parent_id: str
    level: int
    section_number: Optional[str]
    section_title: str
    heading_path: str                       # e.g. "3. Recommendations > 3.1 Behavioural support > 3.1.3 Justification..."
    chunk_index: int                        # 0-indexed within the node
    chunk_count: int                        # Total chunks generated for this node
    sibling_chunk_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProvenanceMetadata:
    """Document and page provenance."""
    source_file: str
    physical_page_start: Optional[int]
    physical_page_end: Optional[int]
    printed_page_start: Optional[int]
    printed_page_end: Optional[int]
    source_type: str = "verbatim"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MedicalMetadata:
    """Clinical taxonomy and retrieval categorization."""
    content_type: str                       # e.g. "recommendation", "evidence", "glossary", "methods"
    retrieval_role: str                     # e.g. "clinical_dense_retrieval", "reference_lookup"
    split_reason: Optional[str] = None      # e.g. "sentence_boundary", "paragraph_boundary", None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MetricsMetadata:
    """Length and token statistics."""
    token_count: int                        # cl100k_base tokens
    word_count: int
    character_count: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ContentPayload:
    """Textual representation for retrieval and LLM context generation."""
    verbatim_text: str                      # 100% unaltered ground truth text
    searchable_text: str                    # Breadcrumb-enriched representation for dense/sparse search

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ─────────────────────────────────────────────────────────────────────────────
# Canonical Retrieval Record
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class RetrievalRecord:
    """
    Standardized, self-contained retrieval record representing a single semantic chunk.
    This serves as the single contract across all retrieval and fusion stages.
    """
    chunk_id: str
    document_id: str
    document_title: str
    hierarchy: HierarchyMetadata
    provenance: ProvenanceMetadata
    medical_metadata: MedicalMetadata
    metrics: MetricsMetadata
    content: ContentPayload

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the complete record to a clean nested dictionary."""
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "document_title": self.document_title,
            "hierarchy": self.hierarchy.to_dict(),
            "provenance": self.provenance.to_dict(),
            "medical_metadata": self.medical_metadata.to_dict(),
            "metrics": self.metrics.to_dict(),
            "content": self.content.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> RetrievalRecord:
        """Constructs a RetrievalRecord from a serialized dictionary."""
        return cls(
            chunk_id=d["chunk_id"],
            document_id=d["document_id"],
            document_title=d.get("document_title", ""),
            hierarchy=HierarchyMetadata(**d["hierarchy"]),
            provenance=ProvenanceMetadata(**d["provenance"]),
            medical_metadata=MedicalMetadata(**d["medical_metadata"]),
            metrics=MetricsMetadata(**d["metrics"]),
            content=ContentPayload(**d["content"]),
        )

    def to_context_assembler_dict(self, distance: float = 1.0) -> Dict[str, Any]:
        """
        Converts the record into the exact dictionary format consumed by ContextAssembler.
        Guarantees 100% interoperability with scripts/context_assembler.py.
        """
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "node_id": self.hierarchy.node_id,
            "parent_id": self.hierarchy.parent_id,
            "section_number": self.hierarchy.section_number,
            "section_title": self.hierarchy.section_title,
            "chunk_index": self.hierarchy.chunk_index,
            "chunk_count": self.hierarchy.chunk_count,
            "content_type": self.medical_metadata.content_type,
            "physical_page_start": self.provenance.physical_page_start,
            "physical_page_end": self.provenance.physical_page_end,
            "token_count": self.metrics.token_count,
            "word_count": self.metrics.word_count,
            "character_count": self.metrics.character_count,
            "source_type": self.provenance.source_type,
            "retrieval_role": self.medical_metadata.retrieval_role,
            "split_reason": self.medical_metadata.split_reason,
            "distance": distance,
            "text": self.content.verbatim_text,
        }

    def to_vector_store_payload(self) -> Tuple[str, str, Dict[str, Any]]:
        """
        Formats record for Vector DB indexing (e.g. ChromaDB).
        Returns: (chunk_id, text_to_embed, flat_metadata_dict)
        """
        # Vector stores like ChromaDB require flat scalar metadata values (str, int, float, bool)
        metadata = {
            "document_id": self.document_id,
            "node_id": self.hierarchy.node_id,
            "parent_id": self.hierarchy.parent_id,
            "level": self.hierarchy.level,
            "section_number": self.hierarchy.section_number or "",
            "section_title": self.hierarchy.section_title,
            "heading_path": self.hierarchy.heading_path,
            "chunk_index": self.hierarchy.chunk_index,
            "chunk_count": self.hierarchy.chunk_count,
            "physical_page_start": self.provenance.physical_page_start if self.provenance.physical_page_start is not None else -1,
            "physical_page_end": self.provenance.physical_page_end if self.provenance.physical_page_end is not None else -1,
            "printed_page_start": self.provenance.printed_page_start if self.provenance.printed_page_start is not None else -1,
            "printed_page_end": self.provenance.printed_page_end if self.provenance.printed_page_end is not None else -1,
            "content_type": self.medical_metadata.content_type,
            "retrieval_role": self.medical_metadata.retrieval_role,
            "token_count": self.metrics.token_count,
            "word_count": self.metrics.word_count,
            "character_count": self.metrics.character_count,
        }
        return self.chunk_id, self.content.searchable_text, metadata

    def to_bm25_document(self) -> Dict[str, Any]:
        """
        Formats record for BM25 sparse keyword indexing.
        """
        return {
            "chunk_id": self.chunk_id,
            "searchable_text": self.content.searchable_text,
            "verbatim_text": self.content.verbatim_text,
            "section_title": self.hierarchy.section_title,
            "section_number": self.hierarchy.section_number or "",
            "content_type": self.medical_metadata.content_type,
            "retrieval_role": self.medical_metadata.retrieval_role,
            "physical_page_start": self.provenance.physical_page_start,
            "physical_page_end": self.provenance.physical_page_end,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Schema Builder & Dataset Generator
# ─────────────────────────────────────────────────────────────────────────────

class RetrievalSchemaBuilder:
    """
    Constructs unified RetrievalRecord instances by combining semantic chunks
    with hierarchical information from Structure Map v2.
    """

    def __init__(
        self,
        semantic_chunks_path: str,
        structure_map_path: str,
    ):
        self.semantic_chunks_path = semantic_chunks_path
        self.structure_map_path = structure_map_path
        self.enc = tiktoken.get_encoding("cl100k_base")

        self.structure_map: Dict[str, Any] = {}
        self.node_lookup: Dict[str, Dict[str, Any]] = {}
        self.raw_chunks_data: Dict[str, Any] = {}
        self.records: List[RetrievalRecord] = []

    def load_resources(self):
        """Loads semantic chunks and structure map datasets."""
        if not os.path.exists(self.semantic_chunks_path):
            raise FileNotFoundError(f"Semantic chunks file not found: {self.semantic_chunks_path}")
        if not os.path.exists(self.structure_map_path):
            raise FileNotFoundError(f"Structure map file not found: {self.structure_map_path}")

        with open(self.semantic_chunks_path, "r", encoding="utf-8") as f:
            self.raw_chunks_data = json.load(f)

        with open(self.structure_map_path, "r", encoding="utf-8") as f:
            self.structure_map = json.load(f)

        self.node_lookup = {n["node_id"]: n for n in self.structure_map.get("nodes", [])}
        logging.info(
            f"Loaded {len(self.raw_chunks_data.get('chunks', []))} chunks and "
            f"{len(self.node_lookup)} structure nodes."
        )

    def _build_heading_path(self, node_id: str) -> str:
        """
        Recursively traverses parent nodes to construct the full ancestor breadcrumb path.
        e.g. '3. Recommendations > 3.1 Behavioural support... > 3.1.3 Justification and evidence'
        """
        path_titles: List[str] = []
        curr_id = node_id

        while curr_id and curr_id != "root":
            node = self.node_lookup.get(curr_id)
            if not node:
                break
            title = node.get("title", "").strip()
            if title:
                path_titles.append(title)
            curr_id = node.get("parent_id", "root")

        path_titles.reverse()
        return " > ".join(path_titles) if path_titles else self.node_lookup.get(node_id, {}).get("title", "")

    def _compute_printed_pages(self, node: Dict[str, Any], phys_start: Optional[int], phys_end: Optional[int]) -> Tuple[Optional[int], Optional[int]]:
        """
        Computes printed page start and end numbers based on node metadata and offset rule:
        For main body (physical page >= 19), printed_page = physical_page - 18.
        """
        p_start = node.get("printed_page_start")
        p_end = node.get("printed_page_end")

        if p_start is not None and p_end is not None:
            return p_start, p_end

        if phys_start is not None and phys_start >= 19:
            calc_start = phys_start - 18
            calc_end = (phys_end - 18) if phys_end is not None else calc_start
            return calc_start, calc_end

        return p_start, p_end

    def _build_searchable_text(
        self,
        doc_title: str,
        section_number: Optional[str],
        section_title: str,
        phys_start: Optional[int],
        phys_end: Optional[int],
        printed_start: Optional[int],
        printed_end: Optional[int],
        verbatim_text: str,
    ) -> str:
        """
        Creates an enriched text representation for search embedding/indexing by prefixing
        concise breadcrumb context to the verbatim text, without mutating the verbatim text.
        """
        parts = []
        short_doc = "WHO 2024 Guideline" if "WHO" in doc_title else doc_title
        parts.append(short_doc)

        if section_number and section_title:
            if not section_title.startswith(section_number):
                parts.append(f"{section_number} {section_title}")
            else:
                parts.append(section_title)
        elif section_title:
            parts.append(section_title)

        if phys_start is not None:
            if phys_end is not None and phys_end != phys_start:
                parts.append(f"Pages {phys_start}–{phys_end}")
            else:
                parts.append(f"Page {phys_start}")

        header = f"[{' | '.join(parts)}]\n"
        return header + verbatim_text

    def build_records(self) -> List[RetrievalRecord]:
        """
        Builds all canonical RetrievalRecord instances from raw chunks and structure map.
        """
        if not self.node_lookup:
            self.load_resources()

        raw_chunks = self.raw_chunks_data.get("chunks", [])
        doc_info = self.structure_map.get("document", {})
        doc_id = doc_info.get("document_id", "who_tobacco_cessation_2024")
        doc_title = doc_info.get("title", "WHO clinical treatment guideline for tobacco cessation in adults")

        # Group chunks by node_id to establish sibling lists
        node_to_chunk_ids: Dict[str, List[str]] = {}
        for ch in raw_chunks:
            nid = ch.get("node_id", "")
            node_to_chunk_ids.setdefault(nid, []).append(ch.get("chunk_id", ""))

        records: List[RetrievalRecord] = []

        for ch in raw_chunks:
            chunk_id = ch.get("chunk_id", "")
            node_id = ch.get("node_id", "")
            parent_id = ch.get("parent_id", "root")
            node = self.node_lookup.get(node_id, {})

            level = node.get("level", 1)
            section_number = ch.get("section_number") or node.get("section_number")
            section_title = ch.get("section_title") or node.get("title") or ""
            heading_path = self._build_heading_path(node_id)
            chunk_index = ch.get("chunk_index", 0)
            chunk_count = ch.get("chunk_count", 1)
            sibling_ids = node_to_chunk_ids.get(node_id, [chunk_id])

            phys_start = ch.get("physical_page_start") or node.get("physical_page_start")
            phys_end = ch.get("physical_page_end") or node.get("physical_page_end")
            printed_start, printed_end = self._compute_printed_pages(node, phys_start, phys_end)

            content_type = ch.get("content_type") or node.get("content_type") or "narrative"
            retrieval_role = ch.get("retrieval_role", "clinical_dense_retrieval")
            split_reason = ch.get("split_reason")

            verbatim_text = ch.get("text", "")
            token_count = ch.get("token_count") or len(self.enc.encode(verbatim_text))
            word_count = ch.get("word_count") or len(verbatim_text.split())
            char_count = ch.get("character_count") or len(verbatim_text)

            searchable_text = self._build_searchable_text(
                doc_title=doc_title,
                section_number=section_number,
                section_title=section_title,
                phys_start=phys_start,
                phys_end=phys_end,
                printed_start=printed_start,
                printed_end=printed_end,
                verbatim_text=verbatim_text,
            )

            record = RetrievalRecord(
                chunk_id=chunk_id,
                document_id=doc_id,
                document_title=doc_title,
                hierarchy=HierarchyMetadata(
                    node_id=node_id,
                    parent_id=parent_id,
                    level=level,
                    section_number=section_number,
                    section_title=section_title,
                    heading_path=heading_path,
                    chunk_index=chunk_index,
                    chunk_count=chunk_count,
                    sibling_chunk_ids=sibling_ids,
                ),
                provenance=ProvenanceMetadata(
                    source_file="data/who_extracted.txt",
                    physical_page_start=phys_start,
                    physical_page_end=phys_end,
                    printed_page_start=printed_start,
                    printed_page_end=printed_end,
                    source_type="verbatim",
                ),
                medical_metadata=MedicalMetadata(
                    content_type=content_type,
                    retrieval_role=retrieval_role,
                    split_reason=split_reason,
                ),
                metrics=MetricsMetadata(
                    token_count=token_count,
                    word_count=word_count,
                    character_count=char_count,
                ),
                content=ContentPayload(
                    verbatim_text=verbatim_text,
                    searchable_text=searchable_text,
                ),
            )
            records.append(record)

        self.records = records
        logging.info(f"Successfully constructed {len(self.records)} canonical RetrievalRecord objects.")
        return self.records

    def export_records(self, output_json_path: str, output_jsonl_path: str):
        """Exports canonical retrieval records dataset in both JSON and JSONL formats."""
        if not self.records:
            self.build_records()

        os.makedirs(os.path.dirname(output_json_path), exist_ok=True)

        payload = {
            "schema_version": "2.0",
            "document": self.structure_map.get("document", {}),
            "total_records": len(self.records),
            "records": [r.to_dict() for r in self.records],
        }

        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        with open(output_jsonl_path, "w", encoding="utf-8") as f:
            for r in self.records:
                f.write(json.dumps(r.to_dict(), ensure_ascii=False) + "\n")

        logging.info(
            f"Exported {len(self.records)} records to {output_json_path} and {output_jsonl_path}"
        )


if __name__ == "__main__":
    chunks_in = r"C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\semantic_chunks_v2.json"
    smap_in = r"C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\structure_map_v2.json"
    out_json = r"C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\retrieval_records_v2.json"
    out_jsonl = r"C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\retrieval_records_v2.jsonl"

    builder = RetrievalSchemaBuilder(chunks_in, smap_in)
    builder.build_records()
    builder.export_records(out_json, out_jsonl)
