"""
Comprehensive Multi-Level Evaluation Benchmark for Dense Semantic Retrieval vs BM25
Medical RAG Project: Oxygen (أوكسجين)
Source Document: WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)

Standardized Benchmark Dataset:
- Category A: Medical Terminology (5 queries)
- Category B: English Paraphrase (5 queries)
- Category C: Egyptian Arabic (5 queries)
- Category D: Egyptian Arabic + Non-Medical Wording (5 queries)
- Category E: Implicit Clinical Intent (5 queries)
- Category F: Specific Clinical Situations (5 queries)
- Category G: Negative Controls / Out-of-Scope (NO_DIRECT_EVIDENCE) (3 queries)

Total: 33 Clinical Evaluation Queries

Evaluation Metrics:
- Recall@1, Recall@5, MRR (Overall & Per Category)
- Top-5 Clinical Evidence Classification:
  - Correct Evidence (Direct WHO Recommendation / Evidence Profile)
  - Related but Insufficient (Relevant chapter/glossary but lacks decision rule)
  - Irrelevant (Unrelated topic)
  - Potentially Misleading (Contradicts clinical intent)
- Head-to-Head Comparison with BM25 Sparse Retrieval
"""

from __future__ import annotations

import os
import sys
import json
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Set, Tuple

sys.path.insert(0, r"C:\Users\moham\OneDrive\Apps\اوكسجين\scripts")
from dense_retriever import DenseRetriever, DenseSearchResult
from bm25_retriever import BM25Retriever, BM25SearchResult

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


# ─────────────────────────────────────────────────────────────────────────────
# Benchmark Data Model
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class GoldEvidence:
    chunk_id: str
    section_number: Optional[str]
    physical_page: int
    rationale: str


@dataclass
class BenchmarkQuery:
    query_id: str
    category: str
    query_text: str
    language_type: str
    gold_evidences: List[GoldEvidence]
    is_negative_control: bool = False

    @property
    def target_chunk_ids(self) -> List[str]:
        return [g.chunk_id for g in self.gold_evidences]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query_id": self.query_id,
            "category": self.category,
            "query_text": self.query_text,
            "language_type": self.language_type,
            "is_negative_control": self.is_negative_control,
            "gold_evidences": [asdict(g) for g in self.gold_evidences],
            "target_chunk_ids": self.target_chunk_ids,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Canonical 33-Query Evaluation Dataset
# ─────────────────────────────────────────────────────────────────────────────

EVALUATION_QUERIES: List[BenchmarkQuery] = [
    # ── Category A: Medical Terminology (5 queries) ──────────────────────────
    BenchmarkQuery(
        query_id="QA1_varenicline_efficacy",
        category="A) Medical Terminology",
        query_text="Varenicline efficacy and adverse events for tobacco cessation",
        language_type="en_medical",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_3_1", "3.3.1", 35, "Recommendation 5 strongly recommending varenicline"),
            GoldEvidence("chunk_sec_3_3_3_3_p01", "3.3.3.3", 38, "RCT evidence for varenicline efficacy"),
            GoldEvidence("chunk_sec_3_3_4_p01", "3.3.4", 41, "Implementation considerations and adverse events"),
        ],
    ),
    BenchmarkQuery(
        query_id="QA2_cytisine_evidence",
        category="A) Medical Terminology",
        query_text="Cytisine clinical trial certainty of evidence and dosage",
        language_type="en_medical",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_3_1", "3.3.1", 35, "Recommendation 7 strongly recommending cytisine"),
            GoldEvidence("chunk_sec_3_3_3_4", "3.3.3.4", 39, "RCT evidence for cytisine with moderate certainty"),
        ],
    ),
    BenchmarkQuery(
        query_id="QA3_bupropion_contraindications",
        category="A) Medical Terminology",
        query_text="Bupropion sustained release contraindications seizure history",
        language_type="en_medical",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_3_1", "3.3.1", 35, "Recommendation 6 strongly recommending bupropion SR"),
            GoldEvidence("chunk_sec_3_3_3_2", "3.3.3.2", 37, "Evidence on bupropion efficacy and seizure contraindications"),
            GoldEvidence("chunk_sec_3_3_4_p01", "3.3.4", 41, "Implementation safety considerations for bupropion"),
        ],
    ),
    BenchmarkQuery(
        query_id="QA4_combination_nrt",
        category="A) Medical Terminology",
        query_text="Combination nicotine replacement therapy patch plus short-acting form",
        language_type="en_medical",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_3_1", "3.3.1", 35, "Recommendation 3 on combination NRT superiority"),
            GoldEvidence("chunk_sec_3_3_3_5", "3.3.3.5", 39, "Evidence comparing combination NRT vs single NRT"),
            GoldEvidence("chunk_node_L1_glossary_of_terms_p05", "Glossary", 11, "Definition of combination pharmacotherapy"),
        ],
    ),
    BenchmarkQuery(
        query_id="QA5_brief_advice_primary_care",
        category="A) Medical Terminology",
        query_text="Brief advice 30 seconds to 3 minutes routine clinical consultation",
        language_type="en_medical",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_1_1", "3.1.1", 29, "Recommendation 1 on brief advice in routine encounters"),
            GoldEvidence("chunk_sec_3_1_3_p01", "3.1.3", 29, "Evidence supporting brief advice (RR=1.25)"),
            GoldEvidence("chunk_node_L1_glossary_of_terms_p03", "Glossary", 11, "Definition of brief advice"),
        ],
    ),

    # ── Category B: English Paraphrase (5 queries) ───────────────────────────
    BenchmarkQuery(
        query_id="QB1_stop_smoking_medications",
        category="B) English Paraphrase",
        query_text="What are the approved medicines that help someone quit cigarettes?",
        language_type="en_paraphrase",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_3_1", "3.3.1", 35, "Summary of first-line pharmacotherapies"),
            GoldEvidence("chunk_sec_3_3_3_6_p01", "3.3.3.6", 40, "General evidence synthesis across pharmacotherapies"),
        ],
    ),
    BenchmarkQuery(
        query_id="QB2_pills_without_nicotine",
        category="B) English Paraphrase",
        query_text="Are there pills without nicotine that reduce the urge to smoke?",
        language_type="en_paraphrase",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_3_1", "3.3.1", 35, "Recommendations for non-nicotine pills: varenicline, bupropion, cytisine"),
            GoldEvidence("chunk_sec_3_3_3_2", "3.3.3.2", 37, "Bupropion non-nicotine oral medication"),
            GoldEvidence("chunk_sec_3_3_3_3_p01", "3.3.3.3", 38, "Varenicline non-nicotine oral medication"),
            GoldEvidence("chunk_sec_3_3_3_4", "3.3.3.4", 39, "Cytisine non-nicotine oral medication"),
        ],
    ),
    BenchmarkQuery(
        query_id="QB3_doctor_talking_duration",
        category="B) English Paraphrase",
        query_text="How much time should a physician spend talking to a patient about quitting?",
        language_type="en_paraphrase",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_1_1", "3.1.1", 29, "Recommendation 1 specifying 30 seconds to 3 minutes"),
            GoldEvidence("chunk_sec_3_1_3_p01", "3.1.3", 29, "Evidence justifying brief advice timing"),
        ],
    ),
    BenchmarkQuery(
        query_id="QB4_phone_support_quitting",
        category="B) English Paraphrase",
        query_text="Does calling a telephone helpline really help people quit smoking?",
        language_type="en_paraphrase",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_1_1", "3.1.1", 29, "Recommendation on toll-free telephone counselling"),
            GoldEvidence("chunk_sec_3_1_3_p04", "3.1.3", 31, "Evidence on quitline effectiveness"),
            GoldEvidence("chunk_node_L1_glossary_of_terms_p14", "Glossary", 12, "Definition of toll-free quitline"),
        ],
    ),
    BenchmarkQuery(
        query_id="QB5_digital_text_apps",
        category="B) English Paraphrase",
        query_text="Can text messages or smartphone apps assist in stopping tobacco use?",
        language_type="en_paraphrase",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_2_1", "3.2.1", 32, "Recommendation 4 on digital interventions and text messaging"),
            GoldEvidence("chunk_sec_3_2_3_p01", "3.2.3", 32, "Evidence on text-messaging programmes"),
            GoldEvidence("chunk_node_L1_glossary_of_terms_p16", "Glossary", 13, "Definition of text messaging support"),
            GoldEvidence("chunk_node_L1_glossary_of_terms_p19", "Glossary", 13, "Definition of smartphone applications"),
        ],
    ),

    # ── Category C: Egyptian Arabic (5 queries) ──────────────────────────────
    BenchmarkQuery(
        query_id="QC1_ana_ayez_abatal_mosh_qader",
        category="C) Egyptian Arabic",
        query_text="أنا عايز أبطل السجاير ومش عارف أبدأ منين",
        language_type="ar_egyptian",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_1_1", "3.1.1", 29, "Core recommendations for brief advice and behavioural support"),
            GoldEvidence("chunk_sec_3_3_1", "3.3.1", 35, "Core recommendations for first-line medications"),
            GoldEvidence("chunk_sec_3_5_1", "3.5.1", 44, "Recommendation 9 on combined behavioural support and medication"),
        ],
    ),
    BenchmarkQuery(
        query_id="QC2_doctor_followup_ar",
        category="C) Egyptian Arabic",
        query_text="في حد أو دكتور ممكن يساعدني خطوة بخطوة وأنا بحاول أبطل؟",
        language_type="ar_egyptian",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_1_1", "3.1.1", 29, "Recommendation 2 on individual intensive counselling"),
            GoldEvidence("chunk_sec_3_1_3_p02", "3.1.3", 30, "Evidence supporting individual face-to-face counselling"),
            GoldEvidence("chunk_sec_3_5_1", "3.5.1", 44, "Recommendation 9 on combined counselling and medical support"),
        ],
    ),
    BenchmarkQuery(
        query_id="QC3_quitline_ar",
        category="C) Egyptian Arabic",
        query_text="في خط ساخن مجاني بالتليفون ممكن يساعدني في تبطيل السجاير؟",
        language_type="ar_egyptian",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_1_1", "3.1.1", 29, "Recommendation for toll-free telephone counselling"),
            GoldEvidence("chunk_sec_3_1_3_p04", "3.1.3", 31, "Evidence on quitline effectiveness"),
            GoldEvidence("chunk_node_L1_glossary_of_terms_p14", "Glossary", 12, "Definition of toll-free quitline"),
        ],
    ),
    BenchmarkQuery(
        query_id="QC4_group_support_ar",
        category="C) Egyptian Arabic",
        query_text="في جلسات جماعية مع ناس تانية بتحاول تبطل عشان نشجع بعض؟",
        language_type="ar_egyptian",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_1_1", "3.1.1", 29, "Recommendation 2 on group face-to-face behavioural support"),
            GoldEvidence("chunk_sec_3_1_3_p03", "3.1.3", 30, "Evidence on group behavioural counselling"),
            GoldEvidence("chunk_node_L1_glossary_of_terms_p13", "Glossary", 12, "Definition of group behavioural counselling"),
        ],
    ),
    BenchmarkQuery(
        query_id="QC5_pills_license_ar",
        category="C) Egyptian Arabic",
        query_text="في حبوب معينة مرخصة بتساعد الواحد يبطل السجاير؟",
        language_type="ar_egyptian",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_3_1", "3.3.1", 35, "Recommendations for prescription oral medications (varenicline, bupropion, cytisine)"),
            GoldEvidence("chunk_node_L1_glossary_of_terms_p09", "Glossary", 12, "Definition of first-line medications"),
        ],
    ),

    # ── Category D: Egyptian Arabic + Non-Medical Wording (5 queries) ─────────
    BenchmarkQuery(
        query_id="QD1_craving_reduction_ar",
        category="D) Non-Medical Wording",
        query_text="في حاجة تساعدني أقلل الرغبة في السجاير ومن غير ما أفضل مشتهي أدخن؟",
        language_type="ar_non_medical",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_3_1", "3.3.1", 35, "Pharmacotherapy recommendations to reduce cravings"),
            GoldEvidence("chunk_sec_3_3_3_1_p01", "3.3.3.1", 36, "NRT mechanism reducing nicotine cravings"),
            GoldEvidence("chunk_node_L1_glossary_of_terms_p17", "Glossary", 13, "NRT definition: relieving cravings and withdrawal"),
        ],
    ),
    BenchmarkQuery(
        query_id="QD2_patch_gum_ar",
        category="D) Non-Medical Wording",
        query_text="في لزقة أو لبانة نيكوتين تخفف الشغف للتدخين؟",
        language_type="ar_non_medical",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_3_1", "3.3.1", 35, "Recommendation 3 on Nicotine Replacement Therapy"),
            GoldEvidence("chunk_sec_3_3_3_1_p01", "3.3.3.1", 36, "Evidence on nicotine patches and nicotine gum"),
            GoldEvidence("chunk_node_L1_glossary_of_terms_p17", "Glossary", 13, "Definition of NRT products"),
        ],
    ),
    BenchmarkQuery(
        query_id="QD3_mobile_sms_ar",
        category="D) Non-Medical Wording",
        query_text="في برنامج على الموبايل أو رسايل تساعد في التبطيل؟",
        language_type="ar_non_medical",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_2_1", "3.2.1", 32, "Recommendation 4 on digital interventions and SMS"),
            GoldEvidence("chunk_sec_3_2_3_p01", "3.2.3", 32, "Evidence on mobile text messaging"),
            GoldEvidence("chunk_node_L1_glossary_of_terms_p16", "Glossary", 13, "Definition of mobile messaging"),
        ],
    ),
    BenchmarkQuery(
        query_id="QD4_withdrawal_symptoms_ar",
        category="D) Non-Medical Wording",
        query_text="جسمي بيتعب وبيجيلي صداع وعصبية أول ما أوقف السجاير، أعمل إيه؟",
        language_type="ar_non_medical",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_3_1", "3.3.1", 35, "Recommendations on pharmacotherapies relieving withdrawal symptoms"),
            GoldEvidence("chunk_sec_3_3_3_1_p01", "3.3.3.1", 36, "Evidence on NRT relieving withdrawal discomfort"),
            GoldEvidence("chunk_node_L1_glossary_of_terms_p17", "Glossary", 13, "Definition of NRT for withdrawal symptoms"),
        ],
    ),
    BenchmarkQuery(
        query_id="QD5_combo_patch_gum_ar",
        category="D) Non-Medical Wording",
        query_text="هل ينفع أجمع بين نوعين علاج نيكوتين مع بعض زي اللزقة واللبان؟",
        language_type="ar_non_medical",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_3_1", "3.3.1", 35, "Recommendation 3 approving combination NRT (patch + short-acting)"),
            GoldEvidence("chunk_sec_3_3_3_5", "3.3.3.5", 39, "Evidence confirming superiority of combination NRT"),
            GoldEvidence("chunk_node_L1_glossary_of_terms_p05", "Glossary", 11, "Definition of combination pharmacotherapy"),
        ],
    ),

    # ── Category E: Implicit Clinical Intent (5 queries) ─────────────────────
    BenchmarkQuery(
        query_id="QE1_relapse_cycle_ar",
        category="E) Implicit Clinical Intent",
        query_text="كل ما أحاول أبطل برجع أدخن تاني، أعمل إيه؟",
        language_type="ar_implicit",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_1_1", "3.1.1", 29, "Intensive counselling incorporating relapse prevention"),
            GoldEvidence("chunk_sec_3_3_1", "3.3.1", 35, "First-line pharmacotherapy for relapsing smokers"),
            GoldEvidence("chunk_sec_3_3_3_5", "3.3.3.5", 39, "Combination NRT improving long-term abstinence"),
        ],
    ),
    BenchmarkQuery(
        query_id="QE2_medication_plus_sessions_ar",
        category="E) Implicit Clinical Intent",
        query_text="الدواء لوحده كفاية ولا لازم جلسات ومتابعة عشان النتيجة تبقى أحسن؟",
        language_type="ar_implicit",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_5_1", "3.5.1", 44, "Recommendation 9 strongly recommending combining medication with behavioural support"),
            GoldEvidence("chunk_sec_3_5_3_p01", "3.5.3", 44, "Evidence showing combined support yields highest quit rates"),
        ],
    ),
    BenchmarkQuery(
        query_id="QE3_doctor_advice_value_ar",
        category="E) Implicit Clinical Intent",
        query_text="نصيحة الطبيب السريعة اللي في دقيقة أو دقيقتين بتفرق بجد ولا كلام وخلاص؟",
        language_type="ar_implicit",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_1_1", "3.1.1", 29, "Recommendation 1 on brief advice in routine healthcare"),
            GoldEvidence("chunk_sec_3_1_3_p01", "3.1.3", 29, "Evidence proving brief advice increases quit rates (RR=1.25)"),
            GoldEvidence("chunk_node_L1_glossary_of_terms_p03", "Glossary", 11, "Definition of brief advice"),
        ],
    ),
    BenchmarkQuery(
        query_id="QE4_heavy_smoker_options_ar",
        category="E) Implicit Clinical Intent",
        query_text="بشرب علبتين سجاير في اليوم من سنين ومش عارف أسيطر على نفسي",
        language_type="ar_implicit",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_3_1", "3.3.1", 35, "First-line pharmacotherapy and combination NRT for heavy dependence"),
            GoldEvidence("chunk_sec_3_5_1", "3.5.1", 44, "Recommendation 9 on combined medication + intensive counselling"),
            GoldEvidence("chunk_sec_3_3_3_5", "3.3.3.5", 39, "Evidence on combination NRT for high dependence"),
        ],
    ),
    BenchmarkQuery(
        query_id="QE5_ai_chatbot_cessation_ar",
        category="E) Implicit Clinical Intent",
        query_text="هل في ذكاء اصطناعي أو شات بوت معتمد يساعد في الإقلاع عن التدخين؟",
        language_type="ar_implicit",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_2_1", "3.2.1", 32, "Recommendation 4 on digital AI interventions and chatbots"),
            GoldEvidence("chunk_sec_3_2_3_p02", "3.2.3", 33, "Evidence on AI and chatbot cessation interventions"),
            GoldEvidence("chunk_node_L1_glossary_of_terms_p01", "Glossary", 11, "Definition of AI cessation interventions"),
        ],
    ),

    # ── Category F: Specific Clinical Situations (5 queries) ─────────────────
    BenchmarkQuery(
        query_id="QF1_pregnant_women_ar",
        category="F) Specific Clinical Situations",
        query_text="أنا حامل وبشرب سجاير، أعمل إيه والدواء أمان ليا ولا لأ؟",
        language_type="ar_clinical_situation",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_3_4_p01", "3.3.4", 41, "Implementation considerations: pharmacotherapy in pregnancy risk-benefit assessment"),
            GoldEvidence("chunk_sec_3_1_4", "3.1.4", 31, "Implementation considerations: behavioural support priority for pregnant women"),
        ],
    ),
    BenchmarkQuery(
        query_id="QF2_smokeless_tobacco_shammah_ar",
        category="F) Specific Clinical Situations",
        query_text="الناس اللي بتستخدم الشمة أو التبغ غير المدخن، إيه علاجهم؟",
        language_type="ar_clinical_situation",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_4_1", "3.4.1", 42, "Recommendation 8 for smokeless tobacco cessation"),
            GoldEvidence("chunk_sec_3_4_3_p01", "3.4.3", 42, "Evidence on varenicline and NRT for smokeless tobacco"),
            GoldEvidence("chunk_node_L1_glossary_of_terms_p20", "Glossary", 13, "Definition of smokeless tobacco"),
        ],
    ),
    BenchmarkQuery(
        query_id="QF3_alternative_acupuncture_hypnosis_ar",
        category="F) Specific Clinical Situations",
        query_text="هل جلسات الإبر الصينية أو التنويم المغناطيسي بتنفع في الإقلاع عن التدخين؟",
        language_type="ar_clinical_situation",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_6_1", "3.6.1", 45, "Recommendation 10 NOT to use acupuncture or hypnotherapy"),
            GoldEvidence("chunk_sec_3_6_3_p01", "3.6.3", 45, "Evidence showing lack of efficacy for alternative therapies"),
            GoldEvidence("chunk_node_L1_glossary_of_terms_p26", "Glossary", 13, "Definition of unproven alternative therapies"),
        ],
    ),
    BenchmarkQuery(
        query_id="QF4_adolescents_young_people_ar",
        category="F) Specific Clinical Situations",
        query_text="هل الأدوية دي تنفع للمراهقين والشباب الصغيرين تحت 18 سنة؟",
        language_type="ar_clinical_situation",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_3_4_p01", "3.3.4", 41, "Implementation considerations for adolescents and youth"),
            GoldEvidence("chunk_sec_3_1_4", "3.1.4", 31, "Behavioural support considerations for young populations"),
        ],
    ),
    BenchmarkQuery(
        query_id="QF5_tuberculosis_comorbidity_ar",
        category="F) Specific Clinical Situations",
        query_text="مرضى الدرن والسل الرئوي اللي بيدخنوا، إيه توصيات منظمة الصحة العالمية ليهم؟",
        language_type="ar_clinical_situation",
        gold_evidences=[
            GoldEvidence("chunk_sec_3_1_4", "3.1.4", 31, "Implementation considerations for patients with TB/chronic respiratory diseases"),
            GoldEvidence("chunk_sec_3_3_4_p01", "3.3.4", 41, "Pharmacotherapy integration in TB clinical programs"),
        ],
    ),

    # ── Category G: Negative Controls / Out-of-Scope (3 queries) ─────────────
    BenchmarkQuery(
        query_id="QG1_ecigarettes_cessation_control",
        category="G) Control (NO_DIRECT_EVIDENCE)",
        query_text="هل السجائر الإلكترونية والفيب موصى بيها كعلاج رسمي للإقلاع عن التدخين في دليل منظمة الصحة العالمية؟",
        language_type="control",
        gold_evidences=[],
        is_negative_control=True,
    ),
    BenchmarkQuery(
        query_id="QG2_metformin_diabetes_control",
        category="G) Control (NO_DIRECT_EVIDENCE)",
        query_text="هل دواء الميتفورمين بتاع السكر بيساعد في تبطيل التدخين؟",
        language_type="control",
        gold_evidences=[],
        is_negative_control=True,
    ),
    BenchmarkQuery(
        query_id="QG3_acupuncture_weight_loss_control",
        category="G) Control (NO_DIRECT_EVIDENCE)",
        query_text="هل الإبر الصينية بتساعد على إنقاص الوزن وحرق الدهون؟",
        language_type="control",
        gold_evidences=[],
        is_negative_control=True,
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
# Evidence Quality Classifier (Clinical Auditing)
# ─────────────────────────────────────────────────────────────────────────────

def classify_evidence_quality(
    chunk_id: str,
    target_ids: Set[str],
    retrieved_rec: Dict[str, Any],
    query: BenchmarkQuery,
) -> str:
    """
    Classifies a retrieved chunk into one of four clinical tiers:
    - CORRECT_EVIDENCE: Direct matching gold target
    - RELATED_INSUFFICIENT: In the same chapter or related domain, but not the exact decision rule
    - IRRELEVANT: Unrelated to the clinical question
    - POTENTIALLY_MISLEADING: Could lead to incorrect clinical action
    """
    if chunk_id in target_ids:
        return "CORRECT_EVIDENCE"

    if query.is_negative_control:
        return "IRRELEVANT"

    # Check if from same section/chapter
    sec = retrieved_rec.get("section_number") or ""
    cat = query.category

    # If it's a pharmacotherapy query and returns another pharmacotherapy chunk, it's related
    if "Pharmacology" in cat or "pills" in query.query_text.lower() or "دواء" in query.query_text:
        if sec.startswith("3.3") or sec.startswith("3.4") or sec.startswith("3.5"):
            return "RELATED_INSUFFICIENT"

    # If it's a behavioural query and returns another behavioural chunk
    if "Behavioural" in cat or "دكتور" in query.query_text or "جلسات" in query.query_text:
        if sec.startswith("3.1") or sec.startswith("3.2"):
            return "RELATED_INSUFFICIENT"

    # If it returns an alternative therapy chunk for standard therapy query, could be misleading
    if sec.startswith("3.6") and not ("الإبر الصينية" in query.query_text or "acupuncture" in query.query_text):
        return "POTENTIALLY_MISLEADING"

    return "IRRELEVANT"


# ─────────────────────────────────────────────────────────────────────────────
# Unified System Evaluator
# ─────────────────────────────────────────────────────────────────────────────

def run_evaluation(
    retriever_fn,
    benchmark: List[BenchmarkQuery],
    system_name: str,
    top_k: int = 5,
) -> Dict[str, Any]:
    """
    Evaluates any retrieval function (Dense or BM25) on the 33-query benchmark.
    """
    pos_queries = [q for q in benchmark if not q.is_negative_control]
    control_queries = [q for q in benchmark if q.is_negative_control]

    category_stats: Dict[str, Dict[str, Any]] = {}
    query_reports: List[Dict[str, Any]] = []

    recall_1_count = 0
    recall_5_count = 0
    mrr_sum = 0.0

    quality_tier_counts = {
        "CORRECT_EVIDENCE": 0,
        "RELATED_INSUFFICIENT": 0,
        "IRRELEVANT": 0,
        "POTENTIALLY_MISLEADING": 0,
    }

    for query in benchmark:
        cat = query.category
        if cat not in category_stats:
            category_stats[cat] = {
                "count": 0,
                "recall_1": 0,
                "recall_5": 0,
                "mrr_sum": 0.0,
            }

        category_stats[cat]["count"] += 1
        target_set = set(query.target_chunk_ids)

        # Retrieve
        results = retriever_fn(query.query_text, top_k=top_k)
        retrieved_ids = [
            r.chunk_id if hasattr(r, "chunk_id") else r["chunk_id"]
            for r in results
        ]

        if query.is_negative_control:
            top_score = 0.0
            if results:
                first = results[0]
                if hasattr(first, "score"):
                    top_score = getattr(first, "score", 0.0)
                elif hasattr(first, "rrf_score"):
                    top_score = getattr(first, "rrf_score", 0.0)
                elif isinstance(first, dict):
                    top_score = first.get("score", first.get("rrf_score", 0.0))

            query_reports.append({
                "query_id": query.query_id,
                "category": query.category,
                "query_text": query.query_text,
                "is_control": True,
                "top_retrieved_id": retrieved_ids[0] if retrieved_ids else None,
                "top_score": round(float(top_score), 6),
                "status": "CONTROL_OBSERVED",
            })
            continue

        hit_1 = (retrieved_ids[0] in target_set) if retrieved_ids else False
        hit_5 = any(cid in target_set for cid in retrieved_ids[:top_k])

        first_rank = None
        for rank, cid in enumerate(retrieved_ids[:top_k], start=1):
            if cid in target_set:
                first_rank = rank
                break

        rr = (1.0 / first_rank) if first_rank is not None else 0.0

        if hit_1:
            recall_1_count += 1
            category_stats[cat]["recall_1"] += 1
        if hit_5:
            recall_5_count += 1
            category_stats[cat]["recall_5"] += 1

        mrr_sum += rr
        category_stats[cat]["mrr_sum"] += rr

        # Audit top-5 items quality
        top_5_items = []
        for i, res in enumerate(results[:top_k]):
            cid = getattr(res, "chunk_id", None) if hasattr(res, "chunk_id") else (res.get("chunk_id", "") if isinstance(res, dict) else "")
            if hasattr(res, "score"):
                score = getattr(res, "score", 0.0)
            elif hasattr(res, "rrf_score"):
                score = getattr(res, "rrf_score", 0.0)
            elif isinstance(res, dict):
                score = res.get("score", res.get("rrf_score", 0.0))
            else:
                score = 0.0

            sec = getattr(res, "section_number", None) if hasattr(res, "section_number") else (res.get("section_number", "") if isinstance(res, dict) else "")
            page = getattr(res, "physical_page_start", None) if hasattr(res, "physical_page_start") else (res.get("physical_page_start", None) if isinstance(res, dict) else None)
            ctype = getattr(res, "content_type", None) if hasattr(res, "content_type") else (res.get("content_type", "") if isinstance(res, dict) else "")

            rec_dict = {"section_number": sec}
            tier = classify_evidence_quality(cid, target_set, rec_dict, query)
            quality_tier_counts[tier] += 1

            top_5_items.append({
                "rank": i + 1,
                "chunk_id": cid,
                "score": round(float(score), 6),
                "section": sec,
                "physical_page": page,
                "content_type": ctype,
                "quality_tier": tier,
                "hit": cid in target_set,
            })

        query_reports.append({
            "query_id": query.query_id,
            "category": query.category,
            "query_text": query.query_text,
            "is_control": False,
            "targets": query.target_chunk_ids,
            "hit_1": hit_1,
            "hit_5": hit_5,
            "first_rank": first_rank,
            "rr": round(rr, 4),
            "top_5": top_5_items,
        })

    num_pos = len(pos_queries)
    overall_r1 = (recall_1_count / num_pos) if num_pos > 0 else 0.0
    overall_r5 = (recall_5_count / num_pos) if num_pos > 0 else 0.0
    overall_mrr = (mrr_sum / num_pos) if num_pos > 0 else 0.0

    cat_breakdown = {}
    for cat, st in category_stats.items():
        n = st["count"]
        if "Control" in cat:
            continue
        cat_breakdown[cat] = {
            "query_count": n,
            "recall_1": round(st["recall_1"] / n, 4),
            "recall_5": round(st["recall_5"] / n, 4),
            "mrr": round(st["mrr_sum"] / n, 4),
        }

    return {
        "system_name": system_name,
        "total_queries": len(benchmark),
        "positive_queries": num_pos,
        "control_queries": len(control_queries),
        "overall": {
            "recall_1": round(overall_r1, 4),
            "recall_5": round(overall_r5, 4),
            "mrr": round(overall_mrr, 4),
        },
        "quality_tiers": quality_tier_counts,
        "category_performance": cat_breakdown,
        "query_reports": query_reports,
    }


def export_benchmark_queries_json(output_path: str):
    """Exports the 33 benchmark queries and gold labels to JSON."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    payload = {
        "dataset_version": "v2.0_dense_benchmark_33q",
        "guideline_source": "WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)",
        "total_queries": len(EVALUATION_QUERIES),
        "queries": [q.to_dict() for q in EVALUATION_QUERIES],
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    logging.info(f"Exported evaluation dataset to {output_path}")


if __name__ == "__main__":
    export_benchmark_queries_json(r"C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\dense_evaluation_queries.json")
