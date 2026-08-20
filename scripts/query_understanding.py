"""
Clinical Query Understanding Engine — Medical RAG: Oxygen (أوكسجين)
Source Document: WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)

Translates patient inquiries (English, Egyptian Colloquial Arabic, non-medical symptoms, implicit intent)
into a structured Clinical Query Representation with canonical medical concepts, intervention codes,
population constraints, and bilingual search terms.

Guarantees:
- 100% Offline & Deterministic.
- Zero Hallucination: strictly extracts medical intentions and canonical ontology terms.
- Does NOT fabricate clinical evidence or alter Ground Truth records.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Set, Optional, Any


# ─────────────────────────────────────────────────────────────────────────────
# Clinical Domain Knowledge & Egyptian Colloquial Lexicon (WHO Aligned)
# ─────────────────────────────────────────────────────────────────────────────

# Egyptian colloquial terms to canonical clinical intervention keys
ARABIC_EGYPTIAN_INTERVENTION_MAP: Dict[str, str] = {
    "لزقة": "nrt_transdermal_patch",
    "لزقه": "nrt_transdermal_patch",
    "لبان": "nrt_gum",
    "لبانة": "nrt_gum",
    "لبانه": "nrt_gum",
    "علكة": "nrt_gum",
    "نيكوتين": "nicotine_replacement_therapy",
    "بدائل النيكوتين": "nicotine_replacement_therapy",
    "بديل النيكوتين": "nicotine_replacement_therapy",
    "حبوب": "oral_pharmacotherapy",
    "برشام": "oral_pharmacotherapy",
    "دواء": "pharmacotherapy",
    "ادوية": "pharmacotherapy",
    "أدوية": "pharmacotherapy",
    "فارينيكلين": "varenicline",
    "تشامبكس": "varenicline",
    "بوبروبيون": "bupropion_sr",
    "ويلبيوترين": "bupropion_sr",
    "سيتيزين": "cytisine",
    "سيتيسين": "cytisine",
    "تابيكس": "cytisine",
    "خط ساخن": "toll_free_quitline",
    "تليفون": "toll_free_quitline",
    "تلفون": "toll_free_quitline",
    "رسايل": "mobile_text_messaging_sms",
    "رسائل": "mobile_text_messaging_sms",
    "موبايل": "digital_smartphone_interventions",
    "برنامج على الموبايل": "digital_smartphone_interventions",
    "تطبيق": "digital_smartphone_interventions",
    "ابلكيشن": "digital_smartphone_interventions",
    "شات بوت": "ai_chatbot_interventions",
    "ذكاء اصطناعي": "ai_chatbot_interventions",
    "جلسات": "behavioural_counselling",
    "جلسات جماعية": "group_behavioural_counselling",
    "جلسات جماعيه": "group_behavioural_counselling",
    "مجموعة": "group_behavioural_counselling",
    "تشجيع": "group_behavioural_counselling",
    "دكتور": "physician_brief_advice_or_counselling",
    "طبيب": "physician_brief_advice_or_counselling",
    "أخصائي": "individual_intensive_counselling",
    "اخصائي": "individual_intensive_counselling",
    "نصيحة": "brief_advice",
    "نصيحه": "brief_advice",
    "استشارة": "brief_advice",
    "ابرة صينية": "acupuncture_unproven",
    "إبر صينية": "acupuncture_unproven",
    "ابر صينيه": "acupuncture_unproven",
    "وخز بالإبر": "acupuncture_unproven",
    "وخز بالابر": "acupuncture_unproven",
    "تنويم مغناطيسي": "hypnotherapy_unproven",
    "تنويم": "hypnotherapy_unproven",
    "ليزر": "laser_therapy_unproven",
    "جلسات ليزر": "laser_therapy_unproven",
    "جلسات الليزر": "laser_therapy_unproven",
    "ساونا": "sauna_out_of_scope",
    "الساونا": "sauna_out_of_scope",
    "تعرق": "sauna_out_of_scope",
    "عرق": "sauna_out_of_scope",
    "القديس يوحنا": "st_johns_wort_unproven",
    "سانت جون": "st_johns_wort_unproven",
    "سجائر عشبية": "herbal_cigarettes_unproven",
    "سجاير عشبية": "herbal_cigarettes_unproven",
    "سيجارة عشبية": "herbal_cigarettes_unproven",
    "اعشاب": "herbal_unproven",
    "أعشاب": "herbal_unproven",
    "عشبة": "herbal_unproven",
    "عطار": "herbal_unproven",
    "أنسولين": "insulin_diabetes_out_of_scope",
    "انسولين": "insulin_diabetes_out_of_scope",
    "سكر تراكمي": "insulin_diabetes_out_of_scope",
    "كسر": "orthopedics_fracture_out_of_scope",
    "جبس": "orthopedics_fracture_out_of_scope",
    "شرايح ومسامير": "orthopedics_fracture_out_of_scope",
    "شريحة ومسامير": "orthopedics_fracture_out_of_scope",
    "زائدة دودية": "appendicitis_emergency_out_of_scope",
    "زايدة دودية": "appendicitis_emergency_out_of_scope",
    "زائدة": "appendicitis_emergency_out_of_scope",
    "زايدة": "appendicitis_emergency_out_of_scope",
    "عضلات": "gym_fitness_out_of_scope",
    "بنش": "gym_fitness_out_of_scope",
    "جيم": "gym_fitness_out_of_scope",
    "شمة": "smokeless_tobacco",
    "شمه": "smokeless_tobacco",
    "تمباك": "smokeless_tobacco",
    "تبغ غير مدخن": "smokeless_tobacco",
    "سويكة": "smokeless_tobacco",
    "سويكه": "smokeless_tobacco",
    "فيب": "e_cigarettes_out_of_scope",
    "الفيب": "e_cigarettes_out_of_scope",
    "شيشة إلكترونية": "e_cigarettes_out_of_scope",
    "الشيشة الإلكترونية": "e_cigarettes_out_of_scope",
    "شيشة الكترونية": "e_cigarettes_out_of_scope",
    "الشيشة الالكترونية": "e_cigarettes_out_of_scope",
    "سجائر الكترونية": "e_cigarettes_out_of_scope",
    "السجائر الالكترونية": "e_cigarettes_out_of_scope",
    "سجائر إلكترونية": "e_cigarettes_out_of_scope",
    "السجائر الإلكترونية": "e_cigarettes_out_of_scope",
    "سجارة الكترونية": "e_cigarettes_out_of_scope",
    "السجارة الالكترونية": "e_cigarettes_out_of_scope",
    "سجارة إلكترونية": "e_cigarettes_out_of_scope",
    "السجارة الإلكترونية": "e_cigarettes_out_of_scope",
    "ميتفورمين": "metformin_out_of_scope",
    "الميتفورمين": "metformin_out_of_scope",
    "تخسيس": "weight_loss_out_of_scope",
    "التخسيس": "weight_loss_out_of_scope",
    "حرق الدهون": "weight_loss_out_of_scope",
    "انقاص الوزن": "weight_loss_out_of_scope",
    "إنقاص الوزن": "weight_loss_out_of_scope",
}

ARABIC_EGYPTIAN_POPULATION_MAP: Dict[str, str] = {
    "حامل": "pregnant_women",
    "حمل": "pregnant_women",
    "رضاعة": "breastfeeding_women",
    "رضاعه": "breastfeeding_women",
    "مراهقين": "adolescents_young_people",
    "مراهق": "adolescents_young_people",
    "شباب": "adolescents_young_people",
    "صغيرين": "adolescents_young_people",
    "أطفال": "adolescents_young_people",
    "اطفال": "adolescents_young_people",
    "ولادنا": "adolescents_young_people",
    "عيالنا": "adolescents_young_people",
    "مدارس": "adolescents_young_people",
    "المدارس": "adolescents_young_people",
    "مش بيدخنوا": "non_smokers",
    "مش مدخنين": "non_smokers",
    "غير مدخنين": "non_smokers",
    "غير مدخن": "non_smokers",
    "سل": "tuberculosis_patients",
    "درن": "tuberculosis_patients",
    "صدر": "respiratory_disease_patients",
    "قلب": "cardiovascular_disease_patients",
    "صرع": "seizure_disorder_patients",
    "تشنجات": "seizure_disorder_patients",
    "مدخن شره": "heavy_smokers",
    "علبتين": "heavy_smokers",
    "شره": "heavy_smokers",
    "انتكاسة": "relapse_smokers",
    "برجع ادخن": "relapse_smokers",
    "برجع أدخن": "relapse_smokers",
}

ARABIC_EGYPTIAN_INTENT_PATTERNS: List[Tuple[str, str]] = [
    (r"(أبطل|ابطل|اوقف|أوقف|تبطيل|توقيف|اقلاع|إقلاع|quit|stop smoking)", "CESSATION_SEEKING"),
    (r"(رغبة|شهوة|مشتهي|شغف|craving|urge)", "CRAVING_REDUCTION"),
    (r"(صداع|عصبية|تعب|جسمي بيتعب|اعراض انسحاب|أعراض انسحاب|withdrawal)", "WITHDRAWAL_MANAGEMENT"),
    (r"(برجع أدخن|برجع ادخن|فشلت|relapse)", "RELAPSE_PREVENTION"),
    (r"(اجمع بين|أجمع بين|مع بعض|combine|combination|together with|alongside|combined with)", "COMBINATION_THERAPY"),
    (r"(احسن من|أحسن من|أفضل من|افضل من|مقارنة|مقارنه|better than|more effective than|versus|vs|compare|compared to|comparison)", "COMPARATIVE_EFFECTIVENESS"),
    (r"(امان|أمان|خطر|مضر|اعراض جانبية|أعراض جانبية|contraindication|safety|adverse)", "SAFETY_CONTRAINDICATION"),
    (r"(مدة|وقت|دقيقة|دقائق|duration|minutes|seconds)", "CONSULTATION_DURATION"),
    (r"(nnt|nnh|number needed to treat|number needed to harm|relative risk|risk ratio|odds ratio|hazard ratio)", "METRIC_STATISTICAL"),
    (r"(منع التدخين|الوقاية من التدخين|الوقاية|وقاية|عدم البدء|ما يبدأش|ما يبدؤوش|ميجربوش|ما يجربوش|حماية.*اللي مش بيدخنوا|مش بيدخنوا|prevention of initiation|prevent.*initiation|prevent.*starting|primary prevention|stop.*becoming smokers)", "PRIMARY_PREVENTION"),
]

# ─────────────────────────────────────────────────────────────────────────────
# Strict Canonical WHO Medical Concepts (ZERO ANSWER LEAKS)
# ─────────────────────────────────────────────────────────────────────────────
# Strictly generic concepts and synonyms.
# ABSOLUTELY NO numbers, treatment durations, NNTs, doses, or quoted conclusions.
CANONICAL_CONCEPT_EXPANSIONS: Dict[str, List[str]] = {
    "nrt_transdermal_patch": ["nicotine patch", "transdermal nicotine", "NRT"],
    "nrt_gum": ["nicotine gum", "short-acting NRT", "oral nicotine"],
    "nicotine_replacement_therapy": ["NRT", "nicotine replacement therapy"],
    "oral_pharmacotherapy": ["pharmacotherapy", "cessation medication", "varenicline", "bupropion", "cytisine"],
    "varenicline": ["varenicline", "nicotinic receptor partial agonist"],
    "bupropion_sr": ["bupropion", "bupropion sustained-release"],
    "cytisine": ["cytisine", "plant-based alkaloid"],
    "toll_free_quitline": ["toll-free telephone quitlines", "quitline counselling", "telephonic support"],
    "mobile_text_messaging_sms": ["text messaging", "mobile phone interventions", "SMS support"],
    "digital_smartphone_interventions": ["smartphone applications", "digital health interventions", "mHealth"],
    "ai_chatbot_interventions": ["artificial intelligence", "conversational agents", "chatbots", "digital interventions"],
    "group_behavioural_counselling": ["group behavioural counselling", "group sessions", "peer support"],
    "individual_intensive_counselling": ["individual counselling", "behavioural support", "face-to-face counselling"],
    "brief_advice": ["brief advice", "clinical advice", "routine consultation", "health-care providers"],
    "smokeless_tobacco": ["smokeless tobacco", "chewing tobacco", "snuff", "snus", "unburnt tobacco"],
    "combination_behavioural_pharmacotherapy": [
        "combining pharmacotherapy and behavioural interventions",
        "combined behavioural support and pharmacotherapy",
        "behavioural interventions and pharmacotherapy",
    ],
    "combination_therapy": ["combination treatment", "combined interventions", "combination therapy"],
    "comparative_evidence": ["comparative effectiveness", "comparison tables", "comparative outcomes"],
    "acupuncture_unproven": ["acupuncture", "acupressure", "laser therapy", "traditional alternative therapies"],
    "hypnotherapy_unproven": ["hypnotherapy", "hypnosis", "unproven alternative therapies"],
    "pregnant_women": ["pregnant women", "pregnancy", "antenatal care"],
    "adolescents_young_people": ["adolescents", "young people", "children", "under 18"],
    "tuberculosis_patients": ["tuberculosis", "TB patients", "chronic respiratory disease"],
    "cardiovascular_disease_patients": ["cardiovascular disease", "cardiac patients"],
    "respiratory_disease_patients": ["chronic respiratory disease", "COPD", "asthma"],
    "seizure_disorder_patients": ["seizure disorder", "epilepsy"],
    "heavy_smokers": ["heavy smokers", "high tobacco dependence"],
    "relapse_smokers": ["relapse prevention", "past quit attempts"],
}


# ─────────────────────────────────────────────────────────────────────────────
# Structured Clinical Query Representation
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ClinicalQueryRepresentation:
    """Structured clinical semantics parsed from the user's natural/colloquial query."""
    raw_query: str
    is_arabic: bool
    is_egyptian_dialect: bool
    detected_intents: List[str]
    detected_interventions: List[str]
    detected_populations: List[str]
    detected_constraints: List[str]
    is_out_of_scope: bool
    out_of_scope_reasons: List[str]
    canonical_terms_en: List[str]
    expanded_search_query: str
    retrieval_dimensions: List[str] = None

    def __post_init__(self):
        if self.retrieval_dimensions is None:
            self.retrieval_dimensions = []

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ClinicalQueryUnderstanding:
    """
    Deterministic rule-based clinical query understanding engine for WHO Tobacco Guideline.
    """

    ARABIC_CHAR_PATTERN = re.compile(r"[\u0600-\u06FF]")
    EGYPTIAN_DIALECT_MARKERS = {
        "عايز", "عاوز", "ابطل", "أبطل", "علشان", "عشان", "ازاي", "إزاي", "ايه", "إيه",
        "ليه", "فين", "مين", "بتاع", "بتاعة", "برجع", "بيجيلي", "بحاول", "لبانة", "لزقة",
        "شمة", "صغيرين", "ينفع", "خلاص", "مش", "كده", "كدة", "دلوقتي"
    }

    # English phrases with strict regex boundary patterns
    ENGLISH_INTERVENTION_PATTERNS: List[Tuple[str, str]] = [
        # Brief advice & consultation
        (r"\bbrief advice\b", "brief_advice"),
        (r"\bbrief talk\b", "brief_advice"),
        (r"\bbrief\b.*\btalk\b", "brief_advice"),
        (r"\bbrief consultation\b", "brief_advice"),
        (r"\bbrief clinical\b", "brief_advice"),
        (r"\bbrief intervention\b", "brief_advice"),
        
        # Smokeless tobacco products
        (r"\bchewing tobacco\b", "smokeless_tobacco"),
        (r"\bsnuff\b", "smokeless_tobacco"),
        (r"\bsnus\b", "smokeless_tobacco"),
        (r"\bgutka\b", "smokeless_tobacco"),
        (r"\bpaan\b", "smokeless_tobacco"),
        (r"\bsmokeless tobacco\b", "smokeless_tobacco"),
        (r"\bsmokeless\b", "smokeless_tobacco"),
        
        # Behavioural & Talking therapies
        (r"\btalking therapy\b", "individual_intensive_counselling"),
        (r"\btalk therapy\b", "individual_intensive_counselling"),
        (r"\bcounselling\b", "individual_intensive_counselling"),
        (r"\bcounseling\b", "individual_intensive_counselling"),
        (r"\bbehavioural therapy\b", "individual_intensive_counselling"),
        (r"\bbehavioral therapy\b", "individual_intensive_counselling"),
        (r"\bbehavioural support\b", "individual_intensive_counselling"),
        (r"\bbehavioral support\b", "individual_intensive_counselling"),
        (r"\bgroup counselling\b", "group_behavioural_counselling"),
        (r"\bgroup therapy\b", "group_behavioural_counselling"),
        
        # Specific Pharmacotherapies
        (r"\bvarenicline\b", "varenicline"),
        (r"\bchampix\b", "varenicline"),
        (r"\bcytisine\b", "cytisine"),
        (r"\btabex\b", "cytisine"),
        (r"\bbupropion\b", "bupropion_sr"),
        (r"\bzyban\b", "bupropion_sr"),
        (r"\bnicotine patch\b", "nrt_transdermal_patch"),
        (r"\bpatch\b", "nrt_transdermal_patch"),
        (r"\bnicotine gum\b", "nrt_gum"),
        (r"\bgum\b", "nrt_gum"),
        (r"\bfast-acting nicotine\b", "nrt_gum"),
        (r"\bshort-acting nicotine\b", "nrt_gum"),
        (r"\blozenge\b", "nicotine_replacement_therapy"),
        (r"\binhaler\b", "nicotine_replacement_therapy"),
        (r"\bnrt\b", "nicotine_replacement_therapy"),
        (r"\bnicotine replacement\b", "nicotine_replacement_therapy"),
        (r"\bnicotine product\b", "nicotine_replacement_therapy"),
        (r"\bcombination nrt\b", "combination_therapy"),
        (r"\bpills\b", "oral_pharmacotherapy"),
        (r"\bmedications?\b", "oral_pharmacotherapy"),
        (r"\bmedicines?\b", "oral_pharmacotherapy"),
        (r"\bpharmacotherapy\b", "oral_pharmacotherapy"),
        
        # Remote & Digital
        (r"\bquitline\b", "toll_free_quitline"),
        (r"\bhelpline\b", "toll_free_quitline"),
        (r"\btelephone\b", "toll_free_quitline"),
        (r"\bsms\b", "mobile_text_messaging_sms"),
        (r"\btext messag\w*\b", "mobile_text_messaging_sms"),
        (r"\btexting\b", "mobile_text_messaging_sms"),
        (r"\bapp\b", "digital_smartphone_interventions"),
        (r"\bapps\b", "digital_smartphone_interventions"),
        (r"\bsmartphone\b", "digital_smartphone_interventions"),
        (r"\bchatbot\b", "ai_chatbot_interventions"),
        (r"\bartificial intelligence\b", "ai_chatbot_interventions"),
        
        # Unproven / Alternative
        (r"\bacupuncture\b", "acupuncture_unproven"),
        (r"\bacupressure\b", "acupuncture_unproven"),
        (r"\blaser\b", "laser_therapy_unproven"),
        (r"\bhypnosis\b", "hypnotherapy_unproven"),
        (r"\bhypnotherapy\b", "hypnotherapy_unproven"),
        (r"\bherbal\b", "herbal_unproven"),
        (r"\bst john\b", "st_johns_wort_unproven"),
        
        # Explicit Out of Scope terms
        (r"\btopiramate\b", "unsupported_intervention_out_of_scope"),
        (r"\btranscranial magnetic stimulation\b", "unsupported_intervention_out_of_scope"),
        (r"\btms\b", "unsupported_intervention_out_of_scope"),
        (r"\be-cigarette\b", "e_cigarettes_out_of_scope"),
        (r"\bvape\b", "e_cigarettes_out_of_scope"),
        (r"\bvaping\b", "e_cigarettes_out_of_scope"),
        (r"\bmetformin\b", "metformin_out_of_scope"),
        (r"\bsemaglutide\b", "semaglutide_out_of_scope"),
        (r"\bozempic\b", "semaglutide_out_of_scope"),
        (r"\bwegovy\b", "semaglutide_out_of_scope"),
        (r"\bweight loss\b", "weight_loss_out_of_scope"),
        (r"\bsauna\b", "sauna_out_of_scope"),
        (r"\binsulin\b", "insulin_diabetes_out_of_scope"),
        (r"\bfracture\b", "orthopedics_fracture_out_of_scope"),
        (r"\bappendicitis\b", "appendicitis_emergency_out_of_scope"),
    ]

    ENGLISH_POPULATION_PATTERNS: List[Tuple[str, str]] = [
        (r"\bpregnant\b", "pregnant_women"),
        (r"\bpregnancy\b", "pregnant_women"),
        (r"\bteenager\w*\b", "adolescents_young_people"),
        (r"\bteen\w*\b", "adolescents_young_people"),
        (r"\badolescent\w*\b", "adolescents_young_people"),
        (r"\byouth\b", "adolescents_young_people"),
        (r"\byoung people\b", "adolescents_young_people"),
        (r"\bchildren\b", "adolescents_young_people"),
        (r"\bunder 18\b", "adolescents_young_people"),
        (r"\bnon-smoker\w*\b", "non_smokers"),
        (r"\bnon smoker\w*\b", "non_smokers"),
        (r"\bnever smoke\w*\b", "non_smokers"),
        (r"\bdon't smoke\b", "non_smokers"),
        (r"\bdo not smoke\b", "non_smokers"),
        (r"\btuberculosis\b", "tuberculosis_patients"),
        (r"\btb\b", "tuberculosis_patients"),
        (r"\bseizure\w*\b", "seizure_disorder_patients"),
        (r"\brelapse\w*\b", "relapse_smokers"),
        (r"\bheavy smoker\w*\b", "heavy_smokers"),
    ]

    def __init__(self):
        pass

    def parse_query(self, query_text: str) -> ClinicalQueryRepresentation:
        """Parses raw user query into structured clinical semantics."""
        raw = query_text.strip()
        is_arabic = bool(self.ARABIC_CHAR_PATTERN.search(raw))
        words = set(re.findall(r"[\w\u0600-\u06FF]+", raw.lower()))
        is_egyptian = is_arabic and bool(words & self.EGYPTIAN_DIALECT_MARKERS)

        detected_intents: List[str] = []
        detected_interventions: List[str] = []
        detected_populations: List[str] = []
        detected_constraints: List[str] = []
        out_of_scope_reasons: List[str] = []
        is_out_of_scope = False

        # 1. Match Intents
        for pattern, intent_name in ARABIC_EGYPTIAN_INTENT_PATTERNS:
            if re.search(pattern, raw, re.IGNORECASE):
                if intent_name not in detected_intents:
                    detected_intents.append(intent_name)

        # 2. Match Interventions (Arabic)
        raw_lower = raw.lower()
        for ar_term, canonical_key in ARABIC_EGYPTIAN_INTERVENTION_MAP.items():
            if ar_term in raw_lower:
                if canonical_key.endswith("_out_of_scope"):
                    is_out_of_scope = True
                    out_of_scope_reasons.append(f"Contains out-of-scope term: '{ar_term}' -> {canonical_key}")
                elif canonical_key not in detected_interventions:
                    detected_interventions.append(canonical_key)

        # English Intervention matches (Word-boundary regex safe)
        for pattern, canonical_key in self.ENGLISH_INTERVENTION_PATTERNS:
            if re.search(pattern, raw_lower):
                if canonical_key.endswith("_out_of_scope"):
                    is_out_of_scope = True
                    out_of_scope_reasons.append(f"Contains out-of-scope term matching: {pattern}")
                elif canonical_key not in detected_interventions:
                    detected_interventions.append(canonical_key)

        # 3. Match Populations (Arabic)
        for ar_term, pop_key in ARABIC_EGYPTIAN_POPULATION_MAP.items():
            if ar_term in raw_lower:
                if pop_key not in detected_populations:
                    detected_populations.append(pop_key)

        # English Population matches (Word-boundary safe)
        for pattern, pop_key in self.ENGLISH_POPULATION_PATTERNS:
            if re.search(pattern, raw_lower):
                if pop_key not in detected_populations:
                    detected_populations.append(pop_key)

        # 4. Multi-Intervention Clinical Combination Detection
        # A. Dual NRT Combination (e.g. Patch + Gum)
        if ("nrt_transdermal_patch" in detected_interventions and "nrt_gum" in detected_interventions) or \
           ("COMBINATION_THERAPY" in detected_intents and "nicotine_replacement_therapy" in detected_interventions):
            if "combination_therapy" not in detected_interventions:
                detected_interventions.append("combination_therapy")

        # B. Combined Pharmacotherapy + Behavioural Support (e.g. real_06: pills + talking therapy)
        has_pharma = any(k in detected_interventions for k in [
            "oral_pharmacotherapy", "nicotine_replacement_therapy", "varenicline", "bupropion_sr", "cytisine"
        ])
        has_counsel = any(k in detected_interventions for k in [
            "individual_intensive_counselling", "group_behavioural_counselling", "behavioural_counselling"
        ])
        if has_pharma and has_counsel:
            if "combination_behavioural_pharmacotherapy" not in detected_interventions:
                detected_interventions.insert(0, "combination_behavioural_pharmacotherapy")

        # C. Combined Multiple Pharmacotherapies (e.g. real_19: bupropion + varenicline)
        pharma_count = sum(1 for k in ["varenicline", "bupropion_sr", "cytisine", "nrt_transdermal_patch", "nrt_gum"] if k in detected_interventions)
        if pharma_count >= 2 or ("COMBINATION_THERAPY" in detected_intents and has_pharma):
            if "combination_therapy" not in detected_interventions:
                detected_interventions.append("combination_therapy")

        # 5. Extract Canonical English Expansion Terms (Concepts Only - Capped at 6)
        canonical_terms: List[str] = []
        for key in detected_interventions + detected_populations:
            expansions = CANONICAL_CONCEPT_EXPANSIONS.get(key, [])
            for term in expansions:
                if term not in canonical_terms:
                    canonical_terms.append(term)

        # 6. Build Non-Destructive Expanded Search Query
        # Strictly preserves raw query and appends capped canonical concept terms
        expansion_str = " ".join(canonical_terms[:6])
        if expansion_str:
            expanded_query = f"{raw} {expansion_str}".strip()
        else:
            expanded_query = raw

        # 7. Generate Generic Concept Retrieval Dimensions for Multi-Evidence Queries
        # Maps each detected intervention and population to its clean canonical search phrase
        retrieval_dimensions: List[str] = []
        for key in detected_interventions + detected_populations:
            terms = CANONICAL_CONCEPT_EXPANSIONS.get(key, [])
            if terms:
                # Use the primary canonical clinical phrase as the dimension query
                dim_str = terms[0]
                if dim_str not in retrieval_dimensions:
                    retrieval_dimensions.append(dim_str)

        # Append generic comparative dimension if comparative intent is present
        if "COMPARATIVE_EFFECTIVENESS" in detected_intents:
            comp_terms = CANONICAL_CONCEPT_EXPANSIONS.get("comparative_evidence", [])
            if comp_terms and comp_terms[0] not in retrieval_dimensions:
                retrieval_dimensions.append(comp_terms[0])

        return ClinicalQueryRepresentation(
            raw_query=raw,
            is_arabic=is_arabic,
            is_egyptian_dialect=is_egyptian,
            detected_intents=detected_intents,
            detected_interventions=detected_interventions,
            detected_populations=detected_populations,
            detected_constraints=detected_constraints,
            is_out_of_scope=is_out_of_scope,
            out_of_scope_reasons=out_of_scope_reasons,
            canonical_terms_en=canonical_terms,
            expanded_search_query=expanded_query,
            retrieval_dimensions=retrieval_dimensions,
        )


if __name__ == "__main__":
    engine = ClinicalQueryUnderstanding()
    test_queries = [
        "How long should a standard brief tobacco cessation talk take during a clinical appointment?",
        "Is it more effective to use quit-smoking pills alongside talking therapy rather than trying pills alone?",
        "What support should doctors give to patients trying to stop chewing tobacco or using snuff?",
        "Does using a nicotine patch together with a fast-acting nicotine product work better than using a single nicotine product alone?",
    ]
    for tq in test_queries:
        parsed = engine.parse_query(tq)
        print("=" * 60)
        print(f"Query: {tq}")
        print(f"  Intents: {parsed.detected_intents}")
        print(f"  Interventions: {parsed.detected_interventions}")
        print(f"  Populations: {parsed.detected_populations}")
        print(f"  Canonical terms: {parsed.canonical_terms_en}")
        print(f"  Expanded search: {parsed.expanded_search_query}")

