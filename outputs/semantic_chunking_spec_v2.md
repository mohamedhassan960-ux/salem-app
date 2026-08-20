# Semantic Chunking Specification v2
## Architecture, Boundaries & Policy for Medical RAG

**Document:** WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (WHO, 2024) & Future Medical Literature  
**Schema Version:** `2.0 (Document-Agnostic & Leaf-First)`  
**Status:** `FINAL APPROVED SPECIFICATION`  
**Input Source:** `outputs/verbatim_nodes_v1.json` (Derived from `outputs/structure_map_v2.json` and `data/who_extracted.txt`)  

---

## 1. Architecture Goal

The primary objective of **Semantic Chunking Specification v2** is to transform the verified, 100% verbatim text of the 90 Leaf Nodes into optimal, self-contained semantic retrieval units (Chunks) for dense vector search and LLM context synthesis.

### Key Tenets:
1. **Medical Fidelity & Zero Hallucination:** No summarization, no paraphrasing, no deletion of qualifiers, dosages, or contraindications.
2. **Context Completeness:** Every clinical recommendation, evidence statement, and statistical finding ($RR$, $95\% CI$, $p$-value) must remain intact within its chunk.
3. **Leaf-First Indexing (No Duplication):** Vector indexing is applied exclusively to Leaf Nodes. Parent/Branch nodes are used for hierarchical context expansion on demand.
4. **Document-Agnostic Engine:** The chunker relies entirely on metadata, structural types, and paragraph boundaries, making it instantly applicable to Guidelines, Research Papers (IMRAD), and Systematic Reviews.
5. **Rebuildability & Provenance:** Chunks can be regenerated with different target sizes without re-extracting from PDF or modifying the underlying verbatim layer.

---

## 2. Input Contract

The chunker consumes `outputs/verbatim_nodes_v1.json` which adheres to the following contract:

```json
{
  "schema_version": "1.0",
  "document": {
    "document_id": "who_tobacco_cessation_2024",
    "title": "WHO clinical treatment guideline for tobacco cessation in adults",
    "document_type": "clinical_guideline",
    "publisher": "World Health Organization",
    "publication_year": 2024,
    "language": "en"
  },
  "source": {
    "file_type": "pdf",
    "file_name": "الاقلاع عن التدخبن.pdf",
    "total_physical_pages": 76
  },
  "nodes": [
    {
      "node_id": "sec_3_1_3",
      "parent_id": "sec_3_1",
      "level": 3,
      "section_number": "3.1.3",
      "title": "3.1.3. Justification and evidence",
      "physical_page_start": 29,
      "physical_page_end": 31,
      "printed_page_start": 11,
      "printed_page_end": 13,
      "content_type": "evidence",
      "extracted_text": "...",
      "word_count": 1383,
      "character_count": 9758,
      "extraction_status": "SUCCESS"
    }
  ]
}
```

---

## 3. Output Contract

The chunker will produce `outputs/semantic_chunks_v2.json` and `outputs/semantic_chunks_v2.jsonl`. Each chunk record adheres to this schema:

```json
{
  "chunk_id": "chunk_sec_3_1_3_p01",
  "document_id": "who_tobacco_cessation_2024",
  "node_id": "sec_3_1_3",
  "parent_node_id": "sec_3_1",
  "chunk_index": 1,
  "total_chunks_in_node": 3,
  "chunk_type": "evidence_justification",
  "content_type": "evidence",
  "section_number": "3.1.3",
  "heading_path": "3. Recommendations > 3.1 Behavioural support > 3.1.3 Justification and evidence",
  "breadcrumb_text": "[WHO 2024 Guideline | 3.1.3 Justification and evidence | Pages 11-13]",
  "physical_page_start": 29,
  "physical_page_end": 30,
  "printed_page_start": 11,
  "printed_page_end": 12,
  "recommendation_id": "REC_01",
  "recommendation_strength": "Strong",
  "certainty_of_evidence": "Moderate",
  "target_intervention": "Brief advice (30s to 3min)",
  "target_population": "All tobacco users accessing health-care settings",
  "parent_chunk_id": null,
  "related_chunk_ids": ["chunk_rec_01_brief_advice", "chunk_sec_3_1_2_questions"],
  "content": "...",
  "searchable_text": "[WHO 2024 Guideline | 3.1.3 Justification and evidence | Pages 11-13]\n...",
  "token_count": 542,
  "word_count": 348,
  "character_count": 2480,
  "is_leaf": true,
  "is_splittable": true
}
```

---

## 4. Leaf Node Policy (Leaf-First Indexing)

1. **Vector Indexing Eligibility:** Only **Leaf Nodes** (nodes with no children) are converted into searchable chunks.
2. **Branch / Parent Nodes:** Branch nodes (e.g. `sec_3`, `sec_3_1`, `sec_3_3`) are **never indexed as independent text chunks**. Their metadata and structural titles are embedded as `heading_path` and `parent_node_id` within leaf chunks.
3. **Double Counting Prevention:** Eliminates 100% of duplicate embeddings between parent chapters and child subsections.

---

## 5. Target Chunk Size Analysis & Selection

Based on the empirical findings of the **Token Distribution Audit** (Median = 248 tokens, P75 = 616 tokens, P90 = 1,132 tokens across 90 leaf nodes):

| Candidate Range | Pros | Cons | Verdict for Medical RAG |
| :---: | :--- | :--- | :---: |
| **200 – 400 tokens** | Highly granular retrieval | Fragments multi-paragraph trial analyses and GRADE evidence summaries | Too small for evidence justification |
| **400 – 700 tokens** | **Optimal balance:** Captures complete Cochrane review syntheses, GRADE explanations, and drug dosage tables intact | Requires paragraph splitting on only ~15% of nodes | **RECOMMENDED (Primary Target)** |
| **700 – 900 tokens** | Minimizes splitting count | Broad context may dilute vector cosine similarity for specific clinical questions | Acceptable for complex tables |
| **> 1,000 tokens** | Zero splitting required for 90% of nodes | Crosses single-passage retrieval limits; wastes LLM context window | Rejected as default |

### **Selected Target Range:**
* **Standard Target Size:** **350 – 650 tokens**
* **Ideal Sweet Spot:** **~500 tokens**

---

## 6. Hard Maximum Token Ceiling

* **Hard Maximum:** **1,000 tokens**
* **Exception Rule (Atomic Tables/Glossaries):** Up to **1,200 tokens** only if an individual structured GRADE table cannot be split without destroying column headers.
* Any leaf node $> 1,000$ tokens **MUST** undergo semantic paragraph splitting.

---

## 7. Overlap Policy

1. **Default Rule:** **Zero Overlap** for atomic nodes ($\le 750$ tokens), recommendations, tables, and glossaries.
2. **Splitting Overlap:** When a large continuous narrative or evidence section ($> 1,000$ tokens) is divided into 2 or more chunks:
   * **Overlap Size:** **50 – 100 tokens** (or exactly **1 leading sentence** of context).
   * **Rationale:** Preserves pronoun referents and statistical context across chunk boundaries without generating redundant text.
3. **Heading Context Injection:** Every chunk prepends a 1-line structured breadcrumb header (e.g. `[WHO 2024 | 3.3.3.1 NRT | Pages 17-18]`) which serves as deterministic context without needing token overlap.

---

## 8. Paragraph Splitting Rules

When a Leaf Node exceeds 750 tokens, it is segmented according to the following strict hierarchy:
1. **Primary Boundary:** Double newline (`\n\n`) representing natural section paragraphs.
2. **Secondary Boundary:** Single newline with bullet point or numbered item (`\n•`, `\n-`, `\n1.`, `\n2.`).
3. **Statistical Preservation Rule (Crucial):** Never split across lines containing relative risk brackets (e.g. `RR: 1.55; 95% CI: 1.49–1.61; 133 studies; 64 640 participants`). The full trial description and its statistical payload must stay in the same chunk.
4. **Sentence Safety Rule:** Splitting mid-sentence (`.` followed by capital letter) is strictly prohibited unless an indivisible single paragraph exceeds the Hard Max (1,000 tokens).

---

## 9. Recommendation Policy (REC Nodes)

1. **Indivisibility:** Every canonical recommendation statement (e.g. `REC_01` to `REC_12`) is stored as a **single, standalone atomic chunk**.
2. **Mandatory Co-located Fields:**
   * Exact recommendation statement text.
   * Strength of recommendation (`Strong` / `Conditional` / `Statement`).
   * Certainty of evidence (`High`, `Moderate`, `Low`, `Very low`).
   * Target population and target intervention.
3. **Chunk Type:** `chunk_type: "recommendation"`.

---

## 10. Evidence & Justification Policy (EVD Nodes)

1. **Topical Partitioning:** Evidence sections spanning multiple drugs or modalities (e.g. `sec_3_3_3` covering NRT, Bupropion, Varenicline, Cytisine, and Combinations) are split by **intervention topic** (`3.3.3.1`, `3.3.3.2`, etc.).
2. **GRADE Profiles:** Meta-analytic findings, risk ratios, confidence intervals, and certainty ratings are packaged as coherent evidence units.
3. **Chunk Type:** `chunk_type: "evidence_justification"`.

---

## 11. Glossary Policy (GLOSSARY Nodes)

1. **Atomic Term Extraction:** The Glossary section (`node_L1_glossary_of_terms` - 1,792 tokens) is partitioned into **27 distinct individual chunks** (1 chunk per term).
2. **Structure:**
   ```text
   Term: Varenicline
   Definition: A medication used for tobacco cessation. It is a partial agonist of nicotinic acetylcholine receptors...
   ```
3. **Chunk Type:** `chunk_type: "glossary_definition"`.

---

## 12. Structured Table Policy (TABLE Nodes)

1. **Markdown Table Integrity:** Tables (such as GRADE Table 1 and Table 2) are represented in standard GitHub-Flavored Markdown table syntax.
2. **Header Retention:** If a large multi-page table requires partitioning, every child chunk repeats the table header row.
3. **Chunk Type:** `chunk_type: "structured_table"`.

---

## 13. List Policy (LIST Nodes)

1. **Lead-in Context:** Lists (e.g. 5As/5Rs components, implementation bullet points) must never be detached from their introductory lead-in sentence.
2. **Atomic Listing:** If a list contains $\le 10$ items and $< 600$ tokens, keep all items together in a single chunk.

---

## 14. References Policy (REF Nodes)

1. **Clinical Vector Exclusion:** The References section (`node_L1_references` - 4,311 tokens) is **excluded from clinical QA semantic embeddings** to prevent citation noise from polluting medical symptom/treatment queries.
2. **Provenance Storage:** References are chunked into 5 page-level bibliographic blocks (`chunk_type: "reference_bibliography"`) and stored in metadata for citation lookup on demand.

---

## 15. Parent Context Strategy (Context Expansion)

To provide LLMs with complete chapter context during multi-hop answering:
1. Every chunk stores `parent_node_id` and `heading_path`.
2. The retrieval layer implements **Parent Context Expansion**: When a child leaf chunk is retrieved with high relevance, the system can fetch sibling chunks sharing the same `parent_node_id` to reconstruct the complete section context without needing duplicate parent embeddings.

---

## 16. Complete Metadata Schema

Every generated chunk must include:

| Field Name | Type | Description | Example |
| :--- | :---: | :--- | :--- |
| `chunk_id` | `str` | Unique deterministic identifier | `"chunk_rec_01_brief_advice"` |
| `document_id` | `str` | Unique document identifier | `"who_tobacco_cessation_2024"` |
| `node_id` | `str` | Reference to Structure Map Node | `"sec_3_1_1"` |
| `parent_node_id` | `str` | Parent Section Identifier | `"sec_3_1"` |
| `chunk_index` | `int` | Sequential chunk index within node | `1` |
| `total_chunks_in_node` | `int` | Total chunks resulting from this node | `1` |
| `chunk_type` | `str` | Functional taxonomy | `"recommendation"` |
| `content_type` | `str` | Medical content classification | `"recommendation"` |
| `section_number` | `str` | Canonical section number | `"3.1.1"` |
| `heading_path` | `str` | Full hierarchical breadcrumb path | `"3. Recommendations > 3.1 > 3.1.1"` |
| `breadcrumb_text` | `str` | Short provenance header | `"[WHO 2024 | 3.1.1 Recommendations | Page 11]"` |
| `physical_page_start` | `int` | PDF Physical Start Page | `29` |
| `physical_page_end` | `int` | PDF Physical End Page | `29` |
| `printed_page_start` | `int` | Printed Document Start Page | `11` |
| `printed_page_end` | `int` | Printed Document End Page | `11` |
| `recommendation_id` | `str` | Canonical Recommendation ID | `"REC_01"` |
| `recommendation_strength` | `str` | GRADE Recommendation Strength | `"Strong"` |
| `certainty_of_evidence` | `str` | GRADE Certainty of Evidence | `"Moderate"` |
| `target_intervention` | `str` | Clinical Intervention | `"Brief advice (30s to 3min)"` |
| `target_population` | `str` | Clinical Population | `"All tobacco users in health-care settings"` |
| `related_chunk_ids` | `list[str]`| Graph links to related chunks | `["chunk_sec_3_1_3_p01"]` |
| `content` | `str` | Pure verbatim text of chunk | `"..."` |
| `searchable_text` | `str` | Breadcrumb + Pure content | `"[WHO 2024 | 3.1.1] ..."` |
| `token_count` | `int` | Exact tokens (`cl100k_base`) | `142` |
| `word_count` | `int` | Exact words count | `94` |
| `character_count` | `int` | Exact character count | `729` |

---

## 17. Provenance & Traceability Strategy

```text
Document: WHO Guideline 2024
   └── Node: sec_3_1_3 (3.1.3 Justification and evidence)
         └── Physical Pages: 29–31 (Printed Pages: 11–13)
               └── Chunk: chunk_sec_3_1_3_p01 (Tokens: 542)
```
Every answer generated by the Medical RAG will cite the exact **Printed Page**, **Section Number**, and **Heading Path** directly from the chunk metadata.

---

## 18. Future Document Compatibility (Document-Agnostic Engine)

The chunking algorithm will operate on any medical document satisfying `structure_map_v2.json`:
* **Original Research Articles (IMRAD):** Methods, Results tables, and Discussion paragraphs will be split using the identical paragraph rules.
* **Systematic Reviews:** Search criteria, study characteristics tables, and meta-analysis summaries will be cleanly mapped to `evidence_justification` and `structured_table` chunk types.

---

## 19. Validation & Acceptance Criteria

Before approving the generated chunks:
1. **Word & Token Conservation:** Total words across all chunks must equal the verbatim leaf text ($\ge 99.5\%$ after running header stripping).
2. **Zero Dropped Statistics:** Every occurrence of $RR$, $CI$, and $p$-values in `verbatim_nodes_v1.json` must exist verbatim in the chunk dataset.
3. **Hard Max Compliance:** $100\%$ of chunks must be $\le 1,000$ tokens (or $\le 1,200$ for tables).
4. **Referential Integrity:** $100\%$ of `related_chunk_ids` must resolve to valid existing chunk IDs.

---

## 20. Failure Handling

* If an indivisible medical paragraph exceeds 1,000 tokens without any double newline, split at the first sentence boundary (`. `) after 600 tokens while duplicating the section heading breadcrumb.
* If a table exceeds 1,200 tokens, split row-wise while injecting the Markdown table header into both chunks.

---

## 21. Concrete Example Transformations

### Example A: Recommendation Node (`sec_3_1_1` $\rightarrow$ 1 Atomic Chunk)
* **Input (Verbatim Node):** 94 words / 142 tokens.
* **Output Chunk (`chunk_rec_01_brief_advice`):**
  ```text
  [WHO 2024 Guideline | 3.1.1 Recommendations | REC_01 | Page 11]
  1. WHO recommends brief advice (between 30 seconds and 3 minutes per encounter) be consistently provided by health-care providers as a routine practice to all tobacco users accessing any health-care settings.
  Strong recommendation; moderate certainty.
  ```

### Example B: Large Evidence Node (`sec_3_1_3` $\rightarrow$ 3 Topic Chunks)
* **Input (Verbatim Node):** 1,383 words / 2,127 tokens (Pages 29–31).
* **Partitioning:**
  * **Chunk 1 (`chunk_sec_3_1_3_brief_advice`):** 480 tokens (Cochrane brief advice review, 24,352 participants, RR: 1.17).
  * **Chunk 2 (`chunk_sec_3_1_3_individual_group`):** 560 tokens (Individual vs group counselling, trial numbers, RR: 1.57 and RR: 1.88).
  * **Chunk 3 (`chunk_sec_3_1_3_telephone_quitline`):** 510 tokens (Quitline telephone counselling meta-analysis, 104 studies, RR: 1.25).

---

## FINAL CHUNKING DECISION

| Decision Parameter | Selected Specification Value |
| :--- | :--- |
| **Target Token Range** | **350 – 650 tokens** (Ideal Sweet Spot: **~500 tokens**) |
| **Hard Maximum Ceiling** | **1,000 tokens** (1,200 tokens for indivisible tables) |
| **Overlap Policy** | **0 tokens** for atomic chunks; **50–100 tokens** (1 sentence) only for split narrative evidence |
| **When to Split** | Any Leaf Node $> 750$ tokens with natural paragraph/topic boundaries |
| **When NOT to Split** | Any Node $\le 750$ tokens, recommendations, individual glossary terms, atomic tables |
| **Glossary Handling** | 27 individual atomic chunks (1 chunk per term) |
| **References Handling** | Excluded from dense clinical embeddings; preserved in provenance lookup store |
| **Duplicate Prevention** | Index Leaf nodes only; Parent nodes serve as hierarchy metadata |
