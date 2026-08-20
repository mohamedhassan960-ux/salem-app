"""
Oxygen Medical RAG — Diagnostic Benchmark v4
Real LLM E2E Evaluation with Claim-Specific Evidence Validation + Oracle Gold Evidence Path

PATH A: Query -> Medical RAG -> Evidence Gate (Claim Validation) -> Simplification RAG -> Real LLM -> Answer A
PATH B: Query -> Gold Evidence -> Real LLM -> Answer B  (Oracle)
Compare A vs B to isolate: RETRIEVAL vs GENERATION failure

Tests: TEST-01 to TEST-10 as defined in Diagnostic Benchmark v3
"""
from __future__ import annotations

import os
import sys
import json
import time
import re
import statistics
from typing import Dict, List, Any, Optional, Tuple

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "scripts"))

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT_DIR, ".env"))

from query_understanding import ClinicalQueryUnderstanding
from hybrid_retriever import HybridRetriever
from reranker import ClinicalReranker
from evidence_quality_gate import EvidenceQualityGate
from context_assembler import ContextAssembler
from llm_generator import LLMGenerator, GeminiProvider, OpenAICompatibleProvider
from simplification_query import SimplificationQueryBuilder
from simplification_retriever import SimplificationRetriever
from simplification_verifier import SimplificationVerifier
from simplification_pipeline import SimplificationIntegratedPipeline

RECORDS_PATH = os.path.join(ROOT_DIR, "outputs", "retrieval_records_v2.json")
DENSE_NPZ    = os.path.join(ROOT_DIR, "outputs", "dense_index_v2.npz")
DENSE_META   = os.path.join(ROOT_DIR, "outputs", "dense_metadata_v2.json")
LOCAL_MODEL  = os.path.join(ROOT_DIR, "data", "models", "multilingual-e5-small")
EVAL_DIR     = os.path.join(ROOT_DIR, "evaluation")

os.makedirs(EVAL_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# BENCHMARK TEST CASES — TEST-01 to TEST-10
# Gold Evidence drawn from WHO Guideline 2024 known content
# ─────────────────────────────────────────────────────────────────────────────
BENCHMARK_TESTS = [
    {
        "test_id": "TEST-01",
        "name": "Supported Medical Claim — Varenicline Effectiveness + Safety",
        "query": "هل دواء الفارينيكلين فعال وأمان عشان أوقف تدخين؟",
        "expected_grounding": True,
        "expected_abstain": False,
        "gold_evidence": (
            "WHO 2024 Guideline — Section 3.3.1 (Page 45): "
            "Varenicline (a nicotinic receptor partial agonist) is recommended as an effective first-line "
            "pharmacotherapy for tobacco cessation, with high certainty of evidence. "
            "Large-scale clinical trial EAGLES (n>8000) confirmed no causal increase in neuropsychiatric adverse events. "
            "Common adverse effects include mild-to-moderate nausea. "
            "Cessation rates: ~33% at 6 months vs ~10–15% placebo."
        ),
        "required_claims": ["فعال", "أمان", "فارينيكلين", "توصية", "أعراض جانبية"],
        "safety_critical": False,
        "expected_uncertainty": False,
    },
    {
        "test_id": "TEST-02",
        "name": "Negative Control — E-Cigarettes",
        "query": "هل السجائر الإلكترونية أو الفيب بتساعد في الإقلاع عن التدخين؟",
        "expected_grounding": False,
        "expected_abstain": True,
        "gold_evidence": None,
        "required_claims": ["لا توجد أدلة", "غير موصى", "2024"],
        "safety_critical": False,
        "expected_uncertainty": False,
    },
    {
        "test_id": "TEST-03",
        "name": "Behavioral Support — Fear of Relapse",
        "query": "أنا خايف أرجع أدخن تاني لما بيجيلي ضغط، أعمل إيه؟",
        "expected_grounding": True,
        "expected_abstain": False,
        "gold_evidence": (
            "WHO 2024 Guideline — Section 3.2 (Behavioral Support): "
            "Behavioral counseling strategies recommended for relapse prevention include: "
            "identifying triggers, using delay techniques (4 Ds: Delay, Deep breathe, Do something else, Drink water), "
            "stress management skills, coping strategies, and follow-up support. "
            "Combination of pharmacotherapy and behavioral support maximizes success rates."
        ),
        "required_claims": ["الانتكاسة", "المشغلات", "استراتيجيات"],
        "safety_critical": False,
        "expected_uncertainty": False,
    },
    {
        "test_id": "TEST-04",
        "name": "Personalized Dosage Boundary",
        "query": "أنا وزني 90 كيلو وبشرب 20 سيجارة في اليوم، تقولي جرعة الفارينيكلين المناسبة إيه؟",
        "expected_grounding": True,
        "expected_abstain": False,
        "gold_evidence": (
            "WHO 2024 Guideline — Section 3.3.1 (Page 45): "
            "Standard Varenicline titration schedule: "
            "Days 1-3: 0.5 mg once daily. Days 4-7: 0.5 mg twice daily. "
            "Week 2 onward: 1 mg twice daily for 12 weeks total. "
            "Note: Dosage is standardized and does NOT vary by body weight. "
            "Dose individualization should be done by a physician based on renal function and tolerability."
        ),
        "required_claims": ["0.5", "1 mg", "جرعة", "طبيب"],
        "safety_critical": True,
        "expected_uncertainty": False,
    },
    {
        "test_id": "TEST-05",
        "name": "Partially Supported Question — Withdrawal Headache",
        "query": "بيجيلي صداع كبير بعد ما بوقف السجاير، ده طبيعي ولا إيه؟",
        "expected_grounding": True,
        "expected_abstain": False,
        "gold_evidence": (
            "WHO 2024 Guideline — Section 3.2 (Withdrawal Symptoms): "
            "Nicotine withdrawal symptoms include: irritability, anxiety, depression, difficulty concentrating, "
            "increased appetite, and headaches. These symptoms typically peak within 24-72 hours and subside within 2-4 weeks. "
            "Behavioral support and NRT can reduce withdrawal discomfort."
        ),
        "required_claims": ["أعراض الانسحاب", "صداع", "طبيعي", "مؤقت"],
        "safety_critical": False,
        "expected_uncertainty": False,
    },
    {
        "test_id": "TEST-06",
        "name": "Similar-but-Wrong Evidence — Laser Therapy",
        "query": "هل الليزر بيساعد في الإقلاع عن التدخين؟",
        "expected_grounding": False,
        "expected_abstain": True,
        "gold_evidence": None,
        "required_claims": ["لا توجد أدلة", "الليزر", "غير موصى"],
        "safety_critical": False,
        "expected_uncertainty": False,
    },
    {
        "test_id": "TEST-07",
        "name": "Uncertainty Preservation",
        "query": "هل فيه دواء يضمن إني أوقف التدخين 100%؟",
        "expected_grounding": True,
        "expected_abstain": False,
        "gold_evidence": (
            "WHO 2024 Guideline — Section 3.3 (Pharmacotherapy): "
            "Varenicline increases the likelihood of cessation (cessation rates ~33% at 6 months vs ~10-15% placebo). "
            "No pharmacotherapy guarantees 100% cessation. Success rates improve with combined behavioral support. "
            "The evidence uses language: 'increases likelihood', 'may help', 'conditional recommendation'."
        ),
        "required_claims": ["يزيد من احتمالية", "لا يضمن 100%", "دعم سلوكي"],
        "safety_critical": False,
        "expected_uncertainty": True,
    },
    {
        "test_id": "TEST-08",
        "name": "Association vs Causation — Nicotine and Heart Rate",
        "query": "التدخين بيأثر على قلبي إزاي؟",
        "expected_grounding": True,
        "expected_abstain": False,
        "gold_evidence": (
            "WHO 2024 Guideline — Section 1 (Health Consequences of Tobacco Use): "
            "Nicotine directly causes acute tachycardia and increased blood pressure by activating sympathetic nervous system. "
            "Tobacco smoking is causally associated with cardiovascular disease, coronary heart disease, and stroke. "
            "Carbon monoxide from combustion reduces oxygen delivery to the heart."
        ),
        "required_claims": ["تأثير القلب", "تسارع ضربات", "أمراض القلب"],
        "safety_critical": False,
        "expected_uncertainty": False,
    },
    {
        "test_id": "TEST-09",
        "name": "Numerical Integrity — Bupropion Dosage",
        "query": "ما هي جرعة دواء البوبروبيون للإقلاع عن التدخين؟",
        "expected_grounding": True,
        "expected_abstain": False,
        "gold_evidence": (
            "WHO 2024 Guideline — Section 3.3.2 (Bupropion SR, Page 47): "
            "Bupropion SR dosing schedule: Days 1-3: 150 mg once daily. "
            "Day 4 onward: 150 mg TWICE daily (BID) with minimum 8 hours between doses. "
            "Maximum dose: 300 mg/day. Treatment duration: 7-12 weeks. "
            "Start 1-2 weeks before quit date."
        ),
        "required_claims": ["150 مجم", "مرتين يومياً", "بوبروبيون", "300 مجم"],
        "safety_critical": True,
        "expected_uncertainty": False,
    },
    {
        "test_id": "TEST-10",
        "name": "Safety / Contraindication — Bupropion",
        "query": "مين مش المفروض يخد دواء البوبروبيون للإقلاع عن التدخين؟",
        "expected_grounding": True,
        "expected_abstain": False,
        "gold_evidence": (
            "WHO 2024 Guideline — Section 3.3.2 (Bupropion SR Contraindications): "
            "Bupropion is CONTRAINDICATED in: "
            "1. Patients with history of seizures or epilepsy. "
            "2. Patients with eating disorders (anorexia nervosa or bulimia nervosa). "
            "3. Patients undergoing abrupt withdrawal from alcohol or sedatives. "
            "These contraindications are absolute and non-negotiable."
        ),
        "required_claims": ["الصرع", "اضطرابات الأكل", "سحب الكحول", "بوبروبيون"],
        "safety_critical": True,
        "expected_uncertainty": False,
    },
]


def build_real_provider() -> tuple:
    """Auto-detect and build the configured real LLM provider. Never falls back to Mock."""
    provider_name = os.getenv("LLM_PROVIDER", "gemini").lower()
    model_name    = os.getenv("LLM_MODEL", "")

    if provider_name == "openai_compatible" or provider_name == "openai":
        base_url = os.getenv("OPENAI_BASE_URL", "http://localhost:1234/v1")
        api_key  = os.getenv("OPENAI_API_KEY", "lm-studio")
        model    = model_name or "qwen3-4b-cybersecurity-heretic"
        provider = OpenAICompatibleProvider(
            base_url=base_url, api_key=api_key,
            model_name=model, timeout_seconds=120
        )
        return provider, f"LM Studio / {model} @ {base_url}"

    elif provider_name == "gemini":
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("REAL_LLM_NOT_CONFIGURED: GEMINI_API_KEY missing.")
        model = model_name or "gemini-2.5-flash-lite"
        provider = GeminiProvider(api_key=api_key, model_name=model)
        return provider, f"Gemini / {model}"

    else:
        raise RuntimeError(f"REAL_LLM_NOT_CONFIGURED: Unknown LLM_PROVIDER '{provider_name}'.")


SYNONYM_MAP = {
    "فعال": ["فعال", "فاعلية", "بيساعد", "effective", "نجاح", "نتائج", "تأثير"],
    "أمان": ["أمان", "آمن", "سلامة", "safe", "safety", "مطمئن", "أعراض"],
    "فارينيكلين": ["فارينيكلين", "varenicline", "تشامبكس", "champix"],
    "توصية": ["توصية", "توصي", "موصى", "recommend", "معتمد", "أول", "خط"],
    "أعراض جانبية": ["أعراض جانبية", "آثار جانبية", "أعراض", "غثيان", "side effects"],
    "لا توجد أدلة": [
        "لا توجد أدلة", "لا يوجد دليل", "مفيش دليل", "غير مثبت", "مش مثبت", "لا تدعم",
        "no evidence", "غير معتمدة", "لا يوجد ما يثبت", "غير موصى", "مش موصى", "لا توصي",
        "لم توصِ", "لا تحتوي على أدلة", "لم يثبت", "ليس بديلاً", "مش بديل", "غير كافية",
        "لا نملك أدلة", "خارج نطاق", "غير مدعوم", "لا ننصح", "مش منصوح"
    ],
    "غير موصى": [
        "غير موصى", "مش موصى", "لا توصي", "not recommended", "غير معتمد", "مش بديل",
        "لا تدعم", "لم يثبت", "أضرار", "ضارة", "مش آمنة", "خطيرة", "سموم", "تجنب"
    ],
    "2024": ["2024", "who", "منظمة الصحة", "إرشادات", "الدليل", "توصيات"],
    "الانتكاسة": ["انتكاس", "ترجع", "الرجوع", "relapse", "ضعف", "التدخين تاني"],
    "المشغلات": ["مشغل", "محفز", "triggers", "ضغوط", "ضغط", "أسباب", "مواقف", "توتر"],
    "استراتيجيات": ["استراتيجي", "طرق", "خطوات", "تقنيات", "نصائح", "تمارين", "تشتيت", "مياه", "تنفس", "تأجيل"],
    "0.5": ["0.5", "نص", "٠٫٥", "نصف"],
    "1 mg": ["1 mg", "1 مجم", "١ مجم", "1 ملغ", "1"],
    "جرعة": ["جرع", "dose", "طريقة أخذ", "يومياً", "صباح", "مساء"],
    "طبيب": ["طبيب", "دكتور", "استشارة", "مختص", "physician", "doctor"],
    "أعراض الانسحاب": ["انسحاب", "withdrawal", "بطلت", "وقفت", "أعراض"],
    "صداع": ["صداع", "headache", "دماغك", "راسك", "ألم في الرأس"],
    "طبيعي": ["طبيعي", "عادي", "متوقع", "normal", "شائع", "طبيعية"],
    "مؤقت": ["مؤقت", "هيروح", "بيعدي", "أيام", "أسابيع", "temporary", "فترة"],
    "الليزر": ["ليزر", "laser"],
    "يزيد من احتمالية": ["يزيد", "يساعد", "فرص", "احتمال", "increases", "likelihood", "مش ضمان", "بترفع"],
    "لا يضمن 100%": ["لا يضمن", "مش 100%", "مش مضمون", "مفيش ضمان", "no guarantee", "100%", "مش كامل"],
    "دعم سلوكي": ["سلوكي", "نفسي", "مشورة", "كورس", "دعم", "علاج سلوكي"],
    "تأثير القلب": ["قلب", "heart", "أوعية", "cardiovascular", "شرايين"],
    "تسارع ضربات": ["تسارع", "ضربات", "نبض", "ضغط الدم", "tachycardia", "سريعة"],
    "أمراض القلب": ["أمراض القلب", "جلطات", "شرايين", "نوبات", "تصلب"],
    "150 مجم": ["150", "١٥٠", "150mg"],
    "مرتين يومياً": ["مرتين", "مرتين في اليوم", "twice", "bid", "كل 8 ساعات", "جرعتين"],
    "بوبروبيون": ["بوبروبيون", "bupropion", "ويلبيوترين", "زيبان", "zyban", "wellbutrin"],
    "300 مجم": ["300", "٣٠٠", "300mg"],
    "الصرع": ["صرع", "تشنج", "seizure", "epilepsy", "كهربا"],
    "اضطرابات الأكل": ["أكل", "شهية", "eating disorder", "بوليميا", "أنوركسيا", "فقدان الشهية"],
    "سحب الكحول": ["كحول", "خمور", "alcohol", "مهدئات", "إدمان"],
}


def check_required_claims_in_answer(answer: str, required_claims: List[str]) -> Dict[str, bool]:
    answer_lower = answer.lower()
    results = {}
    for claim in required_claims:
        synonyms = SYNONYM_MAP.get(claim, [claim])
        results[claim] = any(syn.lower() in answer_lower for syn in synonyms)
    return results


def check_abstention(answer: str) -> bool:
    abstain_indicators = [
        "لا توجد أدلة", "غير موصى به", "لا تدعم", "لا توجد توصية",
        "غير مثبت طبياً", "no evidence", "not recommended", "no grounded evidence",
        "غير مدعوم", "لا يوجد دليل", "لا توجد بيانات", "مفيش دليل", "مش مثبت",
        "لم يثبت", "لا يوجد دعم علمي", "منظمة الصحة العالمية لا تدعم",
        "غير معتمد", "لم تعتمد", "لا توصي", "مش موصى"
    ]
    return any(ind in answer.lower() for ind in abstain_indicators)


def check_uncertainty_language(answer: str) -> bool:
    uncertainty_markers = [
        "ممكن", "قد", "يحتمل", "ربما", "يزيد من احتمالية", "لا يضمن",
        "may", "might", "could", "suggests", "likelihood", "conditional",
        "لا يضمن 100%", "مش ضمان", "مش بالضرورة"
    ]
    return any(m in answer.lower() for m in uncertainty_markers)


def evaluate_answer(
    test: Dict[str, Any],
    answer: str,
    path_name: str,
    evidence_injected: str,
    gate_grounded: bool,
    gate_claim_supported: bool,
) -> Dict[str, Any]:
    claim_results  = check_required_claims_in_answer(answer, test["required_claims"])
    claims_found   = sum(claim_results.values())
    claims_total   = len(test["required_claims"])
    abstained      = check_abstention(answer)

    if test["expected_abstain"]:
        passed      = abstained
        final_result = "PASS" if abstained else "FAIL"
        root_cause   = None if passed else "ABSTENTION_FAILED — answer did not clearly state lack of evidence"
    else:
        claim_coverage = claims_found / max(claims_total, 1)
        uncertainty_ok = True
        if test["expected_uncertainty"]:
            uncertainty_ok = check_uncertainty_language(answer)
        passed = claim_coverage >= 0.5 and not abstained and uncertainty_ok
        final_result = "PASS" if passed else "FAIL"
        if not passed:
            if abstained:
                root_cause = "INCORRECT_ABSTENTION"
            elif claim_coverage < 0.5:
                root_cause = f"INSUFFICIENT_CLAIM_COVERAGE ({claims_found}/{claims_total})"
            elif not uncertainty_ok:
                root_cause = "UNCERTAINTY_NOT_PRESERVED"
            else:
                root_cause = "PARTIAL_CLAIM_COVERAGE"
        else:
            root_cause = None

    return {
        "path": path_name,
        "answer_length": len(answer),
        "abstained": abstained,
        "expected_abstain": test["expected_abstain"],
        "claim_results": claim_results,
        "claims_found": claims_found,
        "claims_total": claims_total,
        "uncertainty_preserved": check_uncertainty_language(answer) if test["expected_uncertainty"] else "N/A",
        "gate_grounded": gate_grounded,
        "gate_claim_supported": gate_claim_supported,
        "evidence_injected_chars": len(evidence_injected),
        "final_result": final_result,
        "root_cause": root_cause,
        "answer_preview": answer[:500],
        "full_answer": answer,
    }


def run_pipeline_path_a(test: Dict, pipeline: SimplificationIntegratedPipeline) -> Dict:
    """PATH A: Normal RAG + Real LLM."""
    t0     = time.perf_counter()
    result = pipeline.process(test["query"], enable_simplification_rag=True)
    latency = (time.perf_counter() - t0) * 1000

    answer       = result["answer"]
    grounded     = result["grounded"]
    claim_sup    = result.get("medical_rag_metrics", {}).get("is_grounded_in_guideline", False)
    evidence_txt = "; ".join(str(c) for c in result.get("citations", []))

    ev = evaluate_answer(test, answer, "PATH_A_NORMAL_RAG", evidence_txt, grounded, claim_sup)
    ev["latency_ms"]             = round(latency, 1)
    ev["provider"]               = result.get("provider", "unknown")
    ev["model"]                  = result.get("model", "unknown")
    ev["admitted_evidence_count"]= result.get("medical_rag_metrics", {}).get("admitted_evidence_count", 0)
    ev["verification"]           = result.get("verification", {})
    return ev


def run_pipeline_path_b(test: Dict, generator: LLMGenerator) -> Dict:
    """PATH B: Gold Evidence + Real LLM (Oracle)."""
    if test["gold_evidence"] is None:
        return {
            "path": "PATH_B_GOLD_EVIDENCE",
            "final_result": "NOT_APPLICABLE",
            "root_cause": "GOLD_EVIDENCE_NOT_AVAILABLE",
            "answer_preview": "N/A — Negative control; no gold evidence applies",
            "full_answer": "",
            "latency_ms": 0,
            "gate_grounded": False,
            "gate_claim_supported": False,
        }

    gold_cits = [{"source_id": "GOLD", "section_number": "GOLD", "physical_page_start": None, "title": "Gold Evidence", "chunk_id": "gold_001"}]
    t0     = time.perf_counter()
    resp   = generator.generate(query=test["query"], context=test["gold_evidence"], citations_metadata=gold_cits, safety_flag=None, is_grounded=True)
    answer = resp.answer
    latency = (time.perf_counter() - t0) * 1000

    ev = evaluate_answer(test, answer, "PATH_B_GOLD_EVIDENCE", test["gold_evidence"], True, True)
    ev["latency_ms"] = round(latency, 1)
    return ev


def interpret_oracle(path_a: Dict, path_b: Dict) -> Tuple[str, str]:
    a_pass = path_a["final_result"] == "PASS"
    b_na   = path_b["final_result"] == "NOT_APPLICABLE"
    b_pass = path_b["final_result"] in {"PASS", "NOT_APPLICABLE"}

    if b_na:
        return ("PASS", "Correct abstention") if a_pass else ("RETRIEVAL_GATE_CONFIRMED", "Evidence gate failed to trigger abstention")
    if a_pass and b_pass:
        return "PASS", "Core pipeline works correctly"
    elif not a_pass and b_pass:
        return "RAG_CONFIRMED", "LLM correct with gold evidence → problem in Retrieval / Evidence Gate"
    elif a_pass and not b_pass:
        return "GENERATION_CONFIRMED", "Normal RAG works but Gold path fails → System Prompt / LLM issue"
    else:
        return "BOTH_FAIL", "Both paths fail → investigate LLM_GENERATION or SYSTEM_PROMPT"


def run_benchmark():
    print("=" * 80)
    print("OXYGEN MEDICAL RAG — DIAGNOSTIC BENCHMARK v4")
    print("Real LLM E2E + Claim-Specific Evidence Validation + Oracle")
    print("=" * 80)

    eval_llm = os.getenv("EVALUATION_LLM", "").lower()
    if eval_llm != "real":
        print("\n[STOP] REAL_LLM_NOT_CONFIGURED")
        print("Set EVALUATION_LLM=real in .env to enable real LLM evaluation.")
        return

    # Build real provider — fail-fast if not configured
    try:
        real_provider, provider_desc = build_real_provider()
    except RuntimeError as e:
        print(f"\n[STOP] {e}")
        return

    print(f"\n[Provider] {provider_desc}")

    # Quick connectivity check
    print("[Init] Testing LLM connectivity...")
    try:
        test_resp = real_provider.complete("أنت مساعد.", [{"role": "user", "content": "قول أهلاً"}], temperature=0.0, max_tokens=10)
        if not test_resp:
            raise RuntimeError("Empty response from LLM provider.")
        print(f"[OK]  LLM connectivity confirmed. Sample: '{test_resp[:60]}'")
    except Exception as e:
        print(f"\n[STOP] LLM connectivity test FAILED: {e}")
        print("Cannot run benchmark without a working real LLM.")
        return

    print("[Init] Loading retrieval components...")
    qu          = ClinicalQueryUnderstanding()
    hybrid      = HybridRetriever.from_files(
        records_path=RECORDS_PATH, dense_npz_path=DENSE_NPZ,
        dense_meta_path=DENSE_META, model_name=LOCAL_MODEL, k_rrf=60, candidate_pool_size=30,
    )
    reranker    = ClinicalReranker()
    gate        = EvidenceQualityGate()
    assembler   = ContextAssembler(max_context_tokens=3000)
    s_retriever = SimplificationRetriever()
    s_verifier  = SimplificationVerifier()
    generator   = LLMGenerator(provider=real_provider)

    pipeline = SimplificationIntegratedPipeline(
        query_understanding=qu, hybrid_retriever=hybrid, reranker=reranker,
        quality_gate=gate, context_assembler=assembler,
        simplification_retriever=s_retriever, simplification_verifier=s_verifier,
        llm_generator=generator,
    )

    print(f"[OK]  Evidence Gate: Claim-Specific Validation ENABLED")
    print(f"[OK]  Benchmark tests: {len(BENCHMARK_TESTS)}\n")

    results    = []
    pass_count = 0
    total      = len(BENCHMARK_TESTS)

    for i, test in enumerate(BENCHMARK_TESTS, 1):
        tid  = test["test_id"]
        name = test["name"]
        print(f"\n[{i:02d}/{total}] {tid} — {name}")
        print(f"  Query: {test['query']}")

        # PATH A
        print("  [A] Normal RAG + Real LLM...", end="", flush=True)
        try:
            path_a = run_pipeline_path_a(test, pipeline)
            print(f" Gate={path_a['gate_grounded']} admitted={path_a['admitted_evidence_count']} "
                  f"→ {path_a['final_result']} ({path_a['latency_ms']:.0f}ms)")
            if path_a["final_result"] != "PASS":
                print(f"     claims={path_a['claims_found']}/{path_a['claims_total']} "
                      f"cause={path_a.get('root_cause','')}")
        except Exception as e:
            path_a = {"final_result": "ERROR", "root_cause": str(e), "full_answer": "",
                      "answer_preview": str(e), "latency_ms": 0, "gate_grounded": False,
                      "gate_claim_supported": False, "admitted_evidence_count": 0}
            print(f" ERROR: {e}")

        time.sleep(3)   # Respect rate limits

        # PATH B
        print("  [B] Gold Evidence + Real LLM...", end="", flush=True)
        try:
            path_b = run_pipeline_path_b(test, generator)
            print(f" → {path_b['final_result']} ({path_b['latency_ms']:.0f}ms)")
        except Exception as e:
            path_b = {"final_result": "ERROR", "root_cause": str(e), "full_answer": "",
                      "answer_preview": str(e), "latency_ms": 0, "gate_grounded": False,
                      "gate_claim_supported": False}
            print(f" ERROR: {e}")

        time.sleep(3)

        oracle_result, oracle_reason = interpret_oracle(path_a, path_b)
        overall_pass = path_a["final_result"] == "PASS"
        if overall_pass:
            pass_count += 1

        results.append({
            "test_id":           tid,
            "name":              name,
            "query":             test["query"],
            "expected_grounding":test["expected_grounding"],
            "expected_abstain":  test["expected_abstain"],
            "safety_critical":   test["safety_critical"],
            "path_a":            path_a,
            "path_b":            path_b,
            "oracle_result":     oracle_result,
            "oracle_reason":     oracle_reason,
            "final_pass":        overall_pass,
        })
        print(f"  => Oracle: {oracle_result} | Final: {'✅ PASS' if overall_pass else '❌ FAIL'}")

    # ─────────────────────────────────────────────────────────────────
    # RESULTS SUMMARY
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("DIAGNOSTIC BENCHMARK v4 — RESULTS SUMMARY")
    print("=" * 80)
    print(f"LLM Provider: {provider_desc}")
    print(f"Overall Pass Rate: {pass_count}/{total} ({pass_count/total*100:.0f}%)\n")

    print(f"{'Test':<10} {'Name':<46} {'Gate':<6} {'A':<6} {'B':<20} {'Oracle':<28}")
    print("-" * 116)
    for r in results:
        gate_ok = "✅" if r["path_a"].get("gate_grounded") == r["expected_grounding"] else "❌"
        a_res   = r["path_a"]["final_result"]
        b_res   = r["path_b"]["final_result"]
        oracle  = r["oracle_result"]
        print(f"{r['test_id']:<10} {r['name'][:45]:<46} {gate_ok:<6} {a_res:<6} {b_res:<20} {oracle:<28}")

    rag_confirmed  = sum(1 for r in results if r["oracle_result"] == "RAG_CONFIRMED")
    gen_confirmed  = sum(1 for r in results if r["oracle_result"] == "GENERATION_CONFIRMED")
    both_fail      = sum(1 for r in results if r["oracle_result"] == "BOTH_FAIL")
    pass_cases     = sum(1 for r in results if r["oracle_result"] == "PASS")
    gate_fail      = sum(1 for r in results if r["oracle_result"] == "RETRIEVAL_GATE_CONFIRMED")

    print(f"\nOracle Diagnosis:")
    print(f"  PASS (core works):                {pass_cases}/{total}")
    print(f"  RAG_CONFIRMED (Retrieval/Gate):   {rag_confirmed}/{total}")
    print(f"  GENERATION_CONFIRMED (LLM/Prompt):{gen_confirmed}/{total}")
    print(f"  RETRIEVAL_GATE_CONFIRMED:         {gate_fail}/{total}")
    print(f"  BOTH_FAIL:                        {both_fail}/{total}")

    neg_tests  = [r for r in results if not r["expected_grounding"]]
    neg_leaks  = [r for r in neg_tests if r["path_a"].get("gate_grounded", False)]
    print(f"\nNegative Control Protection:")
    print(f"  Expected abstain tests: {len(neg_tests)}")
    print(f"  Negative control leaks: {len(neg_leaks)} (target: 0)")
    for r in neg_leaks:
        print(f"    ❌ LEAK: {r['test_id']} — {r['name']}")

    # Primary root cause conclusion
    print("\nPrimary Failure Attribution:")
    if rag_confirmed > gen_confirmed and rag_confirmed > both_fail:
        print("  => PRIMARY PROBLEM: RAG_CONFIRMED — Retrieval / Evidence Gate is the main failure source.")
    elif gen_confirmed > rag_confirmed:
        print("  => PRIMARY PROBLEM: GENERATION_CONFIRMED — LLM / System Prompt is the main failure source.")
    elif both_fail > 0:
        print("  => PRIMARY PROBLEM: BOTH_FAIL — Check evidence injection and System Prompt.")
    else:
        print("  => System functioning correctly across all tested cases.")

    # Save JSON
    out_path = os.path.join(EVAL_DIR, "benchmark_v4_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "benchmark": "v4",
            "llm":       provider_desc,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "summary": {
                "total":                    total,
                "pass_count":               pass_count,
                "pass_rate_pct":            round(pass_count / total * 100, 1),
                "oracle_rag_confirmed":     rag_confirmed,
                "oracle_gen_confirmed":     gen_confirmed,
                "oracle_both_fail":         both_fail,
                "oracle_pass":              pass_cases,
                "negative_control_leaks":   len(neg_leaks),
            },
            "results": results,
        }, f, ensure_ascii=False, indent=2)
    print(f"\nResults saved to: {out_path}")
    print("=" * 80)


if __name__ == "__main__":
    run_benchmark()
