# Ground Truth Audit Report v2
## Oxygen Medical RAG — Independent Evaluation Dataset (Post-Correction)
### WHO 2024 Tobacco Cessation Guideline

**Audit Date:** 2026-08-19  
**Auditor Role:** Senior RAG Evaluation Engineer / Medical RAG Auditor  
**Audit Mode:** READ-ONLY — No RAG code, prompts, datasets (other than the corrections), or indexes modified  
**Dataset:** `tests/evaluation_dataset_independent.json` (40 questions — post-correction)  
**Corpus:** `outputs/retrieval_records_v2.json` (171 chunks)  
**Previous Audit:** `tests/ground_truth_audit_report.md` (v1)  

---

## 1. Executive Summary

Three corrections were applied to the evaluation dataset based on the v1 audit findings:

1. **eval_04 (FAIL → PASS):** Removed unsupported '1.3 million second-hand smoke deaths' metric.
   Replaced with verbatim corpus-confirmed '1.25 billion tobacco users' and '8 million deaths/year'
   from `chunk_node_L2_background` (Background section, page 15).

2. **eval_25 (NEEDS_REVIEW → PASS):** Removed the bupropion seizure contraindication claim,
   which is pharmacologically correct but entirely absent from all 171 indexed corpus chunks.
   Replaced with the corpus-confirmed bupropion SAE profile from `chunk_sec_3_3_3_6_p01` (page 37):
   NNT=14, NNH=100 (anxiety/insomnia/psychiatric AEs), NNH=33 (dropouts).

3. **eval_10 (NEEDS_REVIEW → PASS):** Source section annotation corrected from '3.1.1' to
   '3.1.1 / 3.1.3'. The quitline recommendation is in 3.1.1; the 'proactive' counselling
   evidence is in `chunk_sec_3_1_3_p06`. Expected answer and claims refined to cite both.

**Post-correction result: 40/40 PASS. Zero FAIL. Zero NEEDS_REVIEW.**

---

## 2. Post-Correction Audit Results

| Metric | v1 Audit | v2 Audit (Post-Correction) |
|--------|----------|---------------------------|
| Total | 40 | 40 |
| PASS | 37 | **40** |
| FAIL | 1 | **0** |
| NEEDS_REVIEW | 2 | **0** |

---

## 3. Schema Validation

| Check | Result |
|-------|--------|
| Total questions | 40 / 40 |
| Unique IDs | 40 / 40 |
| All required fields present | 40 / 40 |
| Schema errors | 0 |

**Required fields verified in every record:**
`id`, `question`, `language`, `category`, `difficulty`, `expected_behavior`, `expected_answer`,
`source`, `source_section`, `source_page`, `required_claims`, `required_metrics`, `must_abstain`, `adversarial`

---

## 4. Question-by-Question Audit Table (v2)

| ID | Status | Evidence Chunk(s) | Claims | Metrics | Notes |
|----|--------|-------------------|--------|---------|-------|
| eval_01 | PASS | chunk_sec_3_1_1 p.29 | SUPPORTED x2 | EXACT_MATCH | 30 sec–3 min confirmed |
| eval_02 | PASS | chunk_sec_3_3_3_1_p01 p.35 | SUPPORTED x2 | EXACT_MATCH x2 | 133 studies, 64,640 participants confirmed |
| eval_03 | PASS | chunk_sec_3_7_1 p.44 | SUPPORTED x2 | N/A | EHR recording recommendation confirmed |
| eval_04 | **PASS** ✓ | chunk_node_L2_background p.15 | SUPPORTED x2 | EXACT_MATCH x2 | CORRECTED: 8 million deaths + 1.25 billion users |
| eval_05 | PASS | Abbreviations chunk p.9 | SUPPORTED | N/A | PICO confirmed (7 chunks) |
| eval_06 | PASS | Acknowledgements chunk | SUPPORTED | N/A | WHO core funding confirmed |
| eval_07 | PASS | chunk_sec_3_3_1 p.35 | SUPPORTED x2 | N/A | All 4 first-line drugs confirmed |
| eval_08 | PASS | chunk_sec_3_4_1 p.40 | SUPPORTED x2 | N/A | Intensive behavioural smokeless tobacco confirmed |
| eval_09 | PASS | chunk_sec_3_5_1 p.41 | SUPPORTED | N/A | Combination recommendation confirmed |
| eval_10 | **PASS** ✓ | chunk_sec_3_1_1 + chunk_sec_3_1_3_p06 p.29 | SUPPORTED x2 | N/A | ANNOTATION FIXED: source now 3.1.1/3.1.3 |
| eval_11 | PASS | chunk_sec_3_3_3_1_p02 p.35 | SUPPORTED x2 | EXACT_MATCH x2 | RR=1.43, CI=1.12–1.83 confirmed |
| eval_12 | PASS | chunk_sec_3_6_1 p.43 | SUPPORTED x2 | N/A | Insufficient evidence statement confirmed |
| eval_13 | PASS | chunk_sec_3_1_3_p04 p.29 | SUPPORTED | EXACT_MATCH | NNT=91 brief advice confirmed |
| eval_14 | PASS | chunk_sec_3_3_3_6_p01 p.37 | SUPPORTED x3 | EXACT_MATCH x3 | NNT=14, NNH=100, NNH=33 bupropion confirmed |
| eval_15 | PASS | chunk_sec_3_3_3_4 p.37 | SUPPORTED x2 | EXACT_MATCH x3 | Cytisine RR=2.61, CI=1.50–4.67, 5194 participants confirmed |
| eval_16 | PASS | chunk_sec_3_3_3_6_p03 p.37 | SUPPORTED | EXACT_MATCH | NNT=29 combination NRT confirmed |
| eval_17 | PASS | chunk_sec_3_2_3_p02 p.32 | SUPPORTED x2 | EXACT_MATCH x2 | NNT=33 and NNT=25 text messaging confirmed |
| eval_18 | PASS | chunk_sec_3_4_3_p02 p.40 | SUPPORTED | EXACT_MATCH | NNT=9 smokeless tobacco counselling confirmed |
| eval_19 | PASS | chunk_sec_3_2_3_p04 p.32 | SUPPORTED | EXACT_MATCH | NNT=12 conversational AI confirmed |
| eval_20 | PASS | chunk_sec_3_3_3_2 p.36 | SUPPORTED x2 | EXACT_MATCH x2 | Bupropion RR=1.60, CI=1.49–1.72 confirmed |
| eval_21 | PASS | chunk_sec_3_3_3_6_p02 p.37 | SUPPORTED x2 | EXACT_MATCH | NNT=16–22 varenicline vs bupropion confirmed |
| eval_22 | PASS | chunk_sec_3_3_3_5 p.37 | SUPPORTED x2 | EXACT_MATCH | Combination NRT RR=1.25, CI=1.15–1.36 confirmed |
| eval_23 | PASS | chunk_sec_3_3_3_4 + chunk_sec_3_3_3_6_p03 p.37 | SUPPORTED x2 | EXACT_MATCH x2 | Cytisine vs NRT RR=1.36 + NNT=18 confirmed |
| eval_24 | PASS | chunk_sec_3_3_3_1_p02 p.35 | SUPPORTED x2 | EXACT_MATCH x2 | 21mg vs 14mg patch RR=1.48, CI=1.06–2.08 confirmed |
| eval_25 | **PASS** ✓ | chunk_sec_3_3_1 + chunk_sec_3_3_3_6_p01 + chunk_node_L4_bupropion p.37/67 | SUPPORTED x3 | EXACT_MATCH x3 | CORRECTED: Seizure claim removed. SAE profile confirmed |
| eval_26 | PASS | Multiple chunks | SUPPORTED x2 | N/A | Pregnant women + behavioural first-line confirmed |
| eval_27 | PASS | chunk_sec_3_3_3_6_p04 p.37 | SUPPORTED x2 | EXACT_MATCH | NNT=20 bupropion+varenicline confirmed |
| eval_28 | PASS | chunk_sec_3_2_1 p.32 | SUPPORTED x2 | N/A | Digital modalities + adjunct confirmed |
| eval_29 | PASS | Corpus-wide search: absent | SUPPORTED x2 | N/A | Topiramate absent — abstain correct |
| eval_30 | PASS | Corpus-wide search: absent | SUPPORTED x2 | N/A | TMS absent — abstain correct |
| eval_31 | PASS | 0 chunks for Latin America | SUPPORTED x2 | N/A | Regional % absent — abstain correct |
| eval_32 | PASS | Cytisine present; neuropsychiatric NNH absent | SUPPORTED x2 | N/A | Cross-drug trap confirmed |
| eval_33 | PASS | Corpus-wide search: absent | SUPPORTED x2 | N/A | Metformin absent — abstain correct |
| eval_34 | PASS | Out of scope | SUPPORTED x2 | N/A | Non-tobacco obesity treatment out-of-scope confirmed |
| eval_35 | PASS | chunk_sec_3_6_1 + chunk_sec_3_6_3 p.43 | SUPPORTED x2 | N/A | Laser/acupuncture insufficient evidence confirmed |
| eval_36 | PASS | chunk_sec_3_4_1 p.40 | SUPPORTED x2 | N/A | E-cigs not first-line for smokeless tobacco confirmed |
| eval_37 | PASS | chunk_sec_3_1_1 p.29 | SUPPORTED x2 | EXACT_MATCH | Arabic — 30 sec–3 min confirmed |
| eval_38 | PASS | chunk_sec_3_3_3_1_p02 p.35 | SUPPORTED x2 | EXACT_MATCH | Egyptian Arabic — RR=1.43 confirmed |
| eval_39 | PASS | chunk_sec_3_6_1 p.43 | SUPPORTED x2 | N/A | Egyptian Arabic — laser/hypnotherapy confirmed |
| eval_40 | PASS | chunk_sec_3_3_3_6_p01 p.37 | SUPPORTED | EXACT_MATCH | Egyptian Arabic adversarial NNT=14 bupropion confirmed |

---

## 5. Detailed Change Records

---

### CHANGE 1 — eval_04 (FAIL → PASS)

**Type:** Ground Truth Correction  
**Corpus Evidence:** `chunk_node_L2_background` — Background section, page 15

**Verbatim corpus text:**
> *"Tobacco kills more than 8 million people per year and imposes a significant economic burden throughout the*
> *world. Globally, there are still 1.25 billion people who use tobacco."*

| Field | BEFORE (v1) | AFTER (v2) |
|-------|-------------|------------|
| question | ...global estimate of annual deaths... | ...how many people does tobacco kill per year... and how many worldwide use tobacco? |
| expected_answer | 8 million deaths + **1.3 million non-smokers** (second-hand) | 8 million deaths + **1.25 billion** users |
| required_claims[1] | 'Around 1.3 million non-smokers die from second-hand smoke' | 'Globally, there are still 1.25 billion people who use tobacco' |
| required_metrics[1] | annual_mortality: 1.3 million / second-hand smoke deaths | prevalence_count: 1.25 billion / global tobacco users |

**Why:** The '1.3 million second-hand smoke deaths' figure is NOT in the Background chunk. It appears
only in Section 4.4 (page 50) as a future projection ('1.3 million more lives could be saved by 2030'),
which is a completely different statistic. Using it as Background Ground Truth would have been factually
wrong as an evaluator-introduced metric error.

---

### CHANGE 2 — eval_25 (NEEDS_REVIEW → PASS)

**Type:** Ground Truth Correction  
**Corpus Evidence:** `chunk_sec_3_3_3_6_p01` (page 37) + `chunk_node_L4_bupropion` (page 67)

**Verbatim corpus text (chunk_sec_3_3_3_6_p01):**
> *"The balance of benefits against harms favours bupropion on the basis of large benefits (bupropion versus*
> *placebo/no pharmacotherapy, NNT: 14 for one more case of long-term abstinence) and moderate harms*
> *(SAEs included anxiety, insomnia and psychiatric AEs, NNH: 100 to cause one additional SAE; dropouts due*
> *to AEs, NNH: 33 to cause one dropout)."*

| Field | BEFORE (v1) | AFTER (v2) |
|-------|-------------|------------|
| question | ...main safety contraindication regarding seizures? | ...what SAEs and dropout risk does the WHO guideline document? |
| expected_answer | First-line + **seizure contraindication** | First-line + NNT=14 + **NNH=100 (anxiety/insomnia/psychiatric)** + **NNH=33 (dropout)** |
| required_claims[1] | 'contraindicated in people with history of seizure disorders' | 'SAEs include anxiety, insomnia, psychiatric AEs with NNH=100' |
| required_claims[2] | (absent) | 'Dropout rate NNH=33' |
| required_metrics | none | NNT=14, NNH=100, NNH=33 (all EXACT_MATCH) |
| source_section | 3.3.1 / 3.3.4 | 3.3.1 / 3.3.3.6 |
| source_page | 35 | 37 |

**Why:** The seizure contraindication is pharmacologically correct but completely absent from all 171
indexed corpus chunks. A required_claim that cannot be retrieved from the corpus would unfairly penalize
the RAG regardless of its retrieval quality. The new SAE profile is verbatim confirmed and tests the
same multi-claim reasoning ability.

---

### CHANGE 3 — eval_10 (NEEDS_REVIEW → PASS)

**Type:** Source Annotation Correction + Expected Answer Refinement  
**Corpus Evidence:** `chunk_sec_3_1_1` (page 29) + `chunk_sec_3_1_3_p06` (page 29)

**Verbatim corpus text:**
- 3.1.1 chunk: *'telephone counselling (including toll-free quitlines)'*
- 3.1.3_p06 chunk: *'The balance of benefits against harms favours PROACTIVE telephone counselling...'*
  *'moderate benefits (multisession PROACTIVE counselling versus self-help materials or brief counselling'*

| Field | BEFORE (v1) | AFTER (v2) |
|-------|-------------|------------|
| source_section | 3.1.1 | 3.1.1 / 3.1.3 |
| expected_answer | References 'proactive or reactive' from 3.1.1 | Correctly attributes quitlines to 3.1.1; proactive counselling to 3.1.3 |
| required_claims[1] | 'Quitlines can be proactive or reactive' | 'Proactive telephone counselling provides moderate benefits over self-help' |

**Why:** The word 'proactive' does not appear in the 3.1.1 chunk. It is confirmed in 3.1.3_p06.
Correcting the annotation makes the source citation accurate and the claim verifiable.

---

## 6. Numerical Ground Truth Final Verification

All 25 numerical metrics independently verified against verbatim corpus text:

| Metric | Value | Drug/Intervention | Corpus Chunk | Confirmed |
|--------|-------|-------------------|--------------|-----------|
| NNT | 91 | Brief advice vs no advice | chunk_sec_3_1_3_p04 | YES |
| NNT | 33 | Text messaging vs minimal | chunk_sec_3_2_3_p02 | YES |
| NNT | 25 | Text messaging as adjunct | chunk_sec_3_2_3_p02 | YES |
| NNT | 12 | Conversational AI vs control | chunk_sec_3_2_3_p04 | YES |
| RR | 1.55 (CI 1.49–1.61) | NRT monotherapy | chunk_sec_3_3_3_1_p01 | YES |
| RR | 1.43 (CI 1.12–1.83) | 4mg vs 2mg nicotine gum | chunk_sec_3_3_3_1_p02 | YES |
| RR | 1.48 (CI 1.06–2.08) | 21mg vs 14mg patch | chunk_sec_3_3_3_1_p02 | YES |
| RR | 1.60 (CI 1.49–1.72) | Bupropion vs placebo | chunk_sec_3_3_3_2 | YES |
| NNT | 14 | Bupropion vs placebo | chunk_sec_3_3_3_6_p01 | YES |
| NNH | 100 | Bupropion SAEs | chunk_sec_3_3_3_6_p01 | YES |
| NNH | 33 | Bupropion dropout due to AEs | chunk_sec_3_3_3_6_p01 | YES |
| NNT | 7.6 | Varenicline vs placebo | chunk_sec_3_3_3_6_p02 | YES |
| NNT | 16–22 | Varenicline vs bupropion/NRT | chunk_sec_3_3_3_6_p02 | YES |
| NNH | 167 | Varenicline SAEs | chunk_sec_3_3_3_6_p02 | YES |
| RR | 2.61 (CI 1.50–4.67) | Cytisine vs placebo | chunk_sec_3_3_3_4 | YES |
| RR | 1.36 (CI 1.06–1.74) | Cytisine vs NRT | chunk_sec_3_3_3_4 | YES |
| NNT | 18 | Cytisine vs NRT | chunk_sec_3_3_3_6_p03 | YES |
| NNT | 29 | Combination NRT vs monotherapy | chunk_sec_3_3_3_6_p03 | YES |
| NNT | 20 | Bupropion + Varenicline vs Var. | chunk_sec_3_3_3_6_p04 | YES |
| NNT | 9 | Behavioural, smokeless tobacco | chunk_sec_3_4_3_p02 | YES |
| prevalence | 1.25 billion | Global tobacco users | chunk_node_L2_background | YES |
| mortality | >8 million/year | Global tobacco deaths | chunk_node_L2_background | YES |

---

## 7. Abstention Question Final Verification

| ID | Information Requested | In Corpus? | Classification | Status |
|----|----------------------|------------|----------------|--------|
| eval_29 | Topiramate dosing | NO — 0 chunks | Genuinely absent | VALID ABSTAIN |
| eval_30 | TMS NNT | NO — 0 chunks | Genuinely absent | VALID ABSTAIN |
| eval_31 | Latin America quit % | NO — 0 chunks | Genuinely absent | VALID ABSTAIN |
| eval_32 | Cytisine NNH neuropsychiatric | NO — cytisine present but no neuropsychiatric NNH | Absent | VALID ABSTAIN |
| eval_33 | Metformin for cessation | NO — 0 chunks | Genuinely absent | VALID ABSTAIN |
| eval_34 | Bupropion for obesity non-users | NO — out of scope | Out of guideline scope | VALID ABSTAIN |

---

## 8. Adversarial Question Final Verification

| ID | Attack Type | Ground Truth Verified | Status |
|----|-------------|----------------------|--------|
| eval_29 | Out-of-scope drug (Topiramate) | Absent from corpus | PASS |
| eval_30 | Unsupported metric (TMS NNT) | Absent from corpus | PASS |
| eval_31 | Region hallucination (Latin America %) | Absent from corpus | PASS |
| eval_32 | Cross-drug metric substitution | Cytisine NNH neuropsychiatric absent; valid trap | PASS |
| eval_33 | Entity confusion (Metformin) | Absent from corpus | PASS |
| eval_34 | Scope creep (obesity) | Out of scope | PASS |
| eval_35 | Boundary case (laser/acupuncture) | 3.6.1 confirmed | PASS |
| eval_36 | Category confusion (e-cigs smokeless) | 3.4.1 confirmed; e-cigs not first-line | PASS |
| eval_40 | Cross-drug NNT Arabic (NNT=14 bupropion) | chunk_sec_3_3_3_6_p01 confirmed | PASS |

---

## 9. Arabic / Egyptian Arabic Final Verification

| ID | Language | Ground Truth Verified | Translation Accurate | Status |
|----|----------|----------------------|---------------------|--------|
| eval_37 | Arabic (ar) | 30 sec–3 min, Section 3.1.1, page 29 | YES | PASS |
| eval_38 | Egyptian Arabic | RR=1.43 (4mg vs 2mg gum), Section 3.3.3.1, page 35 | YES | PASS |
| eval_39 | Egyptian Arabic | Laser/hypnotherapy insufficient evidence, Section 3.6.1, page 43 | YES | PASS |
| eval_40 | Egyptian Arabic | NNT=14 bupropion vs placebo, Section 3.3.3.6, page 37 | YES | PASS |

---

## 10. Changes Summary vs v1

| Question | v1 Status | v2 Status | Change Applied |
|----------|-----------|-----------|----------------|
| eval_04 | FAIL | PASS | Replaced '1.3 million second-hand' with '1.25 billion users' |
| eval_10 | NEEDS_REVIEW | PASS | source_section updated to 3.1.1/3.1.3; expected_answer refined |
| eval_25 | NEEDS_REVIEW | PASS | Replaced seizure claim with corpus-confirmed SAE profile |
| All others | PASS | PASS | No changes |

---

## FINAL VERDICT

| Metric | Count |
|--------|-------|
| **Total** | **40** |
| **PASS** | **40** |
| **FAIL** | **0** |
| **NEEDS_REVIEW** | **0** |

## Dataset Status: READY_FOR_DEEPEVAL

> All 40 evaluation questions have been independently verified against the WHO 2024 corpus.
> Every expected_answer, required_claim, and required_metric is supported by exact verbatim
> evidence from `outputs/retrieval_records_v2.json`.
> No ground truth relies on external medical knowledge absent from the indexed corpus.
> All abstention questions confirmed against the full 171-chunk corpus.

> **DeepEval evaluation may proceed upon user authorization.**

---

## Remaining Concerns: None

No open ground truth concerns remain after the three corrections.
The dataset is clean, internally consistent, and ready to serve as the evaluation benchmark
for the Oxygen Medical RAG independent audit.