# Source-to-Chunk Coverage Audit Report
**Guideline:** WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)
**Audit Verdict:** `FAIL — REQUIRES FULL VERBATIM INGESTION`

## 1. Executive Summary & Coverage Metrics
- **Raw Textual Coverage:** **23.0%** (6,472 words in chunks / 28,137 words in source).
- **Clinical Knowledge Coverage:** **70.4%** (Core recommendations and glossary are 100% intact; evidence and implementation narratives are partially abridged).
- **Block Status Breakdown:** FULL: **21** | PARTIAL: **27** | MISSING: **1** | INTENTIONALLY EXCLUDED: **3**
- **12 Canonical Recommendations Integrity:** **100% VERIFIED** (Exact text, strength, evidence certainty, target population).
- **Glossary Integrity:** **100% VERIFIED** (All 27 terms & definitions extracted verbatim).
- **Graph Relationship Integrity:** **100% VERIFIED** (All related chunk IDs are referentially sound).

## 2. Section-by-Section Coverage Matrix
| Block ID | Section / Document Region | Pages | Status | Severity | Word Coverage | Audit Findings |
|---|---|---|---|---|---|---|
| `FM_01_COVER_COPYRIGHT` | Front Matter: Cover & Copyright | P01-P04 | `FULL` | NONE | 109.2% | Preserved in full. |
| `FM_02_TOC` | Front Matter: Table of Contents | P05-P06 | `FULL` | NONE | 136.6% | Preserved in full. |
| `FM_03_ACK` | Front Matter: Acknowledgements | P07-P07 | `FULL` | NONE | 107.4% | Preserved in full. |
| `FM_04_BLANK_P8` | Front Matter: Blank Page 8 | P08-P08 | `INTENTIONALLY_EXCLUDED` | NONE | 0.0% | Blank page in original PDF layout. |
| `FM_05_ABBR` | Front Matter: Abbreviations and acronyms | P09-P09 | `FULL` | NONE | 150.3% | Preserved in full. |
| `FM_06_BLANK_P10` | Front Matter: Blank Page 10 | P10-P10 | `INTENTIONALLY_EXCLUDED` | NONE | 0.0% | Blank page in original PDF layout. |
| `FM_07_GLOSSARY` | Front Matter: Glossary of terms (27 terms) | P11-P13 | `FULL` | NONE | 105.7% | All 27 terms and definitions extracted verbatim. |
| `FM_08_BLANK_P14` | Front Matter: Blank Page 14 | P14-P14 | `INTENTIONALLY_EXCLUDED` | NONE | 0.0% | Blank page in original PDF layout. |
| `FM_09_EXEC_SUMMARY` | Front Matter: Executive summary | P15-P18 | `PARTIAL` | MEDIUM | 29.6% | Summary recs list preserved; full background paragraphs abridged. |
| `SEC_1_1_EXISTING_GUIDELINES` | 1.1 Existing WHO guidelines | P19-P20 | `PARTIAL` | MEDIUM | 7.9% | Background text summarized into concise paragraph. |
| `SEC_1_2_RATIONALE_OBJECTIVES` | 1.2 Rationale and objectives | P20-P21 | `PARTIAL` | MEDIUM | 14.9% | Objectives summarized into concise paragraph. |
| `SEC_1_3_TARGET_AUDIENCE` | 1.3 Target audience | P21-P22 | `PARTIAL` | MEDIUM | 44.3% | Audience text summarized into concise paragraph. |
| `SEC_2_1_SCOPE_QUESTIONS` | 2.1 Scope of the guideline and questions of interest | P23-P24 | `PARTIAL` | MEDIUM | 4.5% | PICO framework summarized. |
| `SEC_2_2_EVIDENCE_REVIEWS` | 2.2 Evidence reviews | P24-P25 | `PARTIAL` | MEDIUM | 4.9% | Review methodology summarized. |
| `SEC_2_3_ASSESSMENT_GRADING` | 2.3 Assessment of evidence & Table 1 | P26-P26 | `FULL` | NONE | 29.5% | Table 1 GRADE criteria preserved in full Markdown. |
| `SEC_2_4_EVIDENCE_TO_RECS` | 2.4 Going from evidence to recommendations & Table 2 | P26-P28 | `FULL` | NONE | 40.4% | Table 2 Strength implications preserved in full Markdown. |
| `SEC_3_1_1_RECS_1_2` | 3.1.1 Recommendations (Rec 1 & Rec 2) | P29-P29 | `FULL` | NONE | 39.0% | Verbatim text, strength, evidence certainty, and provenance verified 100%. |
| `SEC_3_1_2_QUESTIONS` | 3.1.2 Overall questions | P29-P29 | `FULL` | NONE | 39.0% | Clinical questions preserved. |
| `SEC_3_1_3_EVIDENCE` | 3.1.3 Justification and evidence (Behavioural) | P29-P31 | `PARTIAL` | HIGH | 16.8% | Primary pooled effect sizes preserved, but extended subgroup trial narratives omitted. |
| `SEC_3_1_4_IMPLEMENTATION` | 3.1.4 Implementation considerations (Behavioural) | P31-P32 | `PARTIAL` | HIGH | 30.3% | Core bullet points preserved, but full narrative paragraphs abridged. |
| `SEC_3_2_1_REC_3` | 3.2.1 Recommendation (Rec 3: Digital) | P32-P32 | `FULL` | NONE | 43.5% | Verbatim text, strength, evidence certainty verified 100%. |
| `SEC_3_2_2_QUESTIONS` | 3.2.2 Overall questions | P32-P32 | `FULL` | NONE | 43.5% | Clinical questions preserved. |
| `SEC_3_2_3_EVIDENCE` | 3.2.3 Justification and evidence (Digital) | P32-P34 | `PARTIAL` | HIGH | 18.3% | Main trial stats preserved, but full Cochrane study details omitted. |
| `SEC_3_2_4_IMPLEMENTATION` | 3.2.4 Implementation considerations (Digital) | P34-P34 | `PARTIAL` | HIGH | 27.7% | Core bullet points preserved, full text abridged. |
| `SEC_3_3_1_RECS_4_5` | 3.3.1 Recommendations (Rec 4 & Rec 5: Pharmacotherapy) | P35-P35 | `FULL` | NONE | 29.3% | Verbatim text, strength, certainty for all 4 drugs and combinations verified 100%. |
| `SEC_3_3_2_QUESTIONS` | 3.3.2 Overall questions | P35-P35 | `FULL` | NONE | 29.3% | Clinical questions preserved. |
| `SEC_3_3_3_EVIDENCE_PHARMA` | 3.3.3 Justification and evidence (Pharmacotherapy 3.3.3.1-3.3.3.6) | P35-P38 | `PARTIAL` | HIGH | 14.4% | Drug-by-drug pooled RRs preserved, but extended trial analyses and dosage comparisons (Patch 21mg vs 14mg) omitted. |
| `SEC_3_3_4_IMPLEMENTATION` | 3.3.4 Implementation consideration (Pharmacotherapy) | P39-P39 | `PARTIAL` | HIGH | 15.1% | Core bullet points preserved, full clinical considerations text abridged. |
| `SEC_3_4_1_RECS_6_7` | 3.4.1 Recommendations (Rec 6 & Rec 7: Smokeless) | P40-P40 | `FULL` | NONE | 25.3% | Verbatim text and metadata verified 100%. |
| `SEC_3_4_2_QUESTIONS` | 3.4.2 Overall questions | P40-P40 | `FULL` | NONE | 25.3% | Clinical questions preserved. |
| `SEC_3_4_3_EVIDENCE` | 3.4.3 Justification and evidence (Smokeless) | P40-P41 | `PARTIAL` | HIGH | 26.1% | Main trial stats preserved, extended discussion omitted. |
| `SEC_3_4_4_IMPLEMENTATION` | 3.4.4 Implementation considerations (Smokeless) | P41-P41 | `PARTIAL` | HIGH | 37.9% | Core bullets preserved, extended discussion abridged. |
| `SEC_3_5_1_REC_8` | 3.5.1 Recommendation (Rec 8: Combined) | P41-P41 | `FULL` | NONE | 37.9% | Verbatim text and metadata verified 100%. |
| `SEC_3_5_2_QUESTIONS` | 3.5.2 Overall questions | P41-P41 | `FULL` | NONE | 37.9% | Clinical questions preserved. |
| `SEC_3_5_3_EVIDENCE` | 3.5.3 Justification and evidence (Combined) | P41-P42 | `PARTIAL` | HIGH | 23.3% | Cochrane pooled RR preserved, detailed setting analysis abridged. |
| `SEC_3_5_4_IMPLEMENTATION` | 3.5.4 Implementation considerations (Combined) | P42-P42 | `PARTIAL` | HIGH | 18.7% | Core bullets preserved, full text abridged. |
| `SEC_3_6_1_REC_9` | 3.6.1 Statement (Rec 9 / Statement: Alternative) | P43-P43 | `FULL` | NONE | 22.3% | Verbatim text and metadata verified 100%. |
| `SEC_3_6_2_QUESTIONS` | 3.6.2 Overall questions | P43-P43 | `FULL` | NONE | 22.3% | Clinical questions preserved. |
| `SEC_3_6_3_EVIDENCE` | 3.6.3 Justification and evidence (Alternative) | P43-P44 | `PARTIAL` | HIGH | 28.0% | Summary of review conclusions preserved, specific therapy reviews abridged. |
| `SEC_3_6_4_IMPLEMENTATION` | 3.6.4 Implementation considerations (Alternative) | P43-P44 | `PARTIAL` | HIGH | 28.0% | Core guidance preserved, full text abridged. |
| `SEC_3_7_1_RECS_10_11_12` | 3.7.1 Recommendations (Rec 10, 11, 12: System-level) | P44-P44 | `FULL` | NONE | 38.9% | Verbatim text and metadata verified 100%. |
| `SEC_3_7_2_QUESTIONS` | 3.7.2 Overall questions | P44-P44 | `FULL` | NONE | 38.9% | Clinical questions preserved. |
| `SEC_3_7_3_EVIDENCE` | 3.7.3 Justification and evidence (System-level) | P44-P46 | `PARTIAL` | HIGH | 15.7% | Main OR stats preserved, but extensive Cochrane system reviews abridged. |
| `SEC_3_7_4_IMPLEMENTATION` | 3.7.4 Implementation considerations (3.7.4.1-3.7.4.3) | P46-P47 | `PARTIAL` | HIGH | 22.6% | Subsections isolated, but extended narrative guidance abridged. |
| `SEC_3_8_OVERARCHING` | 3.8 Overarching guideline implementation considerations | P47-P48 | `PARTIAL` | HIGH | 15.9% | High-level bullet points preserved, full policy considerations text abridged. |
| `SEC_4_EVIDENCE_TO_RECS` | 4. Evidence to recommendations (4.1-4.5) | P49-P51 | `PARTIAL` | MEDIUM | 7.9% | Core conclusions preserved, full EtD narrative text abridged. |
| `SEC_5_RESEARCH_NEEDS` | 5. Research needs | P52-P53 | `PARTIAL` | MEDIUM | 10.7% | Bullet points preserved, full narrative abridged. |
| `SEC_6_ADOPTION_DISSEMINATION` | 6. Adoption, dissemination, implementation and evaluation | P54-P54 | `PARTIAL` | MEDIUM | 9.1% | Abridged to single summary paragraph. |
| `SEC_REFERENCES` | References (Main Guidelines) | P55-P59 | `MISSING` | MEDIUM | 1.3% | 5 pages of individual citations represented in 1 sentence. |
| `ANNEX_1_MANAGEMENT` | Annex 1: Management of guideline development process | P60-P64 | `PARTIAL` | LOW | 1.8% | Summary paragraph preserved; full member tables not extracted row-by-row. |
| `ANNEX_2_IMPLEMENTATION_INFO` | Annex 2: Additional information for implementing recommendations | P65-P69 | `PARTIAL` | HIGH | 12.3% | Subsections isolated, but 5 pages of detailed operational text abridged into 5 brief chunks. |
| `ANNEX_3_DOI` | Annex 3: Summary of declarations of interest | P70-P76 | `PARTIAL` | LOW | 6.5% | Summary paragraph preserved; full tables not extracted row-by-row. |

## 3. Critical Missing Content Analysis
### High Severity (Clinical Evidence & Implementation Guidance)
1. **Detailed Systematic Review Evidence Narratives (Sections 3.1.3 to 3.7.3):** Primary pooled effect sizes are present, but extended subgroup analyses, dosing comparisons (Patch 21mg vs 14mg), and specific trial citations were omitted.
2. **Extended Implementation Guidance & Annex 2 (Section 3.X.4 & Annex 2):** 5 pages of rich clinical guidance (adolescents, psychiatric comorbidities, varenicline/cytisine titration protocols, and financial barrier mitigation) were abridged into concise summary chunks.

### Medium Severity (Background, Methods & References)
1. **Full Narrative Text of Sections 1, 2, 4, 5, 6:** Background and EtD discussions were preserved as summaries rather than full verbatim paragraphs.
2. **References Section (Pages 55-59):** 5 pages of bibliographic references were condensed into a single description.

## 4. Key Takeaways & Recommendations
1. **Is the 23% finding valid?** Yes, exactly **23.0%** of raw source words are preserved in chunks.
2. **What is genuinely intact?** 100% of the 12 canonical recommendations, 100% of the 27 glossary terms, and GRADE Tables 1 & 2.
3. **Does the chunker need correction?** Yes. The architecture, metadata schema, breadcrumbs, and graph linking are production-ready, but the text ingestion engine in `semantic_chunker.py` must be upgraded to perform full verbatim paragraph ingestion across all 76 pages.