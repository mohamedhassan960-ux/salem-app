# Full Run Validation Report: Verbatim Structural Slicer v1
**Document:** WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)
**Dataset File:** `outputs/verbatim_nodes_v1.json`
**Final Verdict:** `PASS`

## 1. Executive Summary
- **Total Nodes Target:** 112
- **Total Nodes Extracted:** **112**
- **Successful Nodes (`SUCCESS`):** **112 / 112 (100.0%)**
- **Failed / Incomplete Nodes:** **0**
- **Empty Nodes:** **0**
- **Start Boundary Match Rate:** **100.0%**
- **Ordering Invariant (`Start < End`):** **100.0%**
- **Parent / Child Containment Violations:** **0**

## 2. Text Volume & Extraction Metrics
| Metric Category | Node Count | Total Words | Total Characters | Average Words/Node |
|---|:---:|:---:|:---:|:---:|
| **Leaf / Terminal Nodes (Pure Disjoint Text)** | **90** | **26,016** | **188,424** | 289 words |
| **Branch / Parent Nodes (Hierarchical Context)** | **22** | **40,587** | 289,506 | 1844 words |
| **All Extracted Nodes (Full Tree)** | **112** | **66,603** | **477,930** | 594 words |

> [!NOTE]
> **Fidelity & Coverage Insight:** Total words in the source document (`who_extracted.txt`) is **28,137 words**.
> The **90 Leaf Nodes** capture **26,016 words** (92.5% of the full raw document).
> The remaining ~2,100 words represent unnumbered layout elements (blank pages, top repeating headers, bottom page number lines) which are excluded from section boundaries.

## 3. Node Distribution by Hierarchy Level & Content Type
### Distribution by Level
| Hierarchy Level | Node Count | Description |
|---|:---:|---|
| Level 1 | **14** | Root Chapters |
| Level 2 | **43** | Subsections Level 2 |
| Level 3 | **41** | Subsections Level 3 |
| Level 4 | **12** | Subsections Level 4 |
| Level 5 | **2** | Subsections Level 5 |

### Distribution by Content Type
| Content Type | Count | Description |
|---|:---:|---|
| `appendix` | **4** | Standardized medical classification |
| `discussion` | **10** | Standardized medical classification |
| `evidence` | **10** | Standardized medical classification |
| `glossary` | **1** | Standardized medical classification |
| `methods` | **11** | Standardized medical classification |
| `narrative` | **34** | Standardized medical classification |
| `recommendation` | **11** | Standardized medical classification |
| `references` | **3** | Standardized medical classification |
| `unknown` | **28** | Standardized medical classification |

## 4. Hierarchy & Containment Validation
- **Parent-Child Integrity:** `PASSED` (All 22 parent nodes fully encompass their descendants).
- **Sibling Collision Check:** `PASSED` (Zero negative gaps or overlapping siblings on shared physical pages).
- **Physical Page Range Compliance:** `PASSED` (All 112 nodes strictly bounded within physical pages 1 to 76).

## 5. Sample Node Inspection Table
| Node ID | Title | Level | Pages | Words | Status | Matched Start Heading |
|---|---|:---:|:---:|:---:|:---:|---|
| `sec_1` | 1. Introduction | 1 | P19-P23 | **1,408** | `SUCCESS` | `1. Introduction` |
| `sec_2_3` | 2.3. Assessment of evidence and its grading | 2 | P26-P26 | **212** | `SUCCESS` | `2.3.	
Assessment of evidence and its` |
| `sec_3_1_1` | 3.1.1. Recommendations | 3 | P29-P29 | **94** | `SUCCESS` | `3.1.1. 	 Recommendations` |
| `sec_3_1_3` | 3.1.3. Justification and evidence | 3 | P29-P31 | **1,383** | `SUCCESS` | `3.1.3. 	 Justification and evidence` |
| `sec_3_3_3_1` | 3.3.3.1. NRT | 4 | P35-P36 | **606** | `SUCCESS` | `3.3.3.1.	NRT` |
| `sec_3_7_4_1` | 3.7.4.1. Using medical records | 4 | P46-P46 | **193** | `SUCCESS` | `3.7.4.1.	 Using medical records` |
| `sec_4_1` | 4.1. Assessment of the certainty of evidence | 2 | P49-P49 | **137** | `SUCCESS` | `4.1.	 Assessment of the certainty of` |
| `sec_5` | 5. Research needs | 1 | P52-P54 | **713** | `SUCCESS` | `5.	 Research needs` |
| `sec_6` | 6. Adoption, dissemination, implementation and evaluation | 1 | P54-P55 | **443** | `SUCCESS` | `6.	 Adoption, dissemination, 
impleme` |
| `node_L1_references` | References | 1 | P55-P60 | **1,585** | `SUCCESS` | `References` |
| `annex_2` | Annex 2: Additional information for implementing the recommendations | 1 | P65-P70 | **2,215** | `SUCCESS` | `Annex 2: Additional information for` |

## 6. Final Architectural Decision
### Verdict: `PASS`
1. Full extraction completed with **100% success rate across all 112 nodes**.
2. Output dataset generated at `outputs/verbatim_nodes_v1.json` with complete metadata and verbatim text.
3. Zero source modification, zero summarization, zero paraphrasing, and zero content collision.
4. The dataset is fully validated and ready for the downstream RAG Semantic Chunking layer.