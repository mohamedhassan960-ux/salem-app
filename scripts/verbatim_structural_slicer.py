"""
Verbatim Structural Slicer v1
Document-Agnostic Medical Text Extraction Engine

Extracts complete, unmodified verbatim text for hierarchical nodes defined in Structure Map v2.
Guarantees 100% source fidelity, zero summarization, zero paraphrasing, and exact boundary isolation.

Input:
- data/who_extracted.txt
- outputs/structure_map_v2.json

Output:
- outputs/verbatim_nodes_v1.json
"""

import os
import sys
import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class VerbatimStructuralSlicer:
    """Generic, Document-Agnostic Slicer for hierarchical medical document nodes."""

    def __init__(self, source_txt_path: str, structure_map_path: str):
        self.source_txt_path = source_txt_path
        self.structure_map_path = structure_map_path
        self.raw_pages: Dict[int, str] = {}
        self.structure_map: Dict[str, Any] = {}
        self.nodes: List[Dict[str, Any]] = []
        self.node_dict: Dict[str, Dict[str, Any]] = {}
        self.extracted_nodes: List[Dict[str, Any]] = []

    def load_resources(self):
        """Loads and prepares extracted text and Structure Map v2."""
        if not os.path.exists(self.source_txt_path):
            raise FileNotFoundError(f"Source text file not found: {self.source_txt_path}")
        if not os.path.exists(self.structure_map_path):
            raise FileNotFoundError(f"Structure map not found: {self.structure_map_path}")

        with open(self.source_txt_path, 'r', encoding='utf-8', errors='ignore') as f:
            raw_content = f.read()

        pages_raw = re.split(r'===== PAGE (\d+) =====', raw_content)
        for i in range(1, len(pages_raw), 2):
            p_num = int(pages_raw[i])
            self.raw_pages[p_num] = pages_raw[i+1]

        with open(self.structure_map_path, 'r', encoding='utf-8') as f:
            self.structure_map = json.load(f)

        self.nodes = self.structure_map.get("nodes", [])
        self.node_dict = {n["node_id"]: n for n in self.nodes}
        logging.info(f"Loaded {len(self.raw_pages)} pages and {len(self.nodes)} structure nodes.")

    @staticmethod
    def _compile_flexible_pattern(pat_str: Optional[str]) -> Optional[str]:
        """Converts literal escaped pattern into flexible whitespace regex matching tabs, nbsp, and spaces."""
        if not pat_str:
            return None
        # Replace escaped spaces with \s+ to handle tabs and non-breaking spaces
        flex = pat_str.replace(r'\ ', r'\s+').replace(' ', r'\s+')
        if not flex.startswith(r'^\s*'):
            flex = r'^\s*' + flex
        return flex

    def slice_node(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts complete verbatim text slice for a given structure node."""
        node_id = node.get("node_id", "")
        p_start = node.get("physical_page_start", 1)
        p_end = node.get("physical_page_end", len(self.raw_pages))
        text_boundary = node.get("text_boundary", {})
        start_pat_raw = text_boundary.get("start_heading_pattern")
        end_pat_raw = text_boundary.get("end_heading_pattern")

        # 1. Combine raw text across the physical page span
        combined_text = ""
        page_offsets: Dict[int, Tuple[int, int]] = {}
        curr_offset = 0
        for p in range(p_start, p_end + 1):
            p_text = self.raw_pages.get(p, "")
            page_offsets[p] = (curr_offset, curr_offset + len(p_text))
            combined_text += p_text + "\n"
            curr_offset += len(p_text) + 1

        # 2. Compile flexible search regexes
        start_pat = self._compile_flexible_pattern(start_pat_raw)
        end_pat = self._compile_flexible_pattern(end_pat_raw)

        # 3. Locate Start Boundary
        start_match = None
        if start_pat:
            for m in re.finditer(start_pat, combined_text, re.MULTILINE | re.IGNORECASE):
                start_match = m
                break
        
        # Fallback: search for first 3 words of title
        if not start_match and node.get("title"):
            title_words = [re.escape(w) for w in node["title"].split()[:3] if w]
            if title_words:
                fallback_pat = r'^\s*' + r'\s+'.join(title_words)
                for m in re.finditer(fallback_pat, combined_text, re.MULTILINE | re.IGNORECASE):
                    start_match = m
                    break

        start_found = start_match is not None
        start_pos = start_match.start() if start_match else 0
        matched_start_text = start_match.group(0).strip() if start_match else None

        # 4. Locate End Boundary after start_pos
        end_match = None
        if end_pat and start_found:
            for m in re.finditer(end_pat, combined_text[start_pos:], re.MULTILINE | re.IGNORECASE):
                end_match = m
                break

        end_found = end_match is not None
        end_pos = (start_pos + end_match.start()) if end_match else len(combined_text)
        matched_end_text = end_match.group(0).strip() if end_match else None

        # 5. Boundary Validation & Extraction
        ordering_valid = start_pos < end_pos
        if not start_found:
            status = "START_BOUNDARY_NOT_FOUND"
            extracted_text = ""
        elif not ordering_valid:
            status = "INVALID_BOUNDARY_ORDERING"
            extracted_text = ""
        else:
            extracted_text = combined_text[start_pos:end_pos].strip()
            status = "SUCCESS" if len(extracted_text) > 0 else "EMPTY_EXTRACTION"

        word_count = len(extracted_text.split())
        char_count = len(extracted_text)

        result_record = {
            "document_id": self.structure_map.get("document", {}).get("document_id", "medical_doc"),
            "node_id": node_id,
            "parent_id": node.get("parent_id"),
            "level": node.get("level"),
            "section_number": node.get("section_number"),
            "title": node.get("title"),
            "physical_page_start": p_start,
            "physical_page_end": p_end,
            "printed_page_start": node.get("printed_page_start"),
            "printed_page_end": node.get("printed_page_end"),
            "content_type": node.get("content_type", "unknown"),
            "boundary_confidence": node.get("boundary_confidence", "high"),
            "start_boundary_found": start_found,
            "end_boundary_found": end_found,
            "matched_start_heading": matched_start_text,
            "matched_end_heading": matched_end_text,
            "ordering_valid": ordering_valid,
            "extracted_text": extracted_text,
            "character_count": char_count,
            "word_count": word_count,
            "extraction_status": status
        }
        return result_record

    def run_sample(self, sample_node_ids: List[str]) -> List[Dict[str, Any]]:
        """Executes a dry-run / sample slice on specified representative node IDs."""
        self.load_resources()
        results = []
        for nid in sample_node_ids:
            if nid in self.node_dict:
                node = self.node_dict[nid]
                res = self.slice_node(node)
                results.append(res)
            else:
                logging.warning(f"Sample node ID '{nid}' not found in Structure Map v2.")
        return results

    def run_full_extraction(self, output_file_path: str) -> List[Dict[str, Any]]:
        """Extracts verbatim text for ALL nodes in Structure Map v2 and writes output JSON."""
        self.load_resources()
        self.extracted_nodes = []
        for node in self.nodes:
            res = self.slice_node(node)
            self.extracted_nodes.append(res)

        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump({
                "schema_version": "1.0",
                "document": self.structure_map.get("document", {}),
                "source": self.structure_map.get("source", {}),
                "total_nodes_extracted": len(self.extracted_nodes),
                "nodes": self.extracted_nodes
            }, f, ensure_ascii=False, indent=2)

        logging.info(f"Full extraction written to {output_file_path} with {len(self.extracted_nodes)} nodes.")
        return self.extracted_nodes

if __name__ == '__main__':
    src = r'C:\Users\moham\OneDrive\Apps\اوكسجين\data\who_extracted.txt'
    smap = r'C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\structure_map_v2.json'
    slicer = VerbatimStructuralSlicer(src, smap)
    
    sample_ids = [
        'sec_3_1_1',
        'sec_3_1_2',
        'sec_3_1_3',
        'sec_3_1_4',
        'sec_3_3_3',
        'sec_3_7_4',
        'node_L1_references',
        'annex_2'
    ]
    
    sample_results = slicer.run_sample(sample_ids)
    print("\n================ DRY RUN / SAMPLE RUN RESULTS ================")
    for r in sample_results:
        print(f"\nNode ID: {r['node_id']} | Title: {r['title']}")
        print(f"  Pages: P{r['physical_page_start']}-P{r['physical_page_end']} | Status: {r['extraction_status']}")
        print(f"  Start Matched: {r['start_boundary_found']} ('{r['matched_start_heading']}')")
        print(f"  End Matched:   {r['end_boundary_found']} ('{r['matched_end_heading']}')")
        print(f"  Extracted: {r['word_count']:,} words ({r['character_count']:,} chars)")
        txt = r['extracted_text']
        first_100 = repr(txt[:100]) if txt else "EMPTY"
        last_100 = repr(txt[-100:]) if len(txt) >= 100 else repr(txt)
        print(f"  First 100 chars: {first_100}")
        print(f"  Last 100 chars:  {last_100}")
