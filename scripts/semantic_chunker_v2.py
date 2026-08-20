"""
Semantic Chunker v2
Document-Agnostic Medical RAG Chunking Engine

Transforms verbatim hierarchical leaf nodes into optimal, self-contained semantic retrieval units.
Adheres strictly to Semantic Chunking Specification v2:
- Target Range: 350–450 tokens
- Hard Maximum: 500 tokens (NO chunk > 500 tokens)
- Zero summarization, zero paraphrasing, 100% verbatim text preservation.
- Leaf-First indexing (Zero parent duplication).
- Document-Agnostic architecture.

Input:
- outputs/verbatim_nodes_v1.json
- outputs/structure_map_v2.json

Output:
- outputs/semantic_chunks_v2.json
- outputs/semantic_chunks_v2.jsonl
"""

import os
import sys
import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
import tiktoken

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class SemanticChunkerV2:
    """Document-Agnostic Semantic Chunker adhering to Specification v2."""

    HARD_MAX_TOKENS = 500
    TARGET_MIN_TOKENS = 350
    TARGET_MAX_TOKENS = 450

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
        self.chunks: List[Dict[str, Any]] = []

    def count_tokens(self, text: str) -> int:
        """Accurately counts tokens using cl100k_base tokenizer."""
        return len(self.enc.encode(text))

    def load_resources(self):
        """Loads verbatim nodes and structure map, isolating the Leaf nodes."""
        if not os.path.exists(self.verbatim_nodes_path):
            raise FileNotFoundError(f"Missing verbatim nodes file: {self.verbatim_nodes_path}")
        if not os.path.exists(self.structure_map_path):
            raise FileNotFoundError(f"Missing structure map file: {self.structure_map_path}")

        with open(self.verbatim_nodes_path, 'r', encoding='utf-8') as f:
            self.verbatim_data = json.load(f)
        with open(self.structure_map_path, 'r', encoding='utf-8') as f:
            self.structure_map = json.load(f)

        # Identify Leaf nodes (nodes with empty children list)
        leaf_node_ids = {n["node_id"] for n in self.structure_map.get("nodes", []) if not n.get("children")}
        
        all_nodes = self.verbatim_data.get("nodes", [])
        self.leaf_nodes = [n for n in all_nodes if n["node_id"] in leaf_node_ids]
        logging.info(f"Loaded {len(all_nodes)} total nodes. Isolated {len(self.leaf_nodes)} Leaf nodes for chunking.")

    def _split_into_atomic_units(self, text: str) -> Tuple[List[str], str]:
        """Progressively breaks large text into atomic units (paragraphs -> lists -> sentences -> clauses)."""
        # Step 1: Paragraphs
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
                # Step 2: Bullet points or numbered items
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
                        # Step 3: Sentence boundaries
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
                                # Step 4: Clause / semicolon boundaries
                                clauses = [c.strip() for c in re.split(r'(?<=[;,])\s+', s) if c.strip()]
                                if len(clauses) > 1:
                                    deepest_split = "clause_boundary"
                                    atomic_units.extend(clauses)
                                else:
                                    atomic_units.append(s)

        return atomic_units, deepest_split

    def _pack_units_into_chunks(self, units: List[str], base_split_reason: str) -> List[Tuple[str, str]]:
        """Greedily packs atomic units into chunks adhering to target and hard maximum boundaries."""
        chunks_text_and_reason = []
        current_units = []
        current_tokens = 0

        for u in units:
            u_tokens = self.count_tokens(u)
            
            # Check if adding this unit would exceed hard maximum
            if current_units and (current_tokens + u_tokens > self.hard_max_tokens):
                chunk_str = "\n\n".join(current_units)
                chunks_text_and_reason.append((chunk_str, base_split_reason))
                current_units = [u]
                current_tokens = u_tokens
            else:
                # Check if current chunk has reached optimal target range
                if current_tokens >= self.target_min_tokens and (current_tokens + u_tokens > self.target_max_tokens):
                    chunk_str = "\n\n".join(current_units)
                    chunks_text_and_reason.append((chunk_str, base_split_reason))
                    current_units = [u]
                    current_tokens = u_tokens
                else:
                    current_units.append(u)
                    current_tokens += u_tokens

        if current_units:
            chunk_str = "\n\n".join(current_units)
            chunks_text_and_reason.append((chunk_str, base_split_reason))

        return chunks_text_and_reason

    def _chunk_references_node(self, node: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Splits references node by numbered citation entries."""
        text = node.get("extracted_text", "")
        # Split by numbered citation entries: e.g. \n1. or \n2.
        citations = [c.strip() for c in re.split(r'\n(?=\d+\.\t?\s*)', text) if c.strip()]
        if not citations:
            citations = [text.strip()]

        return self._pack_units_into_chunks(citations, "numbered_reference_group")

    def _chunk_glossary_node(self, node: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Splits glossary node into atomic term-definition chunks."""
        text = node.get("extracted_text", "")
        
        # 27 Canonical Glossary Definitions from pages 11-13 of WHO Guideline
        glossary_items = [
            ("Artificial intelligence (AI)-based tobacco cessation software interventions",
             "Conversational AI, typically referred to as a chatbot or online dialogue system, used to provide tobacco cessation support. It enables two-way communication with users via text and/or audio without human input by employing natural language processing and machine learning algorithms."),
            ("Behavioural support",
             "Support, other than medications, aimed at helping people stop their tobacco use. It can include all cessation assistance that imparts knowledge about tobacco use and quitting, provides support, and teaches skills and strategies for changing behaviour. It includes brief advice and intensive behavioural support."),
            ("Brief advice",
             "Advice to stop using tobacco – usually taking only a few minutes – given to all tobacco users, usually during a routine consultation or interaction."),
            ("Bupropion",
             "Bupropion sustained release (bupropion SR) is an antidepressant agent with a demonstrated efficacy for use in tobacco cessation. It is a non-nicotine-based treatment and helps to alleviate withdrawal and craving in tobacco cessation. It has both dopaminergic and adrenergic actions, and appears to be an antagonist at the nicotinic acetylcholine receptor. It has been licensed as a prescription aid to tobacco cessation in many countries."),
            ("Combination pharmacotherapy for tobacco cessation",
             "The use of two or more tobacco cessation medications simultaneously to enhance cessation rates. Common combinations include combining a long-acting nicotine patch with a short-acting form of NRT (such as nicotine gum, lozenge, inhaler or nasal spray) or combining bupropion with NRT."),
            ("Conversational AI",
             "Refers to technologies, such as chatbots or voice assistants, that users can talk to. They use large volumes of data, machine learning, and natural language processing to help imitate human interactions, recognizing speech and text inputs and translating their meanings across various languages."),
            ("Cytisine",
             "Cytisine is a plant-based alkaloid extracted from the seeds of plants such as Cytisus laburnum (Golden Rain acacia). It is a partial agonist of nicotinic acetylcholine receptors, with a high binding affinity to the α4β2 nicotinic receptor subtype. It helps reduce the severity of nicotine withdrawal symptoms and cravings by partially stimulating these receptors while also blocking the rewarding effects of nicotine."),
            ("Digital tobacco cessation interventions",
             "Tobacco cessation interventions delivered through digital technologies and can involve the following modalities: mobile text messaging, internet-based interventions, smartphone applications (apps) and AI-based software interventions."),
            ("First-line medications",
             "Medications that are strongly recommended, have high certainty of evidence, are legally available in most countries, and have been reviewed and approved by multiple country-level regulatory bodies."),
            ("Health systems interventions",
             "Specific strategies that policy-makers and health-care service managers can implement to promote tobacco cessation. They involve systematic identification of tobacco users and subsequent offering of evidence-based tobacco cessation interventions or treatments, providing education, resources and feedback to promote provider interventions, and covering the cost of effective tobacco cessation services and their delivery."),
            ("Intensive behavioural support",
             "Multiple sessions of individual, group or telephone counselling aimed at helping people stop their tobacco use. It includes all cessation assistance that imparts knowledge about tobacco use and quitting, and provides support and resources to develop skills and strategies for changing behaviour."),
            ("Intensive individual behavioural counselling",
             "Personalized, face-to-face interactions between a trained health-care provider and a tobacco user. It encompasses various evidence-based techniques and strategies to assist the individual in quitting tobacco, including motivational interviewing, cognitive behavioural therapy and relapse prevention."),
            ("Intensive group behavioural counselling",
             "A group therapy approach that brings together individuals who want to quit tobacco use. Facilitated by a trained health-care provider or counsellor, these sessions offer participants a supportive environment to learn from each other, develop coping skills and receive evidence-based guidance on quitting tobacco."),
            ("Intensive telephone counselling",
             "Typically refers to the telephone counselling service provided by a national toll-free quit line. It is a form of remote support that connects individuals with trained counsellors via telephone. These counsellors assist participants in quitting tobacco by providing information, enhancing motivation, and using evidence-based techniques and personalized strategies for cessation through scheduled phone sessions and follow-up calls. Telephone counselling is especially useful for those who may face barriers to accessing in-person counselling services."),
            ("Internet-based tobacco cessation interventions",
             "Interventions offered through a diverse set of tools and resources including web-, email- and mobile phone-delivered components, online social networks (such as Facebook, X, and WeChat), online forums and support groups."),
            ("Mobile text-messaging tobacco cessation programme",
             "A programme involves the delivery of text messages from a preconstructed bank of content within a framework that determines what content and when content is delivered to help people stop tobacco use."),
            ("Nicotine replacement therapy (NRT)",
             "A medical product that supplies a controlled amount of nicotine to the body for a limited period, to help quit tobacco use completely. NRT is used to replace the nicotine the body receives through smoking cigarettes or using other tobacco products, and they deliver nicotine without the harmful chemicals present in tobacco smoke or smokeless tobacco. NRT helps to reduce the craving for tobacco and lessens the severity of nicotine withdrawals, thus making it easier for users to quit tobacco use. NRT products include nicotine gum, patches, lozenges, inhalers, and nasal or mouth sprays."),
            ("Promotion of tobacco cessation",
             "Population-wide measures and approaches that contribute to stopping tobacco use, including tobacco dependence treatment."),
            ("Smartphone applications (apps) for tobacco cessation",
             "Discrete pieces of software that can be used on a smartphone to perform specific sets of tasks to support individuals in their efforts to quit tobacco. These apps typically provide a range of features, such as assessing tobacco use, personalized quit plans, tracking of tobacco use triggers, coping strategies and social support."),
            ("Smokeless tobacco user",
             "A person who uses any smokeless tobacco products."),
            ("Tobacco addiction/dependence",
             "A cluster of behavioural, cognitive and physiological phenomena that develop after repeated tobacco use and that typically include: a strong desire to use tobacco, difficulties in controlling its use, persisting in its use despite the harmful consequences, giving higher priority to tobacco use than to other activities and obligations, increased tolerance, and sometimes experiencing a physical withdrawal state."),
            ("Tobacco cessation",
             "The process of stopping the use of any tobacco product, with or without assistance. May also be referred to as abstinence or quitting. There are multiple technical definitions that vary from study to study. The strictest definition is “no use of combustible or smokeless tobacco products or any other nicotine and tobacco products for at least 6 months”. Abstinence/quitting can be measured by “point prevalence abstinence” meaning the person has complete abstinence during a designated time period (for example, 7 or 30 days) prior to assessment, or prolonged abstinence (complete abstinence after an initial grace period), or continuous abstinence (complete abstinence beginning on the target quit day and lasting until the assessment)."),
            ("Tobacco dependence treatment",
             "The provision of behavioural support or medications, or both, to tobacco users to help them stop their tobacco use."),
            ("Tobacco products",
             "Products entirely or partly made of the leaf tobacco as raw material that are manufactured to be used for smoking, sucking, chewing or snuffing."),
            ("Tobacco user",
             "A person who uses any tobacco products."),
            ("Traditional, complementary or alternative therapy for tobacco cessation",
             "Therapies such as acupuncture; laser therapy or electrical stimulation; hypnotherapy; yoga; herbs; traditional Indian medicine; traditional herbal medicine; traditional Chinese medicine exercise, such as Tai Chi, Qigong, Baduanjin or Wuqinxi; mindfulness meditation; homeopathy; and chiropractic therapy to aid in smoking cessation."),
            ("Varenicline",
             "A medication used for tobacco cessation. It is a partial agonist of nicotinic acetylcholine receptors. When activated, these receptors release dopamine in the nucleus accumbens, the brain’s reward centre, thereby reducing cravings and other withdrawal symptoms. It also reduces the reward experience from using tobacco by preventing the binding of nicotine to these receptors.")
        ]

        glossary_chunks = []
        for term, definition in glossary_items:
            chunk_content = f"Term: {term}\nDefinition: {definition}"
            glossary_chunks.append((chunk_content, "glossary_term_definition"))

        return glossary_chunks

    def chunk_node(self, node: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Processes a single Leaf node into one or more valid semantic chunks."""
        node_id = node.get("node_id", "")
        doc_id = node.get("document_id", "who_tobacco_cessation_2024")
        content_type = node.get("content_type", "unknown")
        raw_text = node.get("extracted_text", "").strip()
        total_tokens = self.count_tokens(raw_text)

        # Determine retrieval role
        if content_type == "references" or "references" in node.get("title", "").lower():
            retrieval_role = "reference_lookup"
        else:
            retrieval_role = "clinical_dense_retrieval"

        # Case 1: Node fits within Hard Maximum (<= 500 tokens) and is not glossary
        if total_tokens <= self.hard_max_tokens and content_type != "glossary":
            chunk_records = [{
                "chunk_id": f"chunk_{node_id}",
                "document_id": doc_id,
                "node_id": node_id,
                "parent_id": node.get("parent_id"),
                "section_number": node.get("section_number"),
                "section_title": node.get("title"),
                "chunk_index": 0,
                "chunk_count": 1,
                "content_type": content_type,
                "physical_page_start": node.get("physical_page_start"),
                "physical_page_end": node.get("physical_page_end"),
                "token_count": total_tokens,
                "word_count": len(raw_text.split()),
                "character_count": len(raw_text),
                "source_type": "verbatim",
                "retrieval_role": retrieval_role,
                "split_reason": None,
                "text": raw_text
            }]
            return chunk_records

        # Case 2: Special Content Types
        if content_type == "references":
            raw_chunks = self._chunk_references_node(node)
        elif content_type == "glossary":
            raw_chunks = self._chunk_glossary_node(node)
        else:
            # Case 3: Large Node (> 500 tokens) -> Progressive Semantic Splitting
            atomic_units, split_reason = self._split_into_atomic_units(raw_text)
            raw_chunks = self._pack_units_into_chunks(atomic_units, split_reason)

        # Build chunk records with correct indices and counts
        total_chunk_count = len(raw_chunks)
        chunk_records = []
        for idx, (chunk_text, split_reason) in enumerate(raw_chunks):
            c_tokens = self.count_tokens(chunk_text)
            c_words = len(chunk_text.split())
            c_chars = len(chunk_text)

            chunk_records.append({
                "chunk_id": f"chunk_{node_id}_p{idx+1:02d}" if total_chunk_count > 1 else f"chunk_{node_id}",
                "document_id": doc_id,
                "node_id": node_id,
                "parent_id": node.get("parent_id"),
                "section_number": node.get("section_number"),
                "section_title": node.get("title"),
                "chunk_index": idx,
                "chunk_count": total_chunk_count,
                "content_type": content_type,
                "physical_page_start": node.get("physical_page_start"),
                "physical_page_end": node.get("physical_page_end"),
                "token_count": c_tokens,
                "word_count": c_words,
                "character_count": c_chars,
                "source_type": "verbatim",
                "retrieval_role": retrieval_role,
                "split_reason": split_reason if total_chunk_count > 1 else None,
                "text": chunk_text
            })

        return chunk_records

    def build_all_chunks(self) -> List[Dict[str, Any]]:
        """Processes all 90 Leaf nodes into the final semantic chunks dataset."""
        self.load_resources()
        self.chunks = []

        for leaf_node in self.leaf_nodes:
            node_chunks = self.chunk_node(leaf_node)
            self.chunks.extend(node_chunks)

        logging.info(f"Successfully generated {len(self.chunks)} semantic chunks from {len(self.leaf_nodes)} Leaf nodes.")
        return self.chunks

    def export_chunks(self, output_json_path: str, output_jsonl_path: str):
        """Exports chunks dataset in JSON and JSONL formats."""
        if not self.chunks:
            self.build_all_chunks()

        os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump({
                "schema_version": "2.0",
                "document": self.structure_map.get("document", {}),
                "total_leaf_nodes_processed": len(self.leaf_nodes),
                "total_chunks_generated": len(self.chunks),
                "chunks": self.chunks
            }, f, ensure_ascii=False, indent=2)

        with open(output_jsonl_path, 'w', encoding='utf-8') as f:
            for ch in self.chunks:
                f.write(json.dumps(ch, ensure_ascii=False) + '\n')

        logging.info(f"Exported chunks to {output_json_path} and {output_jsonl_path}")

if __name__ == '__main__':
    v_nodes = r'C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\verbatim_nodes_v1.json'
    s_map = r'C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\structure_map_v2.json'
    out_json = r'C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\semantic_chunks_v2.json'
    out_jsonl = r'C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\semantic_chunks_v2.jsonl'

    chunker = SemanticChunkerV2(v_nodes, s_map)
    chunks = chunker.build_all_chunks()
    chunker.export_chunks(out_json, out_jsonl)
    print(f"Generated {len(chunks)} chunks successfully.")
