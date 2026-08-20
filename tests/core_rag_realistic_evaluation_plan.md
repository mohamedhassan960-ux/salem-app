# Realistic Core RAG Evaluation Plan

## 1. Objective
Determine whether the core Oxygen Medical RAG retrieval pipeline reliably retrieves the correct evidence from its existing 171-chunk WHO corpus when given realistic, naturally phrased user questions.

This test is strictly diagnostic: it evaluates retrieval, reranking, and evidence gate accuracy independently from generation quality.

---

## 2. Dataset Distribution (20 Questions)

All 20 questions are naturally phrased in English, representing realistic clinician or patient inquiries:

| Category | Count | Primary Focus |
|---|:---:|---|
| **Direct Factual** | 5 | Clean factual lookup (brief advice duration, first-line meds, EHR recording, alternative therapies, trial base) |
| **Semantic / Paraphrased** | 5 | Tests conceptual mapping without keyword overlap (pills + therapy, chewing tobacco, apps/texting, counselling formats, global toll) |
| **Numerical** | 4 | Tests retrieval of exact statistics without prompting the numbers in query (brief advice NNT, cytisine RR, bupropion NNT/NNH, texting NNT) |
| **Comparison / Multi-Evidence** | 4 | Head-to-head comparisons requiring single or multi-chunk evidence (combo NRT vs single, cytisine vs NRT, 4mg vs 2mg gum, bupropion + varenicline) |
| **Unsupported (Abstention)** | 2 | Genuinely absent clinical topics (Topiramate, TMS) to verify safe rejection |
| **TOTAL** | **20** | **100% English, 100% Corpus-Grounded, Zero Synthetic Overfitting** |

---

## 3. Evaluation Metrics & Layer Separation

To isolate pipeline bottlenecks, the evaluation records metrics at each stage independently:

```
[Realistic User Question]
          │
          ▼
┌──────────────────────────────────────┐   ───▶ 1. Retrieval Layer:
│ Hybrid Retrieval (Dense + Sparse BM25)│        - Hit@1, Hit@3, Hit@5
└─────────────────┬────────────────────┘        - MRR (Mean Reciprocal Rank)
                  │
                  ▼
┌──────────────────────────────────────┐   ───▶ 2. Clinical Reranker:
│ Cross-Encoder / Priors Reranking     │        - Gold Chunk Promotion Delta
└─────────────────┬────────────────────┘        - Top-3 Precision
                  │
                  ▼
┌──────────────────────────────────────┐   ───▶ 3. Evidence Quality Gate:
│ Threshold & Confidence Filtering     │        - Gold Evidence Admission Rate (%)
└─────────────────┬────────────────────┘        - False Admission Rate on Abstentions
                  │
                  ▼
┌──────────────────────────────────────┐   ───▶ 4. End-to-End Generation (Separate):
│ LLM Response & Claim Grounding       │        - Grounding Faithfulness (%)
└──────────────────────────────────────┘        - Abstention Accuracy (%)
```

### Metrics Definitions:
- **Hit@K (K=1, 3, 5):** Proportion of queries where at least one gold chunk is present in the top-K retrieved items.
- **MRR (Mean Reciprocal Rank):** $(1/|Q|) \sum_{i=1}^{|Q|} (1/	ext{rank}_i)$ of the first gold chunk retrieved.
- **Gold Evidence Admission Rate:** Percentage of supported questions where at least one gold chunk passes the evidence selection gate.
- **Abstention Accuracy:** Percentage of unsupported questions where the system correctly refuses to answer due to lack of evidence.

---

## 4. Diagnostic Interpretation Guide

| Metric Pattern | Diagnosis | Recommended Action |
|---|---|---|
| Retrieval High (>90%), Generation Low (<70%) | Retriever is healthy; issue lies in LLM prompt or claim extraction. | Tune generation prompt / context assembly. |
| Retrieval Low (<75%), Reranker High | Initial hybrid search missed relevant chunks. | Tune BM25 weights / embedding model. |
| Reranker demotes gold chunks | Reranker priors penalizing valid evidence. | Adjust section/evidence level prior weights. |
| Evidence Gate rejects gold chunks | Gate score threshold set too aggressively. | Lower admission threshold or tune score calibration. |
| Abstention Accuracy < 100% | Hallucination on unsupported questions. | Strengthen evidence threshold for ungrounded queries. |
