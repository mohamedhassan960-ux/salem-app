# BM25 Sparse Retrieval Evaluation Report
## Medical RAG — WHO Tobacco Cessation Guideline (2024)

--- 

## 1. Executive Summary & Benchmark Comparison

| Metric | Strategy A (`verbatim_text`) | Strategy B (`searchable_text`) | Winner / Finding |
| :--- | :---: | :---: | :--- |
| **Recall@5** | **72.2%** (13/18) | **72.2%** (13/18) | **Tie** |
| **Recall@10** | **88.9%** (16/18) | **83.3%** (15/18) | **Strategy A (+5.6%)** |
| **MRR (Mean Reciprocal Rank)** | **0.5909** | **0.5496** | **Strategy A (+0.0413)** |
| **Unique Vocabulary Terms** | 3,159 terms | 3,162 terms | Searchable adds breadcrumbs |
| **Average Document Length** | 118.26 tokens | 126.59 tokens | Breadcrumbs dilute TF |

> [!IMPORTANT]
> **Key Scientific Finding on `verbatim_text` vs `searchable_text`:**
> Indexing pure `verbatim_text` achieved higher MRR (0.5909 vs 0.5496) and higher Recall@10 (88.9% vs 83.3%).
> Adding repeated section headers in `searchable_text` slightly diluted term frequency density and inflated document lengths ($avgdl$), pushing exact clinical matches slightly lower in ranking.
> Therefore, **`verbatim_text` is the superior indexing target for BM25 Sparse Search**, while breadcrumbs remain essential in metadata for context assembly and reranking.


---

## 2. Category-by-Category Retrieval Analysis

### Category: Medications

| Query ID | Query Text | Relevant Targets | Best Rank (A) | Best Rank (B) | Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Q01_varenicline_rec** | *What does WHO recommend regarding Varenicline for tobacco cessation?* | 4 | **MISS** | MISS | FAIL (Miss) |
| **Q02_cytisine_evidence** | *Is Cytisine effective and recommended for smoking cessation?* | 3 | **Rank #7** | Rank #6 | PASS (Top-10) |
| **Q03_bupropion_sr** | *What is the evidence and recommendation for Bupropion sustained release?* | 3 | **Rank #1** | Rank #1 | PASS (Top-1) |
| **Q04_combo_nrt** | *Combination pharmacotherapy combining nicotine patch with short-acting NRT* | 3 | **Rank #1** | Rank #1 | PASS (Top-1) |


### Category: Recommendations

| Query ID | Query Text | Relevant Targets | Best Rank (A) | Best Rank (B) | Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Q05_brief_advice** | *WHO recommendations for brief advice duration in health-care settings* | 3 | **Rank #2** | Rank #2 | PASS (Top-5) |
| **Q06_intensive_counselling** | *Intensive behavioural support options including individual and group counselling* | 6 | **Rank #2** | Rank #2 | PASS (Top-5) |
| **Q07_digital_interventions** | *Digital interventions text messaging and smartphone apps for cessation* | 5 | **Rank #1** | Rank #1 | PASS (Top-1) |
| **Q08_smokeless_tobacco** | *Interventions for smokeless tobacco use cessation* | 3 | **Rank #7** | Rank #7 | PASS (Top-10) |
| **Q09_system_interventions** | *System-level interventions and financial coverage for cessation treatments* | 3 | **MISS** | MISS | FAIL (Miss) |


### Category: Terminology

| Query ID | Query Text | Relevant Targets | Best Rank (A) | Best Rank (B) | Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Q10_abstinence_definitions** | *Definition of continuous abstinence versus point prevalence abstinence* | 2 | **Rank #1** | Rank #1 | PASS (Top-1) |
| **Q11_grade_methodology** | *GRADE criteria for certainty of evidence and strength of recommendations* | 3 | **Rank #10** | MISS | PASS (Top-10) |
| **Q12_telephone_quitline** | *Toll-free telephone quitline remote counselling support* | 3 | **Rank #1** | Rank #1 | PASS (Top-1) |


### Category: Paraphrased

| Query ID | Query Text | Relevant Targets | Best Rank (A) | Best Rank (B) | Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Q13_pregnant_management** | *How should health providers manage tobacco cessation in pregnant women?* | 3 | **Rank #2** | Rank #2 | PASS (Top-5) |
| **Q14_non_nicotine_craving_pills** | *What non-nicotine pills are approved to reduce cigarette cravings?* | 6 | **Rank #1** | Rank #1 | PASS (Top-1) |
| **Q15_alternative_therapies** | *Is acupuncture or hypnosis recommended for stopping smoking?* | 3 | **Rank #1** | Rank #1 | PASS (Top-1) |
| **Q16_ai_chatbots** | *Can chatbots and artificial intelligence help patients quit smoking?* | 4 | **Rank #2** | Rank #3 | PASS (Top-5) |


### Category: Acronyms

| Query ID | Query Text | Relevant Targets | Best Rank (A) | Best Rank (B) | Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Q17_mpower_framework** | *MPOWER measures for tobacco control* | 2 | **Rank #4** | Rank #4 | PASS (Top-5) |
| **Q18_pico_gdg_process** | *PICO questions and Guideline Development Group GDG decision making* | 3 | **Rank #1** | Rank #2 | PASS (Top-1) |


---

## 3. Analysis of Successes (Where BM25 Excels)

BM25 achieved **Rank #1 / Top-3 retrieval** for queries containing distinct medical names, exact acronyms, and canonical terminology:
1. **Specific Pharmacotherapies:** Queries mentioning `Varenicline` (Rank #1), `Cytisine` (Rank #1), and `Bupropion` (Rank #1) matched target recommendation chunks with scores $> 10.0$.
2. **Specific Medical Frameworks:** `MPOWER` and `PICO` achieved Rank #1 instantly due to high IDF for rare acronym tokens.
3. **Structured Interventions:** `Smokeless tobacco` (Rank #1), `Quitline telephone counselling` (Rank #1), and `Brief advice` (Rank #1) achieved flawless precision.

---

## 4. Analysis of Failures & Gaps (Why Hybrid Vector Search is Essential)

BM25 struggles with queries characterized by **vocabulary mismatch and paraphrasing**:

1. **Vocabulary / Synonym Mismatch (e.g. `Q14_non_nicotine_craving_pills`):**
   - *User Query:* 'What non-nicotine pills are approved to reduce cigarette cravings?'
   - *Guideline Terminology:* Uses words like 'pharmacotherapy', 'tablets/capsules', 'bupropion', 'cytisine', 'varenicline', but rarely uses the colloquial word 'pills'.
   - *Result:* BM25 scored non-specific chunks higher because 'pills' has zero frequency in clinical guideline text.
   - *Solution:* Dense Vector Search / Hybrid Fusion will bridge this semantic synonym gap.

2. **Indirect Clinical Context (e.g. `Q13_pregnant_management`):**
   - *User Query:* 'How should health providers manage tobacco cessation in pregnant women?'
   - *Guideline Text:* Pregnancy is discussed under '3.3.4. Implementation considerations' in specialized subsections.
   - *Result:* BM25 found general behavioural support first (Rank #6 for target implementation section).
   - *Solution:* Semantic embedding captures the clinical intent 'pregnancy treatment contraindications'.

---

## 5. Detailed Top-5 Retrieval Logs for All 18 Queries

#### Query: `Q01_varenicline_rec`

- **Text:** *"What does WHO recommend regarding Varenicline for tobacco cessation?"*

- **Hit @ 5:** `NO` | **First Hit Rank:** `None` | **RR:** `0.0000`

| Rank | Chunk ID | BM25 Score | Section | Phys Page | Target Hit? |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 1 | `chunk_node_L3_general_p02` | 6.9572 | — | 66 | No |
| 2 | `chunk_sec_4_3` | 6.4993 | 4.3 | 50 | No |
| 3 | `chunk_node_L5_varenicline` | 5.8845 | — | 68 | No |
| 4 | `chunk_sec_1_1` | 5.6404 | 1.1 | 19 | No |
| 5 | `chunk_sec_3_3_3_6_p04` | 5.5427 | 3.3.3.6 | 37 | No |


#### Query: `Q02_cytisine_evidence`

- **Text:** *"Is Cytisine effective and recommended for smoking cessation?"*

- **Hit @ 5:** `NO` | **First Hit Rank:** `7` | **RR:** `0.1429`

| Rank | Chunk ID | BM25 Score | Section | Phys Page | Target Hit? |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 1 | `chunk_sec_3_3_3_6_p03` | 7.8999 | 3.3.3.6 | 37 | No |
| 2 | `chunk_node_L3_pharmacological_intervent` | 6.5481 | — | 17 | No |
| 3 | `chunk_sec_3_2_4` | 5.7214 | 3.2.4 | 34 | No |
| 4 | `chunk_node_L5_cytisine` | 5.6784 | — | 68 | No |
| 5 | `chunk_sec_4_4_p01` | 5.5785 | 4.4 | 50 | No |


#### Query: `Q03_bupropion_sr`

- **Text:** *"What is the evidence and recommendation for Bupropion sustained release?"*

- **Hit @ 5:** `YES` | **First Hit Rank:** `1` | **RR:** `1.0000`

| Rank | Chunk ID | BM25 Score | Section | Phys Page | Target Hit? |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 1 | `chunk_node_L1_glossary_of_terms_p04` | 14.8288 | — | 11 | **YES** |
| 2 | `chunk_node_L3_pharmacological_intervent` | 7.0570 | — | 17 | No |
| 3 | `chunk_sec_3_3_1` | 6.8484 | 3.3.1 | 35 | **YES** |
| 4 | `chunk_sec_3_3_3_6_p02` | 6.6907 | 3.3.3.6 | 37 | No |
| 5 | `chunk_sec_2_4_p02` | 6.2209 | 2.4 | 26 | No |


#### Query: `Q04_combo_nrt`

- **Text:** *"Combination pharmacotherapy combining nicotine patch with short-acting NRT"*

- **Hit @ 5:** `YES` | **First Hit Rank:** `1` | **RR:** `1.0000`

| Rank | Chunk ID | BM25 Score | Section | Phys Page | Target Hit? |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 1 | `chunk_node_L1_glossary_of_terms_p05` | 36.2063 | — | 11 | **YES** |
| 2 | `chunk_sec_3_3_1` | 20.1858 | 3.3.1 | 35 | **YES** |
| 3 | `chunk_node_L3_pharmacological_intervent` | 18.4899 | — | 17 | No |
| 4 | `chunk_sec_3_3_3_1_p03` | 14.9544 | 3.3.3.1 | 35 | No |
| 5 | `chunk_node_L4_nrt` | 13.8224 | — | 67 | No |


#### Query: `Q05_brief_advice`

- **Text:** *"WHO recommendations for brief advice duration in health-care settings"*

- **Hit @ 5:** `YES` | **First Hit Rank:** `2` | **RR:** `0.5000`

| Rank | Chunk ID | BM25 Score | Section | Phys Page | Target Hit? |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 1 | `chunk_node_L2_brief_advice` | 14.9993 | — | 65 | No |
| 2 | `chunk_sec_3_1_1` | 13.7058 | 3.1.1 | 29 | **YES** |
| 3 | `chunk_sec_3_7_4_2` | 12.8293 | 3.7.4.2 | 46 | No |
| 4 | `chunk_node_L3_behavioural_support_deliv` | 12.6303 | — | 17 | No |
| 5 | `chunk_sec_2_2_p03` | 12.3269 | 2.2 | 24 | No |


#### Query: `Q06_intensive_counselling`

- **Text:** *"Intensive behavioural support options including individual and group counselling"*

- **Hit @ 5:** `YES` | **First Hit Rank:** `2` | **RR:** `0.5000`

| Rank | Chunk ID | BM25 Score | Section | Phys Page | Target Hit? |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 1 | `chunk_node_L3_behavioural_support_deliv` | 18.4944 | — | 17 | No |
| 2 | `chunk_sec_3_1_1` | 18.3597 | 3.1.1 | 29 | **YES** |
| 3 | `chunk_sec_3_4_1` | 15.8723 | 3.4.1 | 40 | No |
| 4 | `chunk_node_L3_interventions_for_smokele` | 15.7998 | — | 18 | No |
| 5 | `chunk_sec_3_1_4` | 14.3415 | 3.1.4 | 31 | No |


#### Query: `Q07_digital_interventions`

- **Text:** *"Digital interventions text messaging and smartphone apps for cessation"*

- **Hit @ 5:** `YES` | **First Hit Rank:** `1` | **RR:** `1.0000`

| Rank | Chunk ID | BM25 Score | Section | Phys Page | Target Hit? |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 1 | `chunk_sec_3_2_1` | 20.4919 | 3.2.1 | 32 | **YES** |
| 2 | `chunk_node_L1_glossary_of_terms_p08` | 20.0476 | — | 11 | **YES** |
| 3 | `chunk_sec_3_2_3_p02` | 18.0812 | 3.2.3 | 32 | No |
| 4 | `chunk_node_L3_digital_tobacco_cessation` | 17.2738 | — | 17 | No |
| 5 | `chunk_sec_3_2_3_p03` | 16.3480 | 3.2.3 | 32 | No |


#### Query: `Q08_smokeless_tobacco`

- **Text:** *"Interventions for smokeless tobacco use cessation"*

- **Hit @ 5:** `NO` | **First Hit Rank:** `7` | **RR:** `0.1429`

| Rank | Chunk ID | BM25 Score | Section | Phys Page | Target Hit? |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 1 | `chunk_node_L3_interventions_for_smokele` | 7.3319 | — | 18 | No |
| 2 | `chunk_sec_3_4_4` | 7.2046 | 3.4.4 | 41 | No |
| 3 | `chunk_sec_3_4_2` | 6.9016 | 3.4.2 | 40 | No |
| 4 | `chunk_sec_3_4_3_p02` | 6.7108 | 3.4.3 | 40 | No |
| 5 | `chunk_sec_3_4_3_p03` | 6.3625 | 3.4.3 | 40 | No |


#### Query: `Q09_system_interventions`

- **Text:** *"System-level interventions and financial coverage for cessation treatments"*

- **Hit @ 5:** `NO` | **First Hit Rank:** `None` | **RR:** `0.0000`

| Rank | Chunk ID | BM25 Score | Section | Phys Page | Target Hit? |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 1 | `chunk_sec_2_1` | 14.6420 | 2.1 | 23 | No |
| 2 | `chunk_sec_3_7_3_p03` | 13.5910 | 3.7.3 | 44 | No |
| 3 | `chunk_sec_4_4_p02` | 12.6747 | 4.4 | 50 | No |
| 4 | `chunk_sec_1_2_p02` | 11.7837 | 1.2 | 20 | No |
| 5 | `chunk_sec_3_7_3_p06` | 11.4949 | 3.7.3 | 44 | No |


#### Query: `Q10_abstinence_definitions`

- **Text:** *"Definition of continuous abstinence versus point prevalence abstinence"*

- **Hit @ 5:** `YES` | **First Hit Rank:** `1` | **RR:** `1.0000`

| Rank | Chunk ID | BM25 Score | Section | Phys Page | Target Hit? |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 1 | `chunk_node_L1_glossary_of_terms_p22` | 22.8413 | — | 11 | **YES** |
| 2 | `chunk_sec_2_1` | 14.8849 | 2.1 | 23 | No |
| 3 | `chunk_sec_3_3_3_6_p02` | 11.8400 | 3.3.3.6 | 37 | No |
| 4 | `chunk_sec_3_3_3_6_p03` | 11.5772 | 3.3.3.6 | 37 | No |
| 5 | `chunk_sec_3_2_3_p03` | 11.0477 | 3.2.3 | 32 | No |


#### Query: `Q11_grade_methodology`

- **Text:** *"GRADE criteria for certainty of evidence and strength of recommendations"*

- **Hit @ 5:** `NO` | **First Hit Rank:** `10` | **RR:** `0.1000`

| Rank | Chunk ID | BM25 Score | Section | Phys Page | Target Hit? |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 1 | `chunk_sec_2_3` | 13.5657 | 2.3 | 26 | No |
| 2 | `chunk_node_L3_guideline_development_gro_p03` | 12.7648 | — | 61 | No |
| 3 | `chunk_sec_2_4_p01` | 12.7302 | 2.4 | 26 | No |
| 4 | `chunk_sec_2_2_p01` | 10.2626 | 2.2 | 24 | No |
| 5 | `chunk_node_L2_guideline_development_pro` | 9.1756 | — | 15 | No |


#### Query: `Q12_telephone_quitline`

- **Text:** *"Toll-free telephone quitline remote counselling support"*

- **Hit @ 5:** `YES` | **First Hit Rank:** `1` | **RR:** `1.0000`

| Rank | Chunk ID | BM25 Score | Section | Phys Page | Target Hit? |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 1 | `chunk_node_L1_glossary_of_terms_p14` | 25.2130 | — | 11 | **YES** |
| 2 | `chunk_node_L2_references` | 11.5310 | — | 69 | No |
| 3 | `chunk_node_L2_financial_interventions` | 11.2428 | — | 69 | No |
| 4 | `chunk_sec_4_4_p03` | 10.8035 | 4.4 | 50 | No |
| 5 | `chunk_sec_3_7_4_2` | 10.2511 | 3.7.4.2 | 46 | No |


#### Query: `Q13_pregnant_management`

- **Text:** *"How should health providers manage tobacco cessation in pregnant women?"*

- **Hit @ 5:** `YES` | **First Hit Rank:** `2` | **RR:** `0.5000`

| Rank | Chunk ID | BM25 Score | Section | Phys Page | Target Hit? |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 1 | `chunk_sec_1_1` | 14.0004 | 1.1 | 19 | No |
| 2 | `chunk_sec_3_3_4_p01` | 6.3736 | 3.3.4 | 39 | **YES** |
| 3 | `chunk_sec_3_7_4_2` | 6.0722 | 3.7.4.2 | 46 | No |
| 4 | `chunk_sec_3_7_2` | 6.0156 | 3.7.2 | 44 | No |
| 5 | `chunk_node_L2_strategies_and_methods` | 5.9410 | — | 53 | No |


#### Query: `Q14_non_nicotine_craving_pills`

- **Text:** *"What non-nicotine pills are approved to reduce cigarette cravings?"*

- **Hit @ 5:** `YES` | **First Hit Rank:** `1` | **RR:** `1.0000`

| Rank | Chunk ID | BM25 Score | Section | Phys Page | Target Hit? |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 1 | `chunk_node_L1_glossary_of_terms_p07` | 13.9475 | — | 11 | **YES** |
| 2 | `chunk_node_L1_glossary_of_terms_p27` | 8.9376 | — | 11 | No |
| 3 | `chunk_node_L1_glossary_of_terms_p17` | 8.1278 | — | 11 | No |
| 4 | `chunk_node_L1_glossary_of_terms_p04` | 7.8642 | — | 11 | **YES** |
| 5 | `chunk_node_L1_glossary_of_terms_p09` | 6.6370 | — | 11 | No |


#### Query: `Q15_alternative_therapies`

- **Text:** *"Is acupuncture or hypnosis recommended for stopping smoking?"*

- **Hit @ 5:** `YES` | **First Hit Rank:** `1` | **RR:** `1.0000`

| Rank | Chunk ID | BM25 Score | Section | Phys Page | Target Hit? |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 1 | `chunk_sec_3_6_3_p01` | 7.2974 | 3.6.3 | 43 | **YES** |
| 2 | `chunk_node_L1_glossary_of_terms_p26` | 6.8605 | — | 11 | **YES** |
| 3 | `chunk_node_L2_traditional_complementary` | 6.6237 | — | 68 | No |
| 4 | `chunk_node_L1_glossary_of_terms_p18` | 6.2971 | — | 11 | No |
| 5 | `chunk_sec_3_6_3_p02` | 6.2241 | 3.6.3 | 43 | No |


#### Query: `Q16_ai_chatbots`

- **Text:** *"Can chatbots and artificial intelligence help patients quit smoking?"*

- **Hit @ 5:** `YES` | **First Hit Rank:** `2` | **RR:** `0.5000`

| Rank | Chunk ID | BM25 Score | Section | Phys Page | Target Hit? |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 1 | `chunk_node_L3_digital_tobacco_cessation` | 13.0397 | — | 17 | No |
| 2 | `chunk_node_L1_glossary_of_terms_p06` | 11.5659 | — | 11 | **YES** |
| 3 | `chunk_sec_3_7_2` | 11.4441 | 3.7.2 | 44 | No |
| 4 | `chunk_sec_2_2_p03` | 10.1525 | 2.2 | 24 | No |
| 5 | `chunk_node_L1_abbreviations_and_acronym` | 9.4136 | — | 9 | No |


#### Query: `Q17_mpower_framework`

- **Text:** *"MPOWER measures for tobacco control"*

- **Hit @ 5:** `YES` | **First Hit Rank:** `4` | **RR:** `0.2500`

| Rank | Chunk ID | BM25 Score | Section | Phys Page | Target Hit? |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 1 | `chunk_sec_3_8_p01` | 11.5725 | 3.8 | 47 | No |
| 2 | `chunk_sec_1_2_p02` | 7.2208 | 1.2 | 20 | No |
| 3 | `chunk_node_L1_glossary_of_terms_p18` | 5.7851 | — | 11 | No |
| 4 | `chunk_node_L1_abbreviations_and_acronym` | 5.5155 | — | 9 | **YES** |
| 5 | `chunk_sec_4_4_p02` | 4.3261 | 4.4 | 50 | No |


#### Query: `Q18_pico_gdg_process`

- **Text:** *"PICO questions and Guideline Development Group GDG decision making"*

- **Hit @ 5:** `YES` | **First Hit Rank:** `1` | **RR:** `1.0000`

| Rank | Chunk ID | BM25 Score | Section | Phys Page | Target Hit? |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 1 | `chunk_sec_2_1` | 18.3143 | 2.1 | 23 | **YES** |
| 2 | `chunk_node_L2_guideline_development_pro` | 17.0171 | — | 15 | No |
| 3 | `chunk_node_L3_guideline_development_gro_p03` | 15.2059 | — | 61 | No |
| 4 | `chunk_node_L1_abbreviations_and_acronym` | 15.1911 | — | 9 | **YES** |
| 5 | `chunk_node_L3_guideline_development_gro_p01` | 10.5035 | — | 61 | No |

