# Core Oxygen Medical RAG Evaluation Plan

## 1. Objective
Perform a realistic, fair, and concise benchmark to answer the primary architectural question:
> **"Is the core Oxygen Medical RAG retrieval pipeline working correctly?"**

This evaluation isolates and measures each layer of the pipeline (Retrieval, Reranking, Evidence Quality Gate, and Generation) against a rigorous 20-question English gold-standard dataset grounded in the WHO 2024 Tobacco Cessation Guideline.

---

## 2. Dataset Distribution (20 Questions)

All questions are realistic clinical or user queries in English and grounded exclusively in `outputs/retrieval_records_v2.json` (171 chunks):

| Category | Count | Target Scope & Key Ground Truth Anchors |
|---|:---:|---|
| **Direct Factual** | 5 | Brief advice duration (30s-3min), First-line drugs (4), EHR recording (3.7.1), Global burden (>8M deaths, 1.25B users), NRT trial base (133 studies, 64,640 participants) |
| **Clinical Recommendation** | 4 | Smokeless tobacco (intensive support), Combination therapy (pharmacotherapy + behavioral), Alternative therapies (insufficient evidence), Digital interventions (adjunct role) |
| **Numerical / Statistical** | 4 | Brief advice NNT=91, Bupropion NNT=14 / NNH=100 / NNH=33, Cytisine RR=2.61 (95% CI: 1.50-4.67), SMS NNT=33 / NNT=25 |
| **Comparison Questions** | 3 | Cytisine vs NRT (RR=1.36, NNT=18), 4 mg vs 2 mg gum (RR=1.43), Combo NRT vs Single NRT (RR=1.25, NNT=29) |
| **Multi-Claim Questions** | 2 | Bupropion + Varenicline (NNT=20 + clinical indications), Smokeless tobacco (NNT=9 + delivery formats) |
| **Unsupported / Abstention** | 2 | Topiramate (unsupported drug), TMS (unsupported modality) — must trigger abstention |
| **TOTAL** | **20** | **100% English, 100% Corpus-Grounded, Zero External Knowledge Required** |

---

## 3. Modular Evaluation Architecture & Metrics

To prevent hallucinated answers or parametric LLM luck from masking retrieval defects, the evaluation cleanly isolates four distinct pipeline layers:

```
[User Query]
     │
     ▼
┌─────────────────────────┐   ───▶ Metric: Hit@1, Hit@3, Hit@5, MRR
│  A) Retrieval Layer     │        (Did hybrid search find gold chunk?)
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐   ───▶ Metric: Rank Promotion / Position Delta
│  B) Clinical Reranker   │        (Did clinical priors push gold chunk up?)
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐   ───▶ Metric: Gate Precision & Recall
│  C) Evidence Gate       │        (Did quality gate retain gold chunk?)
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐   ───▶ Metric: Groundedness & Claim Accuracy
│  D) Generation & Claims │        (Is the generated answer faithful & supported?)
└─────────────────────────┘
```

### A. Retrieval Layer Metrics
- **Hit@K (K=1, 3, 5):** Proportion of queries where at least one `gold_chunk_id` is present in top-K retrieved items.
- **Mean Reciprocal Rank (MRR):** $(1/|Q|) \sum_{i=1}^{|Q|} (1/	ext{rank}_i)$ of the first gold chunk retrieved.

### B. Reranking Layer Metrics
- **Reranker Rank Delta:** Average rank improvement $	ext{Rank}_{	ext{initial}} - 	ext{Rank}_{	ext{reranked}}$ for gold evidence chunks.

### C. Evidence Gate Metrics
- **Admissibility Rate:** Proportion of gold chunks that pass the evidence threshold and reach the context assembler.

### D. End-to-End Answer & Grounding Metrics
- **Retrieval Verdict (PASS/FAIL):** `PASS` if $\ge 1$ gold chunk is in the assembled context (or if `must_abstain=True` and no false positive chunks are forced).
- **Grounding Verdict (PASS/FAIL):** `PASS` if 100% of asserted clinical claims and metrics map directly to retrieved context.
- **Answer Correctness (PASS/FAIL):** `PASS` if the final response accurately conveys all `expected_claims` and exact `expected_metric` values.
- **Abstention Verdict (PASS/FAIL):** `PASS` if unsupported queries (`core_19`, `core_20`) trigger explicit, safe abstention without hallucinating metrics.

---

## 4. Strict Pass / Fail Decision Logic

| Scenario | Retrieval Status | Generation Status | Final Evaluation Outcome | Diagnosis |
|---|:---:|:---:|:---:|---|
| Gold chunk retrieved & correct answer generated | **PASS** | **PASS** | **PASS** | Full Pipeline Healthy |
| Gold chunk retrieved but answer inaccurate/hallucinated | **PASS** | **FAIL** | **FAIL** | Generator / Context Issue |
| Gold chunk NOT retrieved, but LLM guessed correctly | **FAIL** | **FAIL\*** | **FAIL** | Retrieval Defect (Unsafe Parametric Memory) |
| Gold chunk NOT retrieved and answer failed | **FAIL** | **FAIL** | **FAIL** | Retrieval Defect |
| Unsupported query correctly abstained | **PASS** | **PASS** | **PASS** | Safe Grounding & Abstention |
| Unsupported query resulted in hallucinated answer | **FAIL** | **FAIL** | **FAIL** | Abstention Failure / Hallucination |

*\*Crucial Rule: A correct answer NEVER counts as a test pass if the gold chunk was missed by retrieval.*
