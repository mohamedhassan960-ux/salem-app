# Realistic Retrieval Evaluation Report
## Oxygen Medical RAG — Production Retrieval Layer Benchmark

**Date:** 2026-08-19  
**Evaluation Type:** Diagnostic Retrieval-Only Evaluation (Phase 1)  
**Dataset:** `tests/core_rag_realistic_evaluation_dataset.json` (20 questions)  
**Corpus:** `outputs/retrieval_records_v2.json` (171 chunks)  
**Pipeline Components Evaluated:** HybridRetriever (Dense multilingual-e5-small + Sparse BM25) ➔ ClinicalReranker ➔ EvidenceQualityGate  
**Generation Tested:** NO (Evaluation frozen strictly at the retrieval/gating interface)

---

## 1. Executive Summary

| Metric | Result | Target Benchmark |
|---|:---:|:---:|
| **Total Questions** | **20** | 20 |
| **Supported Questions** | **18** | 18 |
| **Unsupported Questions** | **2** | 2 |
| **Hit@1** | **6 / 18 (33.3%)** | Diagnostic |
| **Hit@3** | **12 / 18 (66.7%)** | Diagnostic |
| **Hit@5** | **15 / 18 (83.3%)** | $\ge 80.0\%$ |
| **Mean Reciprocal Rank (MRR)** | **0.5204** | Diagnostic |
| **Full Multi-Chunk Retrieval @5** | **0 / 3 (0.0%)** | Diagnostic |
| **Pass / Partial / Miss (Supported)** | **PASS: 12 \| PARTIAL: 3 \| MISS: 3** | — |

---

## 2. Per-Question Results

| ID | Gold Chunk(s) | Top-1 Chunk ID | Hit@1 | Hit@3 | Hit@5 | RR | Full @5 | Status |
|---|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `real_01` | `chunk_sec_3_1_1` | `chunk_sec_3_2_3_p04` | 0 | 0 | 0 | 0.000 | — | **MISS** |
| `real_02` | `chunk_sec_3_3_1` | `chunk_sec_3_4_1` | 0 | 1 | 1 | 0.500 | — | **PASS** |
| `real_03` | `chunk_sec_3_7_1` | `chunk_sec_3_7_2` | 0 | 0 | 1 | 0.200 | — | **PASS** |
| `real_04` | `chunk_sec_3_6_1` | `chunk_sec_3_6_3_p02` | 0 | 1 | 1 | 0.333 | — | **PASS** |
| `real_05` | `chunk_sec_3_3_3_1_p01` | `chunk_sec_3_3_3_1_p01` | 1 | 1 | 1 | 1.000 | — | **PASS** |
| `real_06` | `chunk_sec_3_5_1` | `chunk_sec_3_3_1` | 0 | 0 | 0 | 0.000 | — | **MISS** |
| `real_07` | `chunk_sec_3_4_1` | `chunk_sec_3_4_3_p01` | 0 | 0 | 0 | 0.000 | — | **MISS** |
| `real_08` | `chunk_sec_3_2_1` | `chunk_sec_3_2_3_p02` | 0 | 1 | 1 | 0.500 | — | **PASS** |
| `real_09` | `chunk_sec_3_1_1` | `chunk_sec_3_1_1` | 1 | 1 | 1 | 1.000 | — | **PASS** |
| `real_10` | `chunk_node_L2_background` | `chunk_node_L2_background` | 1 | 1 | 1 | 1.000 | — | **PASS** |
| `real_11` | `chunk_sec_3_1_3_p04` | `chunk_sec_3_1_3_p01` | 0 | 1 | 1 | 0.500 | — | **PASS** |
| `real_12` | `chunk_sec_3_3_3_4` | `chunk_sec_3_3_3_4` | 1 | 1 | 1 | 1.000 | — | **PASS** |
| `real_13` | `chunk_sec_3_3_3_6_p01` | `chunk_sec_3_3_3_6_p01` | 1 | 1 | 1 | 1.000 | — | **PASS** |
| `real_14` | `chunk_sec_3_3_3_5`, `chunk_sec_3_3_3_6_p03` | `chunk_sec_3_3_1` | 0 | 0 | 1 | 0.250 | 0 | **PARTIAL** |
| `real_15` | `chunk_sec_3_3_3_4`, `chunk_sec_3_3_3_6_p03` | `chunk_sec_3_3_1` | 0 | 1 | 1 | 0.333 | 0 | **PARTIAL** |
| `real_16` | `chunk_sec_3_3_3_1_p02` | `chunk_sec_3_3_1` | 0 | 0 | 1 | 0.250 | — | **PASS** |
| `real_17` | `[]` *(Must Abstain)* | `chunk_sec_2_2_p04` | — | — | — | — | — | **UNSUPPORTED** |
| `real_18` | `[]` *(Must Abstain)* | `chunk_sec_1_1` | — | — | — | — | — | **UNSUPPORTED** |
| `real_19` | `chunk_sec_3_3_3_5`, `chunk_sec_3_3_3_6_p04` | `chunk_sec_3_3_1` | 0 | 1 | 1 | 0.500 | 0 | **PARTIAL** |
| `real_20` | `chunk_sec_3_2_3_p02` | `chunk_sec_3_2_3_p02` | 1 | 1 | 1 | 1.000 | — | **PASS** |

---

## 3. Detailed Retrieval Results

### `real_01`
- **Question:** How long should a standard brief tobacco cessation talk take during a clinical appointment?
- **Gold Chunk:** `chunk_sec_3_1_1`
- **Top 5 Retrieved:**
  1. `chunk_sec_3_2_3_p04` (score: 0.8714)
  2. `chunk_sec_3_2_3_p02` (score: 0.8690)
  3. `chunk_sec_3_2_1` (score: 0.8669)
  4. `chunk_sec_3_2_3_p03` (score: 0.8666)
  5. `chunk_sec_3_2_3_p01` (score: 0.8529)
- **Retrieved Gold Chunks:** None
- **Missing Gold Chunks:** `["chunk_sec_3_1_1"]`
- **Retrieval Status:** **MISS**

---

### `real_02`
- **Question:** Which medications are officially recommended by WHO as main pharmacological options for quitting smoking?
- **Gold Chunk:** `chunk_sec_3_3_1`
- **Top 5 Retrieved:**
  1. `chunk_sec_3_4_1` (score: 0.9368)
  2. `chunk_sec_3_3_1` (score: 0.9155) [GOLD]
  3. `chunk_sec_3_1_1` (score: 0.8907)
  4. `chunk_node_L3_interventions_for_smokele` (score: 0.8868)
  5. `chunk_node_L3_pharmacological_intervent` (score: 0.8843)
- **Retrieved Gold Chunks:** `["chunk_sec_3_3_1"]` (Rank 2)
- **Missing Gold Chunks:** None
- **Retrieval Status:** **PASS**

---

### `real_03`
- **Question:** What health system intervention is recommended regarding recording a patient's tobacco use in clinic records?
- **Gold Chunk:** `chunk_sec_3_7_1`
- **Top 5 Retrieved:**
  1. `chunk_sec_3_7_2` (score: 0.9014)
  2. `chunk_sec_3_7_4_1` (score: 0.8993)
  3. `chunk_node_L2_brief_advice` (score: 0.8737)
  4. `chunk_sec_3_7_4_2` (score: 0.8698)
  5. `chunk_sec_3_7_1` (score: 0.8623) [GOLD]
- **Retrieved Gold Chunks:** `["chunk_sec_3_7_1"]` (Rank 5)
- **Missing Gold Chunks:** None
- **Retrieval Status:** **PASS**

---

### `real_04`
- **Question:** What does the WHO guideline say about using alternative therapies like acupuncture or laser therapy to quit smoking?
- **Gold Chunk:** `chunk_sec_3_6_1`
- **Top 5 Retrieved:**
  1. `chunk_sec_3_6_3_p02` (score: 0.7339)
  2. `chunk_sec_3_6_3_p01` (score: 0.7337)
  3. `chunk_sec_3_6_1` (score: 0.6844) [GOLD]
  4. `chunk_sec_3_6_4` (score: 0.5489)
  5. `chunk_sec_2_2_p04` (score: 0.5457)
- **Retrieved Gold Chunks:** `["chunk_sec_3_6_1"]` (Rank 3)
- **Missing Gold Chunks:** None
- **Retrieval Status:** **PASS**

---

### `real_05`
- **Question:** How many studies and total participants formed the evidence base for single NRT monotherapy in the Cochrane review?
- **Gold Chunk:** `chunk_sec_3_3_3_1_p01`
- **Top 5 Retrieved:**
  1. `chunk_sec_3_3_3_1_p01` (score: 0.8601) [GOLD]
  2. `chunk_sec_3_3_3_1_p03` (score: 0.8394)
  3. `chunk_sec_3_3_3_5` (score: 0.8244)
  4. `chunk_node_L3_pharmacological_intervent` (score: 0.6698)
  5. `chunk_sec_3_7_3_p02` (score: 0.5765)
- **Retrieved Gold Chunks:** `["chunk_sec_3_3_3_1_p01"]` (Rank 1)
- **Missing Gold Chunks:** None
- **Retrieval Status:** **PASS**

---

### `real_06`
- **Question:** Is it more effective to use quit-smoking pills alongside talking therapy rather than trying pills alone?
- **Gold Chunk:** `chunk_sec_3_5_1`
- **Top 5 Retrieved:**
  1. `chunk_sec_3_3_1` (score: 0.8915)
  2. `chunk_sec_3_3_3_3_p01` (score: 0.8443)
  3. `chunk_sec_3_3_3_4` (score: 0.8339)
  4. `chunk_sec_3_3_3_6_p03` (score: 0.8287)
  5. `chunk_sec_3_3_3_6_p02` (score: 0.8264)
- **Retrieved Gold Chunks:** None
- **Missing Gold Chunks:** `["chunk_sec_3_5_1"]`
- **Retrieval Status:** **MISS**

---

### `real_07`
- **Question:** What support should doctors give to patients trying to stop chewing tobacco or using snuff?
- **Gold Chunk:** `chunk_sec_3_4_1`
- **Top 5 Retrieved:**
  1. `chunk_sec_3_4_3_p01` (score: 0.8567)
  2. `chunk_node_L3_general_p01` (score: 0.8454)
  3. `chunk_sec_3_4_3_p02` (score: 0.8367)
  4. `chunk_node_L2_financial_interventions` (score: 0.8089)
  5. `chunk_sec_3_5_4` (score: 0.8086)
- **Retrieved Gold Chunks:** None
- **Missing Gold Chunks:** `["chunk_sec_3_4_1"]`
- **Retrieval Status:** **MISS**

---

### `real_08`
- **Question:** Can mobile phone apps and automated texting tools replace standard medical care for smoking cessation?
- **Gold Chunk:** `chunk_sec_3_2_1`
- **Top 5 Retrieved:**
  1. `chunk_sec_3_2_3_p02` (score: 0.8911)
  2. `chunk_sec_3_2_1` (score: 0.8838) [GOLD]
  3. `chunk_sec_3_2_3_p01` (score: 0.8737)
  4. `chunk_sec_3_2_3_p03` (score: 0.8715)
  5. `chunk_sec_3_2_3_p04` (score: 0.8681)
- **Retrieved Gold Chunks:** `["chunk_sec_3_2_1"]` (Rank 2)
- **Missing Gold Chunks:** None
- **Retrieval Status:** **PASS**

---

### `real_09`
- **Question:** What non-drug counselling formats can a clinic offer to people who want to quit tobacco?
- **Gold Chunk:** `chunk_sec_3_1_1`
- **Top 5 Retrieved:**
  1. `chunk_sec_3_1_1` (score: 0.8962) [GOLD]
  2. `chunk_sec_3_1_3_p05` (score: 0.8647)
  3. `chunk_sec_3_1_3_p02` (score: 0.8576)
  4. `chunk_sec_3_1_3_p04` (score: 0.8537)
  5. `chunk_sec_3_1_3_p03` (score: 0.8514)
- **Retrieved Gold Chunks:** `["chunk_sec_3_1_1"]` (Rank 1)
- **Missing Gold Chunks:** None
- **Retrieval Status:** **PASS**

---

### `real_10`
- **Question:** What is the global death toll caused by tobacco products and how widespread is tobacco consumption worldwide?
- **Gold Chunk:** `chunk_node_L2_background`
- **Top 5 Retrieved:**
  1. `chunk_node_L2_background` (score: 0.8747) [GOLD]
  2. `chunk_sec_4_4_p03` (score: 0.8610)
  3. `chunk_sec_6_p02` (score: 0.8386)
  4. `chunk_sec_1_2_p02` (score: 0.8328)
  5. `chunk_node_L2_products` (score: 0.8323)
- **Retrieved Gold Chunks:** `["chunk_node_L2_background"]` (Rank 1)
- **Missing Gold Chunks:** None
- **Retrieval Status:** **PASS**

---

### `real_11`
- **Question:** How many patients need to receive brief clinical advice from a doctor for one additional person to successfully quit?
- **Gold Chunk:** `chunk_sec_3_1_3_p04`
- **Top 5 Retrieved:**
  1. `chunk_sec_3_1_3_p01` (score: 0.8981)
  2. `chunk_sec_3_1_3_p04` (score: 0.8897) [GOLD]
  3. `chunk_sec_3_5_3_p02` (score: 0.8796)
  4. `chunk_sec_3_1_4` (score: 0.8722)
  5. `chunk_sec_3_7_3_p01` (score: 0.8607)
- **Retrieved Gold Chunks:** `["chunk_sec_3_1_3_p04"]` (Rank 2)
- **Missing Gold Chunks:** None
- **Retrieval Status:** **PASS**

---

### `real_12`
- **Question:** How much does cytisine increase the likelihood of quitting smoking compared with placebo in clinical trials?
- **Gold Chunk:** `chunk_sec_3_3_3_4`
- **Top 5 Retrieved:**
  1. `chunk_sec_3_3_3_4` (score: 0.8618) [GOLD]
  2. `chunk_sec_2_4_p02` (score: 0.7130)
  3. `chunk_sec_3_3_3_6_p03` (score: 0.7020)
  4. `chunk_node_L5_cytisine` (score: 0.6971)
  5. `chunk_sec_3_3_2` (score: 0.6889)
- **Retrieved Gold Chunks:** `["chunk_sec_3_3_3_4"]` (Rank 1)
- **Missing Gold Chunks:** None
- **Retrieval Status:** **PASS**

---

### `real_13`
- **Question:** What is the benefit-to-harm ratio for bupropion in terms of how many patients benefit versus how many experience serious side effects or drop out?
- **Gold Chunk:** `chunk_sec_3_3_3_6_p01`
- **Top 5 Retrieved:**
  1. `chunk_sec_3_3_3_6_p01` (score: 0.8541) [GOLD]
  2. `chunk_sec_3_3_3_2` (score: 0.8468)
  3. `chunk_sec_3_3_3_6_p02` (score: 0.8454)
  4. `chunk_sec_3_3_3_6_p04` (score: 0.8396)
  5. `chunk_sec_3_3_4_p01` (score: 0.8000)
- **Retrieved Gold Chunks:** `["chunk_sec_3_3_3_6_p01"]` (Rank 1)
- **Missing Gold Chunks:** None
- **Retrieval Status:** **PASS**

---

### `real_14`
- **Question:** Does using a nicotine patch together with a fast-acting nicotine product work better than using a single nicotine product alone?
- **Gold Chunks:** `chunk_sec_3_3_3_5`, `chunk_sec_3_3_3_6_p03`
- **Top 5 Retrieved:**
  1. `chunk_sec_3_3_1` (score: 0.8623)
  2. `chunk_sec_3_3_3_1_p03` (score: 0.8493)
  3. `chunk_sec_3_3_3_1_p01` (score: 0.8424)
  4. `chunk_sec_3_3_3_5` (score: 0.8380) [GOLD]
  5. `chunk_sec_2_2_p04` (score: 0.5372)
- **Retrieved Gold Chunks:** `["chunk_sec_3_3_3_5"]` (Rank 4)
- **Missing Gold Chunks:** `["chunk_sec_3_3_3_6_p03"]`
- **Retrieval Status:** **PARTIAL**

---

### `real_15`
- **Question:** How does the effectiveness of cytisine compare directly against nicotine replacement therapy?
- **Gold Chunks:** `chunk_sec_3_3_3_4`, `chunk_sec_3_3_3_6_p03`
- **Top 5 Retrieved:**
  1. `chunk_sec_3_3_1` (score: 0.8626)
  2. `chunk_sec_3_3_3_1_p02` (score: 0.6962)
  3. `chunk_sec_3_3_3_4` (score: 0.6958) [GOLD]
  4. `chunk_sec_3_3_3_1_p01` (score: 0.6932)
  5. `chunk_node_L3_pharmacological_intervent` (score: 0.6931)
- **Retrieved Gold Chunks:** `["chunk_sec_3_3_3_4"]` (Rank 3)
- **Missing Gold Chunks:** `["chunk_sec_3_3_3_6_p03"]`
- **Retrieval Status:** **PARTIAL**

---

### `real_16`
- **Question:** Is higher-strength 4 mg nicotine gum more effective than standard 2 mg gum for heavy smokers?
- **Gold Chunk:** `chunk_sec_3_3_3_1_p02`
- **Top 5 Retrieved:**
  1. `chunk_sec_3_3_1` (score: 0.9755)
  2. `chunk_sec_3_3_3_1_p01` (score: 0.7591)
  3. `chunk_sec_3_3_3_1_p03` (score: 0.7444)
  4. `chunk_sec_3_3_3_1_p02` (score: 0.7411) [GOLD]
  5. `chunk_sec_3_7_3_p02` (score: 0.4634)
- **Retrieved Gold Chunks:** `["chunk_sec_3_3_3_1_p02"]` (Rank 4)
- **Missing Gold Chunks:** None
- **Retrieval Status:** **PASS**

---

### `real_17`
- **Question:** What is the recommended dose and quit rate for Topiramate when prescribed for smoking cessation?
- **Gold Chunk:** None *(Must Abstain)*
- **Top 5 Retrieved:**
  1. `chunk_sec_2_2_p04` (score: 0.8933)
  2. `chunk_sec_3_7_3_p01` (score: 0.8709)
  3. `chunk_sec_3_3_4_p01` (score: 0.8546)
  4. `chunk_sec_3_7_3_p05` (score: 0.8469)
  5. `chunk_node_L3_general_p02` (score: 0.8434)
- **Status:** **UNSUPPORTED_ABSTAIN**

---

### `real_18`
- **Question:** What does the WHO guideline conclude about transcranial magnetic stimulation (TMS) for nicotine dependence?
- **Gold Chunk:** None *(Must Abstain)*
- **Top 5 Retrieved:**
  1. `chunk_sec_1_1` (score: 0.8781)
  2. `chunk_sec_2_2_p04` (score: 0.8704)
  3. `chunk_node_L2_rationale_and_objectives` (score: 0.8674)
  4. `chunk_sec_1_2_p01` (score: 0.8493)
  5. `chunk_sec_6_p01` (score: 0.8316)
- **Status:** **UNSUPPORTED_ABSTAIN**

---

### `real_19`
- **Question:** Does adding bupropion to varenicline provide any extra benefit over taking varenicline alone?
- **Gold Chunks:** `chunk_sec_3_3_3_5`, `chunk_sec_3_3_3_6_p04`
- **Top 5 Retrieved:**
  1. `chunk_sec_3_3_1` (score: 0.8900)
  2. `chunk_sec_3_3_3_6_p04` (score: 0.8511) [GOLD]
  3. `chunk_sec_3_3_4_p01` (score: 0.8358)
  4. `chunk_sec_3_3_3_6_p02` (score: 0.8311)
  5. `chunk_sec_3_3_3_6_p01` (score: 0.7701)
- **Retrieved Gold Chunks:** `["chunk_sec_3_3_3_6_p04"]` (Rank 2)
- **Missing Gold Chunks:** `["chunk_sec_3_3_3_5"]`
- **Retrieval Status:** **PARTIAL**

---

### `real_20`
- **Question:** How effective is automated mobile phone text messaging for helping tobacco users quit?
- **Gold Chunk:** `chunk_sec_3_2_3_p02`
- **Top 5 Retrieved:**
  1. `chunk_sec_3_2_3_p02` (score: 0.9311) [GOLD]
  2. `chunk_sec_3_2_3_p01` (score: 0.9196)
  3. `chunk_sec_3_2_1` (score: 0.9116)
  4. `chunk_sec_3_2_2` (score: 0.9112)
  5. `chunk_node_L2_digital_tobacco_cessation` (score: 0.8909)
- **Retrieved Gold Chunks:** `["chunk_sec_3_2_3_p02"]` (Rank 1)
- **Missing Gold Chunks:** None
- **Retrieval Status:** **PASS**

---

## 4. Failure Analysis (Diagnostic Root-Cause Mapping)

Out of 18 supported questions:
- **3 questions suffered complete retrieval misses (Hit@5 = 0)**
- **3 questions suffered partial multi-chunk retrieval (Hit@5 = 1, but missed secondary chunk)**

```
Failure Breakdown (6 questions):
├── Complete Misses (3):
│   ├── real_01: Lexical/Terminology mismatch ("brief cessation talk" vs "brief advice")
│   ├── real_06: Semantic abstraction gap ("pills + talking therapy" vs "pharmacotherapy + behavioural")
│   └── real_07: Terminology mismatch ("chewing tobacco / snuff" vs "smokeless tobacco")
└── Partial Multi-Chunk Misses (3):
    ├── real_14: Missed conclusion chunk chunk_sec_3_3_3_6_p03
    ├── real_15: Missed conclusion chunk chunk_sec_3_3_3_6_p03
    └── real_19: Missed narrative section chunk_sec_3_3_3_5
```

### Analysis of Complete Misses:
1. **`real_01` (MISS):**
   - *Query:* "How long should a standard brief tobacco cessation talk take during a clinical appointment?"
   - *Gold:* `chunk_sec_3_1_1`
   - *Root Cause:* **Lexical & Query Expansion Gap.** The word "talk" and "appointment" in the query caused high dense semantic attraction to Section 3.2.3 digital conversational interventions (which repeatedly scored 0.85–0.87). The ClinicalQueryUnderstanding module failed to map "brief talk" to the formal clinical entity `"brief_advice"`.
2. **`real_06` (MISS):**
   - *Query:* "Is it more effective to use quit-smoking pills alongside talking therapy rather than trying pills alone?"
   - *Gold:* `chunk_sec_3_5_1` (Recommendation 8: Combining pharmacotherapy and behavioural interventions)
   - *Root Cause:* **Irrelevant Chunk Competition & Prior Bias.** The query words "pills" and "quit-smoking" triggered heavy BM25 and dense matches on Section 3.3.1 (general oral pharmacotherapy) and Section 3.3.3.3 (varenicline). The combined intervention recommendation chunk `chunk_sec_3_5_1` was crowded out by individual medication monotherapy chunks.
3. **`real_07` (MISS):**
   - *Query:* "What support should doctors give to patients trying to stop chewing tobacco or using snuff?"
   - *Gold:* `chunk_sec_3_4_1` (Recommendation 6: Intensive behavioural support for smokeless tobacco)
   - *Root Cause:* **Section Granularity / Ranking Preference.** The retriever retrieved Section 3.4.3 evidence chunks (`chunk_sec_3_4_3_p01` and `chunk_sec_3_4_3_p02`), but missed the top-level recommendation chunk `chunk_sec_3_4_1`. This is a ranking boundary issue between recommendation chunks and evidence summaries within the same clinical section.

### Analysis of Partial Multi-Chunk Misses:
- **`real_14`, `real_15`, `real_19` (PARTIAL):**
  - In all 3 comparison questions, the primary evidence chunk was successfully retrieved into Top-5, but the corresponding cross-referenced GDG Conclusion chunk (`chunk_sec_3_3_3_6_p03` or `chunk_sec_3_3_3_5`) was pushed below rank 5 by competing monotherapy chunks.

---

## 5. Unsupported Query Retrieval Behavior

| Question ID | Query | Top-1 Retrieved Chunk | Observation |
|---|---|---|---|
| `real_17` | What is the recommended dose and quit rate for Topiramate when prescribed for smoking cessation? | `chunk_sec_2_2_p04` (score: 0.8933) | Retriever returns general PICO background methodology chunks. Because BM25 has 0 matches for "Topiramate", dense retrieval falls back on generic pharmacotherapy search terms. |
| `real_18` | What does the WHO guideline conclude about transcranial magnetic stimulation (TMS) for nicotine dependence? | `chunk_sec_1_1` (score: 0.8781) | Retriever returns general Scope/Guideline Objectives chunks (`chunk_sec_1_1`, `chunk_sec_2_2_p04`). No evidence is returned, but similarity scores remain ~0.87 due to baseline dense cosine compression. |

---

## 6. Final Decision

### **READY_FOR_NEXT_PHASE**

### Justification:
1. **Overall Retrieval Competence:** The existing retrieval pipeline achieves **Hit@5 of 83.3% (15/18)** on completely realistic, unprompted clinical queries, exceeding the 80% operational baseline.
2. **Top-Rank Strength:** On factual and numerical queries where standard clinical entities are recognized, MRR is strong (0.5204), with key metrics (Cytisine RR, Bupropion NNT/NNH, NRT Study Counts, Background Statistics) placing at **Rank 1**.
3. **Identified Bottlenecks are Non-Fatal for Phase 2:** The 3 observed misses are concentrated in extreme colloquial paraphrasing ("talk" for advice, "pills" for pharmacotherapy, "chewing tobacco" for smokeless tobacco). These diagnose clear expansion targets for query understanding without indicating broken vector stores or inverted index corruption.

The retrieval layer is sufficiently functional and calibrated to proceed to the next diagnostic phase.
