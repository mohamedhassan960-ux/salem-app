# Ground Truth Audit Report
## Oxygen Medical RAG — Independent Evaluation Dataset
### WHO 2024 Tobacco Cessation Guideline

**Audit Date:** 2026-08-19  
**Auditor Role:** Senior RAG Evaluation Engineer / Medical RAG Auditor  
**Audit Mode:** READ-ONLY — No RAG code, prompts, datasets, or indexes modified  
**Dataset:** `tests/evaluation_dataset_independent.json` (40 questions)  
**Corpus:** `outputs/retrieval_records_v2.json` (171 chunks)  

---

## 1. Executive Summary

An independent ground truth audit was performed on all 40 evaluation questions by:

1. Loading the complete evaluation dataset
2. Searching the full WHO corpus (171 chunks) for supporting evidence for every question
3. Verifying exact numerical metrics (NNT, NNH, RR, CI, duration, counts) against verbatim chunk text
4. Auditing every must-abstain question to confirm the absence of information in the corpus
5. Performing special deep-corpus verification on all 9 adversarial questions

**Key Findings:**
- 37 of 40 questions have fully verified, corpus-supported ground truths
- 1 question (eval_04) has a PARTIAL FAIL — one metric in the expected_answer is NOT supported by the indexed corpus
- 1 question (eval_25) has a NEEDS_REVIEW — the seizure contraindication claim is medically correct but absent from the indexed corpus
- 1 question (eval_10) has a PARTIAL NEEDS_REVIEW — "proactive" modifier for quitlines is absent from Section 3.1.1 chunk
- All 6 must-abstain questions are correctly classified — the requested information is genuinely absent from the corpus
- All 9 adversarial questions are structurally sound

---

## 2. Overall Results

| Status | Count |
|--------|-------|
| PASS | 37 |
| FAIL | 1 |
| NEEDS_REVIEW | 2 |
| **TOTAL** | **40** |

---

## 3. Question-by-Question Audit Table

| ID | Status | Category | Evidence Found | Claims | Metrics | Notes |
|----|--------|----------|----------------|--------|---------|-------|
| eval_01 | PASS | direct_factual | chunk_sec_3_1_1 p.29 | SUPPORTED x2 | EXACT_MATCH | "30 seconds and 3 minutes per encounter" verbatim confirmed |
| eval_02 | PASS | direct_factual | chunk_sec_3_3_3_1_p01 p.35 | SUPPORTED x2 | EXACT_MATCH x2 | "133 studies that included 64,640 participants" confirmed |
| eval_03 | PASS | direct_factual | chunk_sec_3_7_1 p.44 | SUPPORTED x2 | N/A | EHR recording recommendation confirmed |
| eval_04 | **FAIL** | direct_factual | chunk_node_L2_background p.15 | SUPPORTED / UNSUPPORTED | EXACT_MATCH / NOT_FOUND | "8 million" confirmed; "1.3 million non-smokers" NOT in corpus |
| eval_05 | PASS | direct_factual | Abbreviations chunk p.9 | SUPPORTED | N/A | PICO expansion confirmed |
| eval_06 | PASS | direct_factual | Acknowledgements chunk | SUPPORTED | N/A | WHO core funding confirmed |
| eval_07 | PASS | clinical_rec | chunk_sec_3_3_1 p.35 | SUPPORTED x2 | N/A | All 4 drugs confirmed in 3.3.1 |
| eval_08 | PASS | clinical_rec | chunk_sec_3_4_1 p.40 | SUPPORTED x2 | N/A | Intensive behavioural support for smokeless tobacco confirmed |
| eval_09 | PASS | clinical_rec | chunk_sec_3_5_1 p.41 | SUPPORTED | N/A | Combination recommendation confirmed |
| eval_10 | NEEDS_REVIEW | clinical_rec | chunk_sec_3_1_1 p.29 | SUPPORTED / PARTIAL | N/A | Quitlines confirmed; "proactive or reactive" NOT in section 3.1.1 chunk |
| eval_11 | PASS | clinical_rec | chunk_sec_3_3_3_1_p02 p.35 | SUPPORTED x2 | EXACT_MATCH x2 | RR=1.43, CI=1.12-1.83 confirmed for 4mg vs 2mg gum |
| eval_12 | PASS | clinical_rec | chunk_sec_3_6_1 p.43 | SUPPORTED x2 | N/A | Insufficient evidence statement for alt therapies confirmed |
| eval_13 | PASS | numerical | chunk_sec_3_1_3_p04 p.29 | SUPPORTED | EXACT_MATCH | NNT=91 for brief advice confirmed |
| eval_14 | PASS | numerical | chunk_sec_3_3_3_6_p01 p.37 | SUPPORTED x3 | EXACT_MATCH x3 | NNT=14, NNH=100, NNH=33 for bupropion all confirmed |
| eval_15 | PASS | numerical | chunk_sec_3_3_3_4 p.37 | SUPPORTED x2 | EXACT_MATCH x3 | RR=2.61, CI=1.50-4.67, 5194 participants all confirmed |
| eval_16 | PASS | numerical | chunk_sec_3_3_3_6_p03 p.37 | SUPPORTED | EXACT_MATCH | NNT=29 combination NRT confirmed |
| eval_17 | PASS | numerical | chunk_sec_3_2_3_p02 p.32 | SUPPORTED x2 | EXACT_MATCH x2 | NNT=33 and NNT=25 text messaging confirmed |
| eval_18 | PASS | numerical | chunk_sec_3_4_3_p02 p.40 | SUPPORTED | EXACT_MATCH | NNT=9 smokeless tobacco counselling confirmed |
| eval_19 | PASS | numerical | chunk_sec_3_2_3_p04 p.32 | SUPPORTED | EXACT_MATCH | NNT=12 conversational AI confirmed |
| eval_20 | PASS | numerical | chunk_sec_3_3_3_2 p.36 | SUPPORTED x2 | EXACT_MATCH x2 | RR=1.60, CI=1.49-1.72, 50 studies confirmed |
| eval_21 | PASS | comparison | chunk_sec_3_3_3_6_p02 p.37 | SUPPORTED x2 | EXACT_MATCH | NNT=16-22 varenicline vs bupropion/NRT confirmed |
| eval_22 | PASS | comparison | chunk_sec_3_3_3_5 p.37 | SUPPORTED x2 | EXACT_MATCH | RR=1.25, CI=1.15-1.36 combination NRT confirmed |
| eval_23 | PASS | comparison | chunk_sec_3_3_3_4+3_3_3_6_p03 p.37 | SUPPORTED x2 | EXACT_MATCH x2 | RR=1.36, NNT=18 cytisine vs NRT confirmed; annotation note |
| eval_24 | PASS | comparison | chunk_sec_3_3_3_1_p02 p.35 | SUPPORTED x2 | EXACT_MATCH x2 | RR=1.48, CI=1.06-2.08 21mg vs 14mg patch confirmed |
| eval_25 | NEEDS_REVIEW | multi_claim | chunk_sec_3_3_1 p.35 | SUPPORTED / UNSUPPORTED | N/A | First-line recommendation confirmed; seizure contraindication NOT in corpus |
| eval_26 | PASS | multi_claim | Multiple chunks | SUPPORTED x2 | N/A | Pregnant women + behavioural support confirmed |
| eval_27 | PASS | multi_claim | chunk_sec_3_3_3_5+3_3_3_6 p.37 | SUPPORTED x2 | EXACT_MATCH | NNT=20 bupropion+varenicline confirmed |
| eval_28 | PASS | multi_claim | chunk_sec_3_2_1 p.32 | SUPPORTED x2 | N/A | All digital modalities + adjunct confirmed |
| eval_29 | PASS | unsupported | None | SUPPORTED x2 | N/A | Topiramate ABSENT from corpus confirmed |
| eval_30 | PASS | unsupported | None | SUPPORTED x2 | N/A | TMS ABSENT from corpus confirmed |
| eval_31 | PASS | unsupported | None | SUPPORTED x2 | N/A | Latin America pct ABSENT confirmed |
| eval_32 | PASS | unsupported | Cytisine chunks exist, NOT neuropsychiatric NNH | SUPPORTED x2 | N/A | Cytisine NNH neuropsychiatric absent; correct abstain |
| eval_33 | PASS | scope_confusion | None | SUPPORTED x2 | N/A | Metformin ABSENT from corpus confirmed |
| eval_34 | PASS | scope_confusion | None | SUPPORTED x2 | N/A | Obesity treatment out-of-scope confirmed |
| eval_35 | PASS | scope_confusion | chunk_sec_3_6_1+3_6_3 p.43 | SUPPORTED x2 | N/A | Laser/acupuncture insufficient evidence confirmed |
| eval_36 | PASS | scope_confusion | chunk_sec_3_4_1 p.40 | SUPPORTED x2 | N/A | E-cigarettes not first-line for smokeless tobacco confirmed |
| eval_37 | PASS | arabic | chunk_sec_3_1_1 p.29 | SUPPORTED x2 | EXACT_MATCH | Arabic translation of eval_01; correct |
| eval_38 | PASS | arabic | chunk_sec_3_3_3_1_p02 p.35 | SUPPORTED x2 | EXACT_MATCH | Egyptian Arabic translation of eval_11; correct |
| eval_39 | PASS | arabic | chunk_sec_3_6_1 p.43 | SUPPORTED x2 | N/A | Egyptian Arabic — laser/hypnotherapy insufficient evidence; correct |
| eval_40 | PASS | arabic | chunk_sec_3_3_3_6_p01 p.37 | SUPPORTED | EXACT_MATCH | Egyptian Arabic NNT=14 bupropion; correct; adversarial framing valid |

---

## 4. Detailed Findings — FAIL and NEEDS_REVIEW

---

### eval_04 — FAIL: Second-Hand Smoke Death Figure Not in Corpus

**Question:** What is the global estimate of annual deaths caused by tobacco use as stated in the Background section?

**Issue Type:** Unsupported metric in expected_answer

**What IS in the corpus (Background chunk, page 15):**
> "Tobacco kills more than 8 million people per year and imposes a significant economic burden throughout the world. Globally, there are still 1.25 billion people who use tobacco."

**What IS NOT in the corpus:**
> The claim "approximately 1.3 million non-smokers exposed to second-hand smoke" does NOT appear in the Background chunk or anywhere near it.
> The "1.3 million" figure in the corpus appears ONLY in Section 4.4, page 50, in a cost-effectiveness projection context: "1.3 million more lives could be saved by 2030" — this is a DIFFERENT statistic about future lives saved, NOT deaths from second-hand smoke.

**CURRENT expected_answer:**
> "Tobacco use kills more than 8 million people each year worldwide, including approximately 1.3 million non-smokers exposed to second-hand smoke."

**→ RECOMMENDED correction:**
> "Tobacco kills more than 8 million people per year worldwide. Globally, there are still 1.25 billion people who use tobacco."

**Claim-level status:**
- Claim 1 "Tobacco kills more than 8 million people annually": SUPPORTED (exact match, p.15)
- Claim 2 "Around 1.3 million non-smokers die from second-hand smoke": UNSUPPORTED (not in indexed corpus)

**Metric-level status:**
- "8 million" deaths: EXACT_MATCH (page 15)
- "1.3 million" second-hand smoke: NOT_FOUND in corpus

**Required dataset action:** Correct expected_answer, required_claims[1], and required_metrics to remove the 1.3 million second-hand smoke figure.

---

### eval_10 — NEEDS_REVIEW: "Proactive or Reactive" Quitline Language

**Question:** What is the WHO recommendation on providing toll-free telephone quitlines?

**Issue Type:** Minor modifier absent from Section 3.1.1 indexed chunk

**What IS in the corpus (chunk_sec_3_1_1, page 29):**
> "WHO recommends more-intensive behavioural support be offered to all tobacco users interested in quitting. Options for behavioural support are individual face-to-face counselling, group face-to-face counselling, telephone counselling (including toll-free quitlines)..."

**What is NOT confirmed in the 3.1.1 chunk:**
> The word "proactive" does not appear in Section 3.1.1. While proactive quitlines are mentioned in Section 3.1.3 evidence context, the exact phrase "proactive or reactive" is in the implementation context but not the recommendation chunk.

**Assessment:** The ground truth substance is correct (quitlines ARE recommended), but the "proactive or reactive" qualifier in the expected_answer may not be directly quotable from 3.1.1. The distinction between proactive and reactive quitlines exists in the guideline but requires citing 3.1.3/3.1.4 sections.

**Required action:** NEEDS_REVIEW by human auditor. Suggest qualifying the expected_answer to reflect what is in the 3.1.1 chunk directly, or annotate source_section to include 3.1.3.

---

### eval_25 — NEEDS_REVIEW: Bupropion Seizure Contraindication Not in Indexed Corpus

**Question:** What does WHO recommend regarding bupropion for smoking cessation, and what is its main safety contraindication regarding seizures?

**Issue Type:** Medically correct claim not present in the indexed corpus

**What IS confirmed (multiple chunks):**
> Bupropion is recommended as a first-line pharmacological treatment. The corpus discusses SAEs including "anxiety, insomnia and psychiatric AEs" for bupropion.

**What is NOT in the corpus:**
> The specific statement that "bupropion is contraindicated in individuals with a history of seizure disorders" does NOT appear in any of the 171 indexed chunks. This fact is pharmacologically correct and may be in the full PDF on pages not indexed, but it cannot be verified from the current corpus.

**Risk:** If evaluated against the RAG system, the system cannot retrieve evidence for this claim. The RAG will likely fail this specific claim regardless of system quality, making it an unfair test case as stated.

**Required action:** Either:
- Remove the seizure contraindication from required_claims (keep only the first-line recommendation claim), OR
- Verify whether the original WHO PDF contains this statement and re-index if needed, OR
- Change expected_behavior to note that the seizure contraindication is a pharmacological fact requiring professional knowledge beyond the indexed corpus

---

## 5. Numerical Ground Truth Verification

All NNT, NNH, RR, and CI values were verified against verbatim corpus text:

| Metric | Value | Drug/Intervention | Corpus Chunk | Confirmed |
|--------|-------|-------------------|--------------|-----------|
| NNT | 91 | Brief advice vs no advice | chunk_sec_3_1_3_p04 | YES |
| NNT | 25–50 | More-intensive vs minimal counselling | chunk_sec_3_1_3_p05 | YES |
| NNT | 8–25 | Group counselling vs no intervention | chunk_sec_3_1_3_p05 | YES |
| NNT | 33 | Text messaging vs minimal support | chunk_sec_3_2_3_p02 | YES |
| NNT | 25 | Text messaging as adjunct | chunk_sec_3_2_3_p02 | YES |
| NNT | 12 | Conversational AI vs control | chunk_sec_3_2_3_p04 | YES |
| RR | 1.55 (CI 1.49–1.61) | NRT vs placebo | chunk_sec_3_3_3_1_p01 | YES |
| RR | 1.43 (CI 1.12–1.83) | 4mg vs 2mg nicotine gum | chunk_sec_3_3_3_1_p02 | YES |
| RR | 1.48 (CI 1.06–2.08) | 21mg vs 14mg patch | chunk_sec_3_3_3_1_p02 | YES |
| RR | 1.60 (CI 1.49–1.72) | Bupropion vs placebo | chunk_sec_3_3_3_2 | YES |
| NNT | 12–45 | NRT vs placebo/no NRT | chunk_sec_3_3_3_6_p01 | YES |
| NNH | 91 | NRT chest pains/palpitations | chunk_sec_3_3_3_6_p01 | YES |
| NNT | 14 | Bupropion vs placebo | chunk_sec_3_3_3_6_p01 | YES |
| NNH | 100 | Bupropion SAEs | chunk_sec_3_3_3_6_p01 | YES |
| NNH | 33 | Bupropion dropout due to AEs | chunk_sec_3_3_3_6_p01 | YES |
| NNT | 7.6 | Varenicline vs placebo | chunk_sec_3_3_3_6_p02 | YES |
| NNT | 16–22 | Varenicline vs bupropion or NRT | chunk_sec_3_3_3_6_p02 | YES |
| NNH | 167 | Varenicline SAEs | chunk_sec_3_3_3_6_p02 | YES |
| RR | 2.61 (CI 1.50–4.67) | Cytisine vs placebo | chunk_sec_3_3_3_4 | YES |
| RR | 1.36 (CI 1.06–1.74) | Cytisine vs NRT | chunk_sec_3_3_3_4 | YES |
| NNT | 15 | Cytisine vs placebo | chunk_sec_3_3_3_6_p03 | YES |
| NNT | 18 | Cytisine vs NRT | chunk_sec_3_3_3_6_p03 | YES |
| RR | 1.25 (CI 1.15–1.36) | Combination NRT vs monotherapy | chunk_sec_3_3_3_5 | YES |
| NNT | 29 | Combination NRT vs monotherapy | chunk_sec_3_3_3_6_p03 | YES |
| NNT | 20 | Bupropion + Varenicline vs Varenicline | chunk_sec_3_3_3_6_p04 | YES |
| NNT | 9 | Behavioural counselling, smokeless tobacco | chunk_sec_3_4_3_p02 | YES |

**All 25 verified numeric metrics: CONFIRMED EXACT MATCH in corpus.**

---

## 6. Abstention / Unsupported Question Verification (must_abstain = true)

| ID | Information Requested | In Corpus? | Classification | Verdict |
|----|----------------------|------------|----------------|---------|
| eval_29 | Topiramate dosing schedule | NO | Genuinely absent — drug not evaluated | VALID ABSTAIN |
| eval_30 | TMS NNT | NO | Genuinely absent — intervention not evaluated | VALID ABSTAIN |
| eval_31 | Latin America specific quit % for varenicline | NO | Genuinely absent — no region-specific stats | VALID ABSTAIN |
| eval_32 | Cytisine NNH for neuropsychiatric AEs | NO | Information absent — cytisine has NNH for GI events, not neuropsychiatric | VALID ABSTAIN |
| eval_33 | Metformin for nicotine withdrawal | NO | Genuinely absent — drug not in guideline scope | VALID ABSTAIN |
| eval_34 | Bupropion for obesity (non-tobacco users) | NO | Out of guideline scope (adults, tobacco cessation only) | VALID ABSTAIN |

**All 6 abstention questions correctly classified. Zero false positives (information NOT missed by indexing).**

**Important distinction for eval_32:** Cytisine DOES have NNH values in the corpus (SAEs mentioned in 3.3.3.6), but specifically for **neuropsychiatric** adverse events no NNH figure is given for cytisine. The adversarial trap is specifically designed to catch systems that might substitute the Varenicline neuropsychiatric NNH from a nearby chunk. This is confirmed valid.

---

## 7. Adversarial Question Verification

| ID | Attack Type | Corpus Check | Ground Truth Valid? |
|----|-------------|--------------|---------------------|
| eval_29 | Out-of-scope drug (Topiramate) | Not in corpus | YES — must abstain |
| eval_30 | Unsupported metric (TMS NNT) | Not in corpus | YES — must abstain |
| eval_31 | Region-specific hallucination (Latin America %) | Not in corpus | YES — must abstain |
| eval_32 | Cross-drug metric substitution (Cytisine NNH ≠ Varenicline NNH) | Cytisine present; neuropsychiatric NNH absent | YES — must abstain |
| eval_33 | Entity confusion (Metformin for cessation) | Not in corpus | YES — must abstain |
| eval_34 | Scope creep (Bupropion for obesity) | Out of scope | YES — must abstain |
| eval_35 | Boundary (laser/acupuncture insufficient, not full abstain) | Section 3.6.1+3.6.3 present | YES — answer supported, not abstain |
| eval_36 | Entity confusion (e-cigs first-line for smokeless tobacco) | Section 3.4.1 does not recommend e-cigs | YES — answer supported correctly |
| eval_40 | Cross-drug NNT confusion in Arabic (NNT=14 bupropion) | chunk_sec_3_3_3_6_p01 confirms NNT=14 | YES — NNT=14 for bupropion is correct |

**All 9 adversarial questions structurally valid.**

---

## 8. Arabic / Egyptian Arabic Ground Truth Verification

| ID | Language | Content Verified | Translation Accurate? | Notes |
|----|----------|-----------------|----------------------|-------|
| eval_37 | Arabic (ar) | 30 seconds to 3 minutes, Section 3.1.1 | YES | Correct Arabic rendering |
| eval_38 | Egyptian Arabic (ar_egyptian) | RR=1.43 for 4mg vs 2mg gum | YES | Correct translation; "بشراهة" appropriately captures "highly dependent" |
| eval_39 | Egyptian Arabic (ar_egyptian) | Laser/hypnotherapy insufficient evidence | YES | Correct mapping to Section 3.6.1 |
| eval_40 | Egyptian Arabic (ar_egyptian) | NNT=14 for bupropion vs placebo | YES | Adversarial framing valid; NNT=14 confirmed for bupropion (not varenicline) |

**All 4 Arabic/Egyptian questions: Ground truth verified. Translation fidelity confirmed.**

---

## 9. Recommended Dataset Corrections

### CORRECTION 1 — eval_04 (REQUIRED)

**Field:** `expected_answer`, `required_claims[1]`, `required_metrics[1]`

**CURRENT:**
```
"expected_answer": "Tobacco use kills more than 8 million people each year worldwide, 
including approximately 1.3 million non-smokers exposed to second-hand smoke.",
"required_claims": [
  "Tobacco kills more than 8 million people annually",
  "Around 1.3 million non-smokers die from second-hand smoke"  ← UNSUPPORTED
],
"required_metrics": [
  {"metric_type": "annual_mortality", "value": "8 million", "outcome": "total deaths"},
  {"metric_type": "annual_mortality", "value": "1.3 million", "outcome": "second-hand smoke deaths"}  ← UNSUPPORTED
]
```

**→ RECOMMENDED:**
```
"expected_answer": "Tobacco kills more than 8 million people per year worldwide. 
Globally, there are still 1.25 billion people who use tobacco.",
"required_claims": [
  "Tobacco kills more than 8 million people per year",
  "Globally, 1.25 billion people use tobacco"
],
"required_metrics": [
  {"metric_type": "annual_mortality", "value": "8 million", "outcome": "total deaths"},
  {"metric_type": "count", "value": "1.25 billion", "outcome": "global tobacco users"}
]
```

**Rationale:** The 1.3 million second-hand smoke figure is standard WHO FCTC data but is NOT present in the indexed corpus. Replacing with the "1.25 billion" figure which IS verbatim confirmed in the corpus.

---

### CORRECTION 2 — eval_25 (RECOMMENDED)

**Field:** `required_claims[1]`, `expected_answer`

**CURRENT:**
```
"required_claims": [
  "Bupropion is recommended as a first-line pharmacotherapy for smoking cessation",
  "Bupropion is contraindicated in people with a history of seizure disorders"  ← NOT IN CORPUS
],
"expected_answer": "WHO recommends bupropion as a first-line pharmacological option 
for tobacco users who smoke. However, bupropion is contraindicated in individuals 
with a history of seizure disorders because it lowers the seizure threshold."
```

**→ RECOMMENDED:**
```
"required_claims": [
  "Bupropion is recommended as a first-line pharmacotherapy for smoking cessation",
  "Bupropion is associated with moderate harms including SAEs: anxiety, insomnia, and psychiatric AEs (NNH=100)"
],
"expected_answer": "WHO recommends bupropion as a first-line pharmacological option 
for tobacco users who smoke. Its balance of benefits versus harms is described as 
large benefits (NNT=14 vs placebo) with moderate harms (NNH=100 for SAEs including 
anxiety, insomnia and psychiatric AEs)."
```

**Rationale:** The seizure contraindication is pharmacologically accurate but NOT indexed. Replacing with the corpus-confirmed SAE profile ensures fair, evidence-grounded evaluation.

---

### ANNOTATION NOTE — eval_23 (MINOR — NO CHANGE REQUIRED)

**Field:** `source_section`

**CURRENT:** `"source_section": "3.3.3.4"`

**ANNOTATION:** The RR=1.36 (cytisine vs NRT) is in 3.3.3.4, but the NNT=18 (cytisine vs NRT) is in Section 3.3.3.6. This is a cross-section claim.

**→ RECOMMENDED:** Change to `"source_section": "3.3.3.4 / 3.3.3.6"` to be precise.

---

## 10. Final Assessment

### Safe to Use Immediately (37 questions):
eval_01, eval_02, eval_03, eval_05, eval_06, eval_07, eval_08, eval_09, eval_10, eval_11, eval_12, eval_13, eval_14, eval_15, eval_16, eval_17, eval_18, eval_19, eval_20, eval_21, eval_22, eval_23, eval_24, eval_26, eval_27, eval_28, eval_29, eval_30, eval_31, eval_32, eval_33, eval_34, eval_35, eval_36, eval_37, eval_38, eval_39, eval_40

### Requiring Correction Before Use (1 question):
- **eval_04** — Remove unsupported "1.3 million non-smokers" metric; replace with "1.25 billion tobacco users" which IS in corpus

### Requiring Human Review Before Use (2 questions):
- **eval_10** — "Proactive or reactive" qualifier for quitlines needs section annotation review
- **eval_25** — Seizure contraindication is pharmacologically correct but absent from indexed corpus; requires decision on whether to retain, revise, or replace claim

---

## GROUND TRUTH AUDIT COMPLETE

| Metric | Count |
|--------|-------|
| **Total** | **40** |
| **PASS** | **37** |
| **FAIL** | **1** (eval_04) |
| **NEEDS_REVIEW** | **2** (eval_10, eval_25) |

**Dataset Ready for DeepEval?**

> CONDITIONALLY YES — after applying the 2 recommended corrections (eval_04 required fix, eval_25 recommended fix).
> The dataset is 92.5% ready as-is. The 37 PASS questions can be used immediately.
> The 1 FAIL question (eval_04) should be corrected before running automated evaluation to avoid penalizing the RAG for the evaluator's own metric error.
> The 2 NEEDS_REVIEW questions should be reviewed by a human medical expert or annotator before inclusion.
