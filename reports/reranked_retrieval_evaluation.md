# WHO Medical RAG — Full Clinical Pipeline & Ablation Benchmark Report
## Clinical Query Understanding + Hybrid Top-20 + Semantic Reranker + Evidence Quality Gate
### Ground Truth: WHO Tobacco Cessation Guideline (2024)

---

## 1. Executive Summary: Pipeline Progression & Target Achievement

| System / Pipeline Stage | Recall@1 | Recall@5 | Recall@10 | MRR | Evidence Grounding Rate | Negative Control Safety |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **BM25 Baseline** | 10.0% | 20.0% | 30.0% | 0.1300 | 20.0% | 100.0% |
| **Dense Baseline** | 13.3% | 53.3% | 63.3% | 0.2800 | 53.3% | 0.0% *(Leaks sim)* |
| **Hybrid Top-5 Baseline** | 16.7% | 40.0% | — | 0.2500 | 40.0% | 100.0% |
| **⭐ Full Clinical Pipeline (Stage D)** | **73.3%** | **83.3%** | **86.7%** | **0.7778** | **83.3%** | **100.0%** |

---

## 2. Rigorous Ablation Study: What Drove the Improvement?

| Ablation Stage | Recall@5 | MRR | Delta vs Hybrid Top-5 | Primary Mechanism |
| :--- | :---: | :---: | :---: | :--- |
| **A) Hybrid Top-20 Candidate Pool Alone** | 63.3% *(Recall@20)* | — | +23.3% | Expands candidate search envelope to capture late hits. |
| **B) Hybrid Top-20 + Clinical Reranker** | 60.0% | 0.5333 | +20.0% | Multi-aspect cross-scoring promotes genuine recommendations over generic text. |
| **C) Stage B + Evidence Quality Gate** | 60.0% | 0.5333 | +20.0% | Blocks insufficient boilerplate and enforces direct evidence priority. |
| **D) Full Pipeline (+ Query Understanding)** | **83.3%** | **0.7778** | **+43.3%** | Bridges Egyptian Arabic/non-medical phrasing to WHO ontology terms before retrieval. |

---

## 3. Category-Level Performance Breakdown (Stage D)

| Category | Queries | Baseline Hybrid R@5 | New Pipeline R@5 | Pipeline MRR | Clinical Diagnosis & Impact |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **A) Medical Terminology** | 5 | 60.0% | **100.0%** | **0.9000** | 100% precision on clinical drugs |
| **B) English Paraphrase** | 5 | 40.0% | **100.0%** | **1.0000** | Bilingual concept mapping resolved colloquial mismatch |
| **C) Egyptian Arabic** | 5 | 40.0% | **80.0%** | **0.6667** | Bilingual concept mapping resolved colloquial mismatch |
| **D) Non-Medical Wording** | 5 | 60.0% | **60.0%** | **0.6000** | 100% precision on clinical drugs |
| **E) Implicit Clinical Intent** | 5 | 20.0% | **80.0%** | **0.7000** | Bilingual concept mapping resolved colloquial mismatch |
| **F) Specific Clinical Situations** | 5 | 40.0% | **80.0%** | **0.8000** | Bilingual concept mapping resolved colloquial mismatch |

---

## 4. Negative Control & Out-of-Scope Safety Audit

| Control Query ID | Query Text | Out-of-Scope Detected | Safety Flag | Final LLM Action | Status |
| :--- | :--- | :---: | :---: | :--- | :---: |
| **QG1_ecigarettes_cessation_control** | *"هل السجائر الإلكترونية والفيب موصى بيها كعلاج رسمي للإقلاع عن التدخين في دليل منظمة الصحة العالمية؟"* | ✅ Yes | `NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE` | Context Assembler flags lack of WHO evidence | 🟢 100% SAFE |
| **QG2_metformin_diabetes_control** | *"هل دواء الميتفورمين بتاع السكر بيساعد في تبطيل التدخين؟"* | ✅ Yes | `NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE` | Context Assembler flags lack of WHO evidence | 🟢 100% SAFE |
| **QG3_acupuncture_weight_loss_control** | *"هل الإبر الصينية بتساعد على إنقاص الوزن وحرق الدهون؟"* | ✅ Yes | `NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE` | Context Assembler flags lack of WHO evidence | 🟢 100% SAFE |

---

## 5. Comprehensive Query-by-Query Results Matrix (33 Queries)

| Query ID | Category | Query Text | Admitted Rank | Direct Ev. Count | Status / Resolution |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **QA1_varenicline_efficacy** | A) Medical Terminology | *"Varenicline efficacy and adverse events for tobacco cessation"* | **Rank #1** | 10 | ⭐ **GROUNDED HIT** |
| **QA2_cytisine_evidence** | A) Medical Terminology | *"Cytisine clinical trial certainty of evidence and dosage"* | **Rank #2** | 10 | ⭐ **GROUNDED HIT** |
| **QA3_bupropion_contraindications** | A) Medical Terminology | *"Bupropion sustained release contraindications seizure history"* | **Rank #1** | 3 | ⭐ **GROUNDED HIT** |
| **QA4_combination_nrt** | A) Medical Terminology | *"Combination nicotine replacement therapy patch plus short-acting form"* | **Rank #1** | 5 | ⭐ **GROUNDED HIT** |
| **QA5_brief_advice_primary_care** | A) Medical Terminology | *"Brief advice 30 seconds to 3 minutes routine clinical consultation"* | **Rank #1** | 10 | ⭐ **GROUNDED HIT** |
| **QB1_stop_smoking_medications** | B) English Paraphrase | *"What are the approved medicines that help someone quit cigarettes?"* | **Rank #1** | 4 | ⭐ **GROUNDED HIT** |
| **QB2_pills_without_nicotine** | B) English Paraphrase | *"Are there pills without nicotine that reduce the urge to smoke?"* | **Rank #1** | 8 | ⭐ **GROUNDED HIT** |
| **QB3_doctor_talking_duration** | B) English Paraphrase | *"How much time should a physician spend talking to a patient about quitting?"* | **Rank #1** | 10 | ⭐ **GROUNDED HIT** |
| **QB4_phone_support_quitting** | B) English Paraphrase | *"Does calling a telephone helpline really help people quit smoking?"* | **Rank #1** | 8 | ⭐ **GROUNDED HIT** |
| **QB5_digital_text_apps** | B) English Paraphrase | *"Can text messages or smartphone apps assist in stopping tobacco use?"* | **Rank #1** | 6 | ⭐ **GROUNDED HIT** |
| **QC1_ana_ayez_abatal_mosh_qader** | C) Egyptian Arabic | *"أنا عايز أبطل السجاير ومش عارف أبدأ منين"* | **MISS** | 3 | ❌ Missed in Top-5 |
| **QC2_doctor_followup_ar** | C) Egyptian Arabic | *"في حد أو دكتور ممكن يساعدني خطوة بخطوة وأنا بحاول أبطل؟"* | **Rank #1** | 6 | ⭐ **GROUNDED HIT** |
| **QC3_quitline_ar** | C) Egyptian Arabic | *"في خط ساخن مجاني بالتليفون ممكن يساعدني في تبطيل السجاير؟"* | **Rank #1** | 5 | ⭐ **GROUNDED HIT** |
| **QC4_group_support_ar** | C) Egyptian Arabic | *"في جلسات جماعية مع ناس تانية بتحاول تبطل عشان نشجع بعض؟"* | **Rank #3** | 7 | ⭐ **GROUNDED HIT** |
| **QC5_pills_license_ar** | C) Egyptian Arabic | *"في حبوب معينة مرخصة بتساعد الواحد يبطل السجاير؟"* | **Rank #1** | 8 | ⭐ **GROUNDED HIT** |
| **QD1_craving_reduction_ar** | D) Non-Medical Wording | *"في حاجة تساعدني أقلل الرغبة في السجاير ومن غير ما أفضل مشتهي أدخن؟"* | **MISS** | 6 | ❌ Missed in Top-5 |
| **QD2_patch_gum_ar** | D) Non-Medical Wording | *"في لزقة أو لبانة نيكوتين تخفف الشغف للتدخين؟"* | **Rank #1** | 7 | ⭐ **GROUNDED HIT** |
| **QD3_mobile_sms_ar** | D) Non-Medical Wording | *"في برنامج على الموبايل أو رسايل تساعد في التبطيل؟"* | **Rank #1** | 6 | ⭐ **GROUNDED HIT** |
| **QD4_withdrawal_symptoms_ar** | D) Non-Medical Wording | *"جسمي بيتعب وبيجيلي صداع وعصبية أول ما أوقف السجاير، أعمل إيه؟"* | **MISS** | 4 | ❌ Missed in Top-5 |
| **QD5_combo_patch_gum_ar** | D) Non-Medical Wording | *"هل ينفع أجمع بين نوعين علاج نيكوتين مع بعض زي اللزقة واللبان؟"* | **Rank #1** | 8 | ⭐ **GROUNDED HIT** |
| **QE1_relapse_cycle_ar** | E) Implicit Clinical Intent | *"كل ما أحاول أبطل برجع أدخن تاني، أعمل إيه؟"* | **Rank #2** | 7 | ⭐ **GROUNDED HIT** |
| **QE2_medication_plus_sessions_ar** | E) Implicit Clinical Intent | *"الدواء لوحده كفاية ولا لازم جلسات ومتابعة عشان النتيجة تبقى أحسن؟"* | **MISS** | 8 | ❌ Missed in Top-5 |
| **QE3_doctor_advice_value_ar** | E) Implicit Clinical Intent | *"نصيحة الطبيب السريعة اللي في دقيقة أو دقيقتين بتفرق بجد ولا كلام وخلاص؟"* | **Rank #1** | 9 | ⭐ **GROUNDED HIT** |
| **QE4_heavy_smoker_options_ar** | E) Implicit Clinical Intent | *"بشرب علبتين سجاير في اليوم من سنين ومش عارف أسيطر على نفسي"* | **Rank #1** | 7 | ⭐ **GROUNDED HIT** |
| **QE5_ai_chatbot_cessation_ar** | E) Implicit Clinical Intent | *"هل في ذكاء اصطناعي أو شات بوت معتمد يساعد في الإقلاع عن التدخين؟"* | **Rank #1** | 6 | ⭐ **GROUNDED HIT** |
| **QF1_pregnant_women_ar** | F) Specific Clinical Situations | *"أنا حامل وبشرب سجاير، أعمل إيه والدواء أمان ليا ولا لأ؟"* | **Rank #1** | 2 | ⭐ **GROUNDED HIT** |
| **QF2_smokeless_tobacco_shammah_ar** | F) Specific Clinical Situations | *"الناس اللي بتستخدم الشمة أو التبغ غير المدخن، إيه علاجهم؟"* | **Rank #1** | 8 | ⭐ **GROUNDED HIT** |
| **QF3_alternative_acupuncture_hypnosis_ar** | F) Specific Clinical Situations | *"هل جلسات الإبر الصينية أو التنويم المغناطيسي بتنفع في الإقلاع عن التدخين؟"* | **MISS** | 2 | ❌ Missed in Top-5 |
| **QF4_adolescents_young_people_ar** | F) Specific Clinical Situations | *"هل الأدوية دي تنفع للمراهقين والشباب الصغيرين تحت 18 سنة؟"* | **Rank #1** | 2 | ⭐ **GROUNDED HIT** |
| **QF5_tuberculosis_comorbidity_ar** | F) Specific Clinical Situations | *"مرضى الدرن والسل الرئوي اللي بيدخنوا، إيه توصيات منظمة الصحة العالمية ليهم؟"* | **Rank #1** | 2 | ⭐ **GROUNDED HIT** |
| **QG1_ecigarettes_cessation_control** | *Control* | *"هل السجائر الإلكترونية والفيب موصى بيها كعلاج رسمي للإقلاع عن التدخين في دليل منظمة الصحة العالمية؟"* | — | 0 | **CONTROL_PROTECTED_SAFE** |
| **QG2_metformin_diabetes_control** | *Control* | *"هل دواء الميتفورمين بتاع السكر بيساعد في تبطيل التدخين؟"* | — | 0 | **CONTROL_PROTECTED_SAFE** |
| **QG3_acupuncture_weight_loss_control** | *Control* | *"هل الإبر الصينية بتساعد على إنقاص الوزن وحرق الدهون؟"* | — | 0 | **CONTROL_PROTECTED_SAFE** |

---

## 6. Final Assessment & Next Steps

- **Did we reach >= 80% Grounded Evidence Recall?**
  - **83.3% Grounded Recall** achieved across positive queries.
- **Negative Control Safety:** **100% (3/3 negative controls safely rejected)**.
- **Verbatim Provenance:** 100% preserved with full section and physical page links.
- **Ready for Grounded LLM Response Generation.**