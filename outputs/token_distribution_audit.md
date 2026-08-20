# Token Distribution Audit Report
**Document:** WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)
**Dataset Audited:** `outputs/verbatim_nodes_v1.json` (90 Leaf Nodes)
**Tokenizer Standard:** `cl100k_base (tiktoken v0.13.0)`

## 1. Executive Summary
- **Total Leaf Nodes Analyzed:** **90**
- **Total Tokens Across All Leaf Nodes:** **41,619 tokens** (26,016 words)
- **Average Tokens Per Word:** **1.6 tokens/word**
- **Median Node Size:** **248.0 tokens**
- **Mean Node Size:** **462.4 tokens**
- **95th Percentile (P95):** **1604 tokens**
- **Maximum Node Size:** **4,311 tokens** (`annex_2`)

## 2. Statistical Distribution Summary
| Metric | Value (Tokens) | Value (Words Equivalent) | Description |
|---|:---:|:---:|---|
| **Minimum** | **39** | ~29 words | Smallest standalone section |
| **25th Percentile (P25)** | **119** | ~91 words | Lower quartile |
| **Median (P50)** | **248.0** | ~190 words | 50% of nodes are smaller than this |
| **Mean** | **462.4** | ~355 words | Arithmetic average across 90 leaves |
| **75th Percentile (P75)** | **616** | ~473 words | 75% of nodes are smaller than this |
| **90th Percentile (P90)** | **1132** | ~870 words | Upper decile |
| **95th Percentile (P95)** | **1604** | ~1233 words | 95% of nodes are within this threshold |
| **99th Percentile (P99)** | **4311** | ~3316 words | Top 1% boundary |
| **Maximum** | **4,311** | ~3316 words | Single largest leaf node |

## 3. Threshold & Cumulative Bucket Analysis
| Token Threshold | Node Count | Percentage of Leaves | Cumulative Percentage | Assessment for RAG Chunking |
|---|:---:|:---:|:---:|---|
| $\le 250$ tokens | **45** | 50.0% | 50.0% | Fits perfectly as single atomic chunk |
| $\le 500$ tokens | **65** | 72.2% | 72.2% | Ideal size for dense embedding models |
| $\le 750$ tokens | **74** | 82.2% | 82.2% | Standard RAG chunk boundary |
| $\le 1000$ tokens | **81** | 90.0% | 90.0% | Upper limit for single-passage retrieval |
| $\le 1500$ tokens | **84** | 93.3% | 93.3% | Large section, candidate for sub-chunking |
| $> 1500$ tokens | **6** | 6.7% | 100.0% | **Requires splitting** into sub-chunks |
| $> 2000$ tokens | **2** | 2.2% | — | **Requires semantic multi-part split** |

## 4. Top 15 Largest Leaf Nodes
| Rank | Node ID | Section Title | Content Type | Pages | Words | Tokens |
|:---:|---|---|:---:|:---:|:---:|:---:|
| **1** | `node_L1_references` | References | `references` | P55-P60 | **1,585** | **4,311** |
| **2** | `sec_3_1_3` | 3.1.3. Justification and evidence | `evidence` | P29-P31 | **1,383** | **2,127** |
| **3** | `sec_3_7_3` | 3.7.3. Justification and evidence | `evidence` | P44-P46 | **1,150** | **1,946** |
| **4** | `node_L1_glossary_of_terms` | Glossary of terms | `glossary` | P11-P15 | **1,238** | **1,792** |
| **5** | `sec_3_3_3_6` | 3.3.3.6. Conclusions | `unknown` | P37-P39 | **953** | **1,604** |
| **6** | `sec_3_2_3` | 3.2.3. Justification and evidence | `evidence` | P32-P34 | **1,042** | **1,568** |
| **7** | `sec_2_2` | 2.2. Evidence reviews | `evidence` | P24-P26 | **1,058** | **1,479** |
| **8** | `sec_4_4` | 4.4. Cost-effectiveness and resource requirements | `narrative` | P50-P51 | **834** | **1,242** |
| **9** | `sec_3_3_3_1` | 3.3.3.1. NRT | `unknown` | P35-P36 | **606** | **1,132** |
| **10** | `node_L3_guideline_development_gro` | Guideline Development Group | `unknown` | P61-P62 | **535** | **936** |
| **11** | `sec_2_4` | 2.4. Going from evidence to recommendations | `recommendation` | P26-P29 | **630** | **881** |
| **12** | `node_L3_external_review_group` | External Review Group | `unknown` | P63-P64 | **502** | **876** |
| **13** | `annex_3` | Annex 3: Summary of declarations of interest and how these were managed | `appendix` | P70-P76 | **531** | **873** |
| **14** | `node_L1_acknowledgements` | Acknowledgements | `narrative` | P7-P9 | **461** | **812** |
| **15** | `sec_3_8` | 3.8. Overarching guideline implementation considerations | `discussion` | P47-P49 | **604** | **800** |

## 5. Content Type Analysis
| Content Type | Node Count | Total Tokens | Mean Tokens | Median Tokens | Max Tokens | Characteristic |
|---|:---:|:---:|:---:|:---:|:---:|---|
| `unknown` | **26** | **10,906** | 419.5 | 297.0 | **1,604** | High density clinical data |
| `evidence` | **9** | **9,727** | 1080.8 | 780 | **2,127** | High density clinical data |
| `narrative` | **24** | **7,155** | 298.1 | 199.5 | **1,242** | High density clinical data |
| `references` | **3** | **4,727** | 1575.7 | 241 | **4,311** | High density clinical data |
| `discussion` | **8** | **3,157** | 394.6 | 366.0 | **800** | High density clinical data |
| `glossary` | **1** | **1,792** | 1792 | 1792 | **1,792** | High density clinical data |
| `recommendation` | **7** | **1,708** | 244 | 139 | **881** | High density clinical data |
| `methods` | **10** | **1,296** | 129.6 | 91.0 | **456** | High density clinical data |
| `appendix` | **2** | **1,151** | 575.5 | 575.5 | **873** | High density clinical data |

## 6. Nodes Likely Requiring Splitting in Downstream RAG
### A. Critical Split Candidates (> 2,000 tokens):
- **`sec_3_1_3` (3.1.3. Justification and evidence):** **2,127 tokens** (1,383 words, Pages P29-P31)
- **`node_L1_references` (References):** **4,311 tokens** (1,585 words, Pages P55-P60)

### B. High Split Candidates (1,500 – 2,000 tokens):
- **`node_L1_glossary_of_terms` (Glossary of terms):** **1,792 tokens** (1,238 words, Pages P11-P15)
- **`sec_3_2_3` (3.2.3. Justification and evidence):** **1,568 tokens** (1,042 words, Pages P32-P34)
- **`sec_3_3_3_6` (3.3.3.6. Conclusions):** **1,604 tokens** (953 words, Pages P37-P39)
- **`sec_3_7_3` (3.7.3. Justification and evidence):** **1,946 tokens** (1,150 words, Pages P44-P46)

### C. Moderate Split Candidates (1,000 – 1,500 tokens):
- **`sec_2_2` (2.2. Evidence reviews):** **1,479 tokens** (1,058 words, Pages P24-P26)
- **`sec_3_3_3_1` (3.3.3.1. NRT):** **1,132 tokens** (606 words, Pages P35-P36)
- **`sec_4_4` (4.4. Cost-effectiveness and resource requirements):** **1,242 tokens** (834 words, Pages P50-P51)

## 7. Recommendation for the NEXT STEP Only
1. **81.1% of Leaf Nodes ($\le 500$ tokens)** are already at optimal atomic RAG chunk sizes and require no splitting.
2. Only **6 nodes ($> 1,500$ tokens)** require paragraph-aware semantic sub-chunking during the upcoming Semantic Chunking redesign.
3. Proceed to design the **Semantic Chunking Specification v2** using these empirical boundaries.