# Evaluation Dataset Report
## Oxygen Medical RAG — Independent Audit Dataset

**File:** `tests/evaluation_dataset_independent.json`  
**Created:** 2026-08-19  
**Auditor role:** Senior RAG Evaluation Engineer (Audit Mode — no source code changes)

---

## 1. Dataset Summary

| Metric | Value |
|--------|-------|
| Total questions | 40 |
| Source document | WHO 2024 Clinical Treatment Guideline for Tobacco Cessation in Adults |
| Source corpus | `outputs/retrieval_records_v2.json` (171 indexed chunks) |
| Adversarial questions | 9 (22.5%) |
| Must-abstain questions | 6 (15%) |
| Languages covered | English, Arabic (Modern Standard), Arabic (Egyptian Colloquial) |

---

## 2. Distribution by Category

| Category | Count | Target | Status |
|----------|-------|--------|--------|
| direct_factual | 6 | 6 | PASS |
| clinical_recommendations | 6 | 6 | PASS |
| numerical_statistical | 8 | 8 | PASS |
| comparison_questions | 4 | 4 | PASS |
| multi_claim_questions | 4 | 4 | PASS |
| unsupported_questions | 4 | 4 | PASS |
| scope_entity_confusion | 4 | 4 | PASS |
| arabic_questions | 4 | 4 | PASS |
| **TOTAL** | **40** | **40** | **PASS** |

---

## 3. Distribution by Difficulty

| Difficulty | Count | Percentage |
|------------|-------|------------|
| easy | 4 | 10% |
| medium | 16 | 40% |
| hard | 20 | 50% |

---

## 4. Distribution by Language

| Language | Count |
|----------|-------|
| English (en) | 36 |
| Arabic Modern Standard (ar) | 1 |
| Arabic Egyptian Colloquial (ar_egyptian) | 3 |

---

## 5. Adversarial Question Coverage

The dataset contains **9 adversarial questions** (22.5%).

| ID | Attack Type |
|----|-------------|
| eval_29 | Out-of-scope drug (Topiramate) — hallucination trap |
| eval_30 | Unsupported modality (TMS NNT) — metric fabrication trap |
| eval_31 | Region-specific statistic (Latin America) — specificity hallucination |
| eval_32 | Cross-drug metric substitution (Cytisine NNH vs Varenicline NNH) |
| eval_33 | Entity confusion (Metformin for nicotine withdrawal) |
| eval_34 | Scope creep (bupropion for obesity in non-tobacco users) |
| eval_35 | Boundary question (laser/acupuncture — insufficient evidence, not full abstain) |
| eval_36 | Entity confusion (e-cigarettes as first-line for smokeless tobacco) |
| eval_40 | Cross-drug NNT confusion in Arabic (Bupropion vs Varenicline metric conflation) |

---

## 6. Ground-Truth Anchors (Key WHO Metrics Tested)

All numerical ground truths extracted verbatim from `outputs/retrieval_records_v2.json`.

| Metric | Drug / Intervention | Value | Section | Page |
|--------|---------------------|-------|---------|------|
| NNT | Brief advice (vs no advice) | 91 | 3.1.3 | 29 |
| NNT | Group counselling (vs no intervention) | 8-25 | 3.1.3 | 29 |
| NNT | Text messaging (vs minimal support) | 33 | 3.2.3 | 32 |
| NNT | Text messaging (as adjunct) | 25 | 3.2.3 | 32 |
| NNT | Conversational AI intervention | 12 | 3.2.3 | 32 |
| RR | NRT monotherapy (vs control) | 1.55 (95% CI: 1.49-1.61) | 3.3.3.1 | 35 |
| RR | Nicotine gum 4 mg vs 2 mg | 1.43 (95% CI: 1.12-1.83) | 3.3.3.1 | 35 |
| RR | Bupropion (vs placebo, 50 studies) | 1.60 (95% CI: 1.49-1.72) | 3.3.3.2 | 36 |
| NNT | Bupropion (vs placebo) | 14 | 3.3.3.6 | 37 |
| NNH | Bupropion SAEs | 100 | 3.3.3.6 | 37 |
| NNH | Bupropion dropouts due to AEs | 33 | 3.3.3.6 | 37 |
| RR | Cytisine (vs placebo, 6+ months) | 2.61 (95% CI: 1.50-4.67) | 3.3.3.4 | 37 |
| RR | Cytisine (vs NRT) | 1.36 (95% CI: 1.06-1.74) | 3.3.3.4 | 37 |
| NNT | Cytisine (vs NRT) | 18 | 3.3.3.6 | 37 |
| NNT | Combination NRT (vs monotherapy) | 29 | 3.3.3.6 | 37 |
| NNT | Bupropion + Varenicline (vs Var. alone) | 20 | 3.3.3.6 | 37 |
| NNT | Behavioural counselling (smokeless tobacco) | 9 | 3.4.3 | 40 |

---

## 7. Overlap Analysis with Existing Test Suite

**Method:** Jaccard token similarity (threshold > 0.5) across all 40 independent questions
vs 29 extracted test question strings from `tests/*.py`.

| Metric | Value |
|--------|-------|
| Independent questions | 40 |
| Existing test queries | 29 |
| High-overlap pairs (Jaccard > 0.5) | 2 |
| Overlap rate | **5.0%** |
| **Novelty rate** | **95.0%** |

**Requirement met: >90% novelty confirmed.**

### Flagged near-overlaps (semantic analysis):

1. **eval_19** (AI NNT=12) vs 'What is the NNT for semaglutide for tobacco cessation?'
   - Tokens overlap on 'nnt', 'tobacco', 'cessation'. Semantically OPPOSITE: one tests a
     supported metric (AI NNT=12), the other tests an unsupported drug (must-abstain).
     No real duplication.

2. **eval_32** (Cytisine NNH, neuropsychiatric) vs 'What is the NNH for neuropsychiatric
   serious adverse events for varenicline?'
   - eval_32 deliberately targets the cross-drug metric substitution trap: system must
     NOT return Varenicline NNH=167 for cytisine, where no NNH value exists.
     Adversarial by design, not a duplicate.

---

## 8. JSON Schema Compliance

All 40 questions include the required fields:

    id, question, language, category, difficulty, expected_behavior,
    expected_answer, source, source_section, source_page,
    required_claims, required_metrics, must_abstain, adversarial

All fields verified programmatically.

---

## 9. Verification Methodology

1. **Source verification:** All expected_answer values cross-checked against verbatim WHO
   chunk text from `outputs/retrieval_records_v2.json` using keyword searches for NNT,
   NNH, RR, and section numbers.
2. **No source code modified:** Audit constraint fully observed. No changes to RAG source,
   prompts, retrieval logic, reranker, evidence gate, claim validator, indexes, source
   documents, or existing tests.
3. **Overlap analysis:** Automated Jaccard token similarity scan against 29 existing test
   questions extracted from `tests/*.py` files.
4. **Distribution verification:** All 8 category quotas match the specification exactly.
5. **Adversarial coverage:** 9 adversarial questions spanning 5 attack types:
   out-of-scope drugs, unsupported metrics, region-specific hallucination,
   cross-drug metric substitution, scope creep.

---

## 10. Usage Instructions (For Phase 4 — When Authorized)

```python
import json

with open('tests/evaluation_dataset_independent.json', 'r', encoding='utf-8') as f:
    eval_dataset = json.load(f)

# Filter by category
factual = [q for q in eval_dataset if q['category'] == 'numerical_statistical']

# Filter must-abstain
abstain_cases = [q for q in eval_dataset if q['must_abstain']]

# Filter adversarial
adversarial = [q for q in eval_dataset if q['adversarial']]
```

> WARNING: DO NOT run DeepEval evaluation until explicitly authorized by the user.
