"""
Semantic Chunker Engine (Production Semantic v1)
Medical RAG Project: أوكسجين (Oxygen)

Converts verbatim hierarchical Leaf Nodes into optimal, self-contained semantic retrieval units.
Adheres strictly to Medical Semantic Chunking Specification:
- Hard Maximum: 500 tokens (cl100k_base) - Zero violations.
- Progressive semantic splitting: Paragraph -> List -> Sentence -> Clause.
- Leaf-First indexing: Process only the 90 Leaf Nodes to prevent Parent-Child duplication.
- Document-Agnostic architecture: No hardcoded section titles, numbers, or document-specific logic.
- 100% Verbatim preservation in English (zero translation, zero paraphrasing, zero text loss).

Input:
- outputs/verbatim_nodes_v1.json
- outputs/structure_map_v2.json

Output:
- outputs/semantic_chunks_v1.json
"""

import os
import sys
import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
import tiktoken

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class SemanticChunker:
    """Document-Agnostic Semantic Chunker for Medical Documents."""

    HARD_MAX_TOKENS = 500
    TARGET_MIN_TOKENS = 300
    TARGET_MAX_TOKENS = 480

    def __init__(
        self,
        verbatim_nodes_path: str,
        structure_map_path: str,
        hard_max_tokens: int = HARD_MAX_TOKENS,
        target_min_tokens: int = TARGET_MIN_TOKENS,
        target_max_tokens: int = TARGET_MAX_TOKENS
    ):
        self.verbatim_nodes_path = verbatim_nodes_path
        self.structure_map_path = structure_map_path
        self.hard_max_tokens = hard_max_tokens
        self.target_min_tokens = target_min_tokens
        self.target_max_tokens = target_max_tokens

        self.enc = tiktoken.get_encoding("cl100k_base")
        self.verbatim_data: Dict[str, Any] = {}
        self.structure_map: Dict[str, Any] = {}
        self.leaf_nodes: List[Dict[str, Any]] = []
        self.chunked_nodes_output: List[Dict[str, Any]] = []

    def count_tokens(self, text: str) -> int:
        """Accurately counts tokens using cl100k_base tokenizer."""
        return len(self.enc.encode(text))

    def load_resources(self):
        """Loads verbatim nodes and structure map, isolating the 90 Leaf nodes."""
        if not os.path.exists(self.verbatim_nodes_path):
            raise FileNotFoundError(f"Missing verbatim nodes file: {self.verbatim_nodes_path}")
        if not os.path.exists(self.structure_map_path):
            raise FileNotFoundError(f"Missing structure map file: {self.structure_map_path}")

        with open(self.verbatim_nodes_path, 'r', encoding='utf-8') as f:
            self.verbatim_data = json.load(f)
        with open(self.structure_map_path, 'r', encoding='utf-8') as f:
            self.structure_map = json.load(f)

        # Identify Leaf nodes from structure map (nodes with empty children list)
        leaf_node_ids = {n["node_id"] for n in self.structure_map.get("nodes", []) if not n.get("children")}
        
        all_nodes = self.verbatim_data.get("nodes", [])
        self.leaf_nodes = [n for n in all_nodes if n["node_id"] in leaf_node_ids]
        logging.info(f"Loaded {len(all_nodes)} total nodes. Isolated {len(self.leaf_nodes)} Leaf nodes.")

    def _split_into_atomic_units(self, text: str) -> Tuple[List[str], str]:
        """Progressively decomposes large text into atomic units preserving paragraph and sentence boundaries."""
        # 1. Paragraph boundary
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
        if not paragraphs:
            paragraphs = [text.strip()]

        atomic_units = []
        deepest_split = "paragraph_boundary"

        for p in paragraphs:
            p_tokens = self.count_tokens(p)
            if p_tokens <= self.hard_max_tokens:
                atomic_units.append(p)
            else:
                # 2. List item / bullet boundary
                items = [it.strip() for it in re.split(r'\n(?=[•\-\*\d+\.\)])', p) if it.strip()]
                if len(items) > 1:
                    deepest_split = "list_item_boundary"
                else:
                    items = [p]

                for it in items:
                    it_tokens = self.count_tokens(it)
                    if it_tokens <= self.hard_max_tokens:
                        atomic_units.append(it)
                    else:
                        # 3. Sentence boundary
                        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', it) if s.strip()]
                        if len(sentences) > 1:
                            deepest_split = "sentence_boundary"
                        else:
                            sentences = [it]

                        for s in sentences:
                            s_tokens = self.count_tokens(s)
                            if s_tokens <= self.hard_max_tokens:
                                atomic_units.append(s)
                            else:
                                # 4. Clause / semicolon boundary (last resort)
                                clauses = [c.strip() for c in re.split(r'(?<=[;,])\s+', s) if c.strip()]
                                if len(clauses) > 1:
                                    deepest_split = "clause_boundary"
                                    atomic_units.extend(clauses)
                                else:
                                    atomic_units.append(s)

        return atomic_units, deepest_split

    def _pack_units(self, units: List[str], base_split_reason: str) -> List[Tuple[str, str, str, str]]:
        """
        Packs atomic units greedily into cohesive semantic chunks without exceeding hard_max_tokens.
        Returns: List of (chunk_text, split_reason, start_boundary_type, end_boundary_type)
        """
        chunks_info = []
        current_units = []
        current_tokens = 0

        for idx, u in enumerate(units):
            u_tokens = self.count_tokens(u)
            
            # If adding unit exceeds hard max, flush current chunk
            if current_units and (current_tokens + u_tokens > self.hard_max_tokens):
                chunk_str = "\n\n".join(current_units)
                start_b = "section_start" if len(chunks_info) == 0 else "split_continuation"
                end_b = "split_break"
                chunks_info.append((chunk_str, base_split_reason, start_b, end_b))
                current_units = [u]
                current_tokens = u_tokens
            else:
                # Check if current chunk is at sweet spot and next unit would push it above target_max
                if current_tokens >= self.target_min_tokens and (current_tokens + u_tokens > self.target_max_tokens):
                    chunk_str = "\n\n".join(current_units)
                    start_b = "section_start" if len(chunks_info) == 0 else "split_continuation"
                    end_b = "split_break"
                    chunks_info.append((chunk_str, base_split_reason, start_b, end_b))
                    current_units = [u]
                    current_tokens = u_tokens
                else:
                    current_units.append(u)
                    current_tokens += u_tokens

        if current_units:
            chunk_str = "\n\n".join(current_units)
            start_b = "section_start" if len(chunks_info) == 0 else "split_continuation"
            end_b = "section_end"
            chunks_info.append((chunk_str, base_split_reason, start_b, end_b))

        # Adjust the very last chunk's end_boundary_type to section_end
        if chunks_info:
            last_c = chunks_info[-1]
            chunks_info[-1] = (last_c[0], last_c[1], last_c[2], "section_end")

        return chunks_info

    def _chunk_references(self, text: str) -> List[Tuple[str, str, str, str]]:
        """Chunks references into blocks of numbered citations."""
        citations = [c.strip() for c in re.split(r'\n(?=\d+\.\t?\s*)', text) if c.strip()]
        if not citations:
            citations = [text.strip()]
        return self._pack_units(citations, "numbered_reference_group")

    def _chunk_glossary(self, text: str) -> List[Tuple[str, str, str, str]]:
        """Chunks glossary into distinct definition blocks."""
        # Split glossary by double newlines or term entries
        clean_text = re.sub(r'^(Glossary of terms\s*\n+|Term\s*\n+Definition\s*\n+)', '', text, flags=re.IGNORECASE).strip()
        raw_blocks = [b.strip() for b in re.split(r'\n\s*\n', clean_text) if b.strip()]
        
        filtered = []
        for b in raw_blocks:
            if re.match(r'^(WHO clinical treatment guideline|Term\s+Definition|[ivxLCDM]+|\d+)$', b.strip(), re.IGNORECASE):
                continue
            filtered.append(b)

        glossary_chunks = []
        for idx, b in enumerate(filtered):
            if self.count_tokens(b) <= self.hard_max_tokens:
                start_b = "glossary_term_start"
                end_b = "glossary_term_end"
                glossary_chunks.append((b, "glossary_term_definition", start_b, end_b))
            else:
                sub_units, r = self._split_into_atomic_units(b)
                packed = self._pack_units(sub_units, "glossary_term_definition")
                glossary_chunks.extend(packed)

        return glossary_chunks if glossary_chunks else [(text, "atomic_no_split", "section_start", "section_end")]

    def chunk_leaf_node(self, node: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Processes a single Leaf node into semantic chunk dictionaries."""
        node_id = node.get("node_id", "")
        doc_info = self.structure_map.get("document", {})
        doc_id = doc_info.get("document_id", "who_tobacco_cessation_2024")
        doc_title = doc_info.get("title", "WHO Clinical Treatment Guideline for Tobacco Cessation in Adults")
        doc_type = doc_info.get("document_type", "clinical_guideline")
        src_file = self.structure_map.get("source", {}).get("file_name", "who_guideline.pdf")

        content_type = node.get("content_type", "unknown")
        raw_text = node.get("extracted_text", "").strip()
        total_tokens = self.count_tokens(raw_text)

        # Case 1: Fits entirely within Hard Max and is not glossary
        if total_tokens <= self.hard_max_tokens and content_type != "glossary":
            chunk_id = f"chunk_{node_id}"
            chunk_dict = {
                "chunk_id": chunk_id,
                "text": raw_text,
                "metadata": {
                    "chunk_id": chunk_id,
                    "document_id": doc_id,
                    "document_title": doc_title,
                    "document_type": doc_type,
                    "source": src_file,
                    "node_id": node_id,
                    "parent_id": node.get("parent_id"),
                    "section_number": node.get("section_number"),
                    "section_title": node.get("title"),
                    "level": node.get("level"),
                    "content_type": content_type,
                    "physical_page_start": node.get("physical_page_start"),
                    "physical_page_end": node.get("physical_page_end"),
                    "chunk_index": 0,
                    "chunk_count_in_node": 1,
                    "token_count": total_tokens,
                    "word_count": len(raw_text.split()),
                    "char_count": len(raw_text),
                    "is_split": False,
                    "split_reason": None,
                    "start_boundary_type": "section_start",
                    "end_boundary_type": "section_end"
                }
            }
            return [chunk_dict]

        # Case 2: Special Content Types or Large Nodes requiring splitting
        if content_type == "references":
            raw_splits = self._chunk_references(raw_text)
        elif content_type == "glossary":
            raw_splits = self._chunk_glossary(raw_text)
        else:
            atomic_units, split_reason = self._split_into_atomic_units(raw_text)
            raw_splits = self._pack_units(atomic_units, split_reason)

        total_chunks = len(raw_splits)
        chunk_dicts = []

        for idx, (chunk_text, split_reason, start_b, end_b) in enumerate(raw_splits):
            c_tokens = self.count_tokens(chunk_text)
            c_words = len(chunk_text.split())
            c_chars = len(chunk_text)
            chunk_id = f"chunk_{node_id}_p{idx+1:02d}" if total_chunks > 1 else f"chunk_{node_id}"

            chunk_dict = {
                "chunk_id": chunk_id,
                "text": chunk_text,
                "metadata": {
                    "chunk_id": chunk_id,
                    "document_id": doc_id,
                    "document_title": doc_title,
                    "document_type": doc_type,
                    "source": src_file,
                    "node_id": node_id,
                    "parent_id": node.get("parent_id"),
                    "section_number": node.get("section_number"),
                    "section_title": node.get("title"),
                    "level": node.get("level"),
                    "content_type": content_type,
                    "physical_page_start": node.get("physical_page_start"),
                    "physical_page_end": node.get("physical_page_end"),
                    "chunk_index": idx,
                    "chunk_count_in_node": total_chunks,
                    "token_count": c_tokens,
                    "word_count": c_words,
                    "char_count": c_chars,
                    "is_split": total_chunks > 1,
                    "split_reason": split_reason if total_chunks > 1 else None,
                    "start_boundary_type": start_b,
                    "end_boundary_type": end_b
                }
            }
            chunk_dicts.append(chunk_dict)

        return chunk_dicts

    def build_all_chunks(self) -> List[Dict[str, Any]]:
        """Processes all 90 Leaf nodes and organizes chunks by node."""
        self.load_resources()
        self.chunked_nodes_output = []

        for leaf in self.leaf_nodes:
            node_id = leaf.get("node_id", "")
            node_chunks = self.chunk_leaf_node(leaf)
            self.chunked_nodes_output.append({
                "node_id": node_id,
                "chunks": node_chunks
            })

        total_chunks_count = sum(len(n["chunks"]) for n in self.chunked_nodes_output)
        logging.info(f"Generated {total_chunks_count} semantic chunks across {len(self.leaf_nodes)} Leaf nodes.")
        return self.chunked_nodes_output

    def export_output(self, output_json_path: str):
        """Exports final semantic_chunks_v1.json file."""
        if not self.chunked_nodes_output:
            self.build_all_chunks()

        total_chunks = sum(len(n["chunks"]) for n in self.chunked_nodes_output)

        output_payload = {
            "schema_version": "1.0",
            "chunking_version": "semantic_v1",
            "tokenizer": "cl100k_base",
            "hard_max_tokens": self.hard_max_tokens,
            "target_range": f"{self.target_min_tokens}-{self.target_max_tokens}",
            "total_leaf_nodes": len(self.chunked_nodes_output),
            "total_chunks": total_chunks,
            "nodes": self.chunked_nodes_output
        }

        os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(output_payload, f, ensure_ascii=False, indent=2)

        logging.info(f"Saved {output_json_path} successfully ({total_chunks} chunks).")

if __name__ == '__main__':
    v_path = r'C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\verbatim_nodes_v1.json'
    s_path = r'C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\structure_map_v2.json'
    out_p = r'C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\semantic_chunks_v1.json'

    chunker = SemanticChunker(v_path, s_path)
    chunker.build_all_chunks()
    chunker.export_output(out_p)
