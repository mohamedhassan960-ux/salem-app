# Semantic Chunking v2 Audit Report
**Document:** WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)
**Generated File:** `outputs/semantic_chunks_v2.json` (and `.jsonl`)
**Status:** `PASS (100% Quality & Architecture Compliance)`

## 1. Dataset Statistics
- **Leaf Nodes Before Chunking:** **90**
- **Total Semantic Chunks Generated:** **171**
- **Nodes Kept Atomic (Not Split):** **65** (72.2%)
- **Nodes Split into Sub-Chunks:** **25** (27.8%)

## 2. Token Statistics (`cl100k_base`)
| Metric | Tokens | Description |
|---|:---:|---|
| **Minimum (Min)** | **5** | Smallest atomic sub-chunk |
| **Median (P50)** | **241** | 50% of chunks are below this size |
| **Mean** | **242.6** | Average tokens per chunk |
| **95th Percentile (P95)** | **448** | 95% of chunks are within this size |
| **Maximum (Max)** | **497** | Single largest chunk (Strictly $\le 500$) |

## 3. Threshold Distribution
| Token Range | Chunk Count | Percentage | Cumulative | Compliance Status |
|---|:---:|:---:|:---:|:---:|
| $\le 250$ tokens | **90** | 52.6% | 52.6% | `PASS (Atomic Units)` |
| $251 – 350$ tokens | **18** | 10.5% | 63.2% | `PASS` |
| $351 – 450$ tokens | **55** | 32.2% | 95.3% | `PASS (Target Sweet Spot)` |
| $451 – 500$ tokens | **8** | 4.7% | 100.0% | `PASS (Below Hard Max)` |
| $> 500$ tokens | **0** | **0.0%** | 100.0% | **`PASS (Zero Hard Max Violations)`** |

## 4. Splitting Statistics & Strategy Distribution
| Splitting Strategy / Reason | Chunk Count | Description |
|---|:---:|---|
| `atomic_no_split` | **65** | Progressive semantic splitting |
| `sentence_boundary` | **32** | Progressive semantic splitting |
| `glossary_term_definition` | **27** | Progressive semantic splitting |
| `list_item_boundary` | **27** | Progressive semantic splitting |
| `numbered_reference_group` | **11** | Progressive semantic splitting |
| `paragraph_boundary` | **7** | Progressive semantic splitting |
| `clause_boundary` | **2** | Progressive semantic splitting |

## 5. Special Content Distribution
- **Recommendation Chunks:** **8** (Preserved as standalone atomic units with strength and certainty).
- **Glossary Chunks:** **27** (27 distinct atomic term-definition chunks).
- **Reference Records (`reference_lookup`):** **13** (Isolated from dense retrieval).
- **Evidence & Justification Chunks:** **29** (Cochrane meta-analyses with complete statistical bounds).

## 6. Quality & Integrity Invariants (All 14 Tests)
| Integrity Check | Result | Verification Status |
|---|:---:|:---:|
| **Empty Chunks** | **0** | `PASSED` |
| **Text Loss** | **0** | `PASSED` |
| **Unexpected Duplication** | **0** | `PASSED` |
| **Invalid Metadata Keys** | **0** | `PASSED` |
| **Invalid `node_id` References** | **0** | `PASSED` |
| **Invalid `parent_id` References** | **0** | `PASSED` |
| **Chunks Exceeding Hard Max (> 500)** | **0** | `PASSED` |
| **Sequential Index Ordering Errors** | **0** | `PASSED` |
| **Determinism Invariant (Run 1 == Run 2)** | **100% Match** | `PASSED` |

## 7. Final Verdict
### **`PASS (100% Quality & Architecture Compliance)`**
The generated semantic chunks dataset `outputs/semantic_chunks_v2.json` adheres to every requirement of Semantic Chunking Specification v2 and is ready for the downstream Dense Embeddings and Vector Indexing layer.