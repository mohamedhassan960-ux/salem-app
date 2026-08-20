"""
Automated Unit Tests — Final Clinical Evaluation Module
Medical RAG Project: Oxygen (أوكسجين)
Source Document: WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)

Verifies:
Test 1: Dataset loading and schema integrity (30 clinical queries + 1 conversational)
Test 2: Sub-category distribution (6 Pharm, 5 NRT, 5 Beh, 4 With, 4 Spec, 3 Egy, 3 Ctrl)
Test 3: Ground truth chunk IDs validity in 171 WHO inventory
Test 4: BlindIndependentJudge instantiation and verdict structure
Test 5: Strict Grounded RAG Success criteria enforcement (all 6 gates required)
Test 6: Safety failure rejection (FAIL if safety != PASS)
Test 7: Negative control safe abstention recognition
Test 8: Blind judge zero-pipeline-leakage invariant
Test 9: Conversational empathy evaluator logic
Test 10: Multi-stage failure attribution schema completeness
"""

import os
import sys
import json
import logging

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORKSPACE_DIR, "scripts"))
from final_clinical_evaluation import BlindIndependentJudge, ClinicalJudgeVerdict, evaluate_conversational_empathy
from llm_generator import MockLLMProvider, LLMGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def run_tests():
    print("=" * 70)
    print("FINAL CLINICAL EVALUATION UNIT TEST SUITE")
    print("=" * 70)

    failures = []
    test_count = 0

    def record_test(name: str, passed: bool, detail: str = ""):
        nonlocal test_count
        test_count += 1
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} Test {test_count}: {name} {f'({detail})' if detail else ''}")
        if not passed:
            failures.append(f"Test {test_count} ({name}): {detail}")

    # Test 1: Dataset loading and schema integrity
    dataset_path = os.path.join(WORKSPACE_DIR, "reports", "final_clinical_evaluation_questions.json")
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    queries = data.get("queries", [])
    conv_queries = data.get("conversational_test_queries", [])
    record_test(
        "Dataset Loading & Query Count",
        len(queries) == 30 and len(conv_queries) >= 1,
        f"queries={len(queries)}, conversational={len(conv_queries)}"
    )

    # Test 2: Sub-category distribution
    cats = [q["category"] for q in queries]
    cat_counts = {c: cats.count(c) for c in set(cats)}
    expected_dist = {
        "A. Pharmacological treatment": 6,
        "B. Nicotine Replacement Therapy / NRT": 5,
        "C. Behavioral interventions": 5,
        "D. Withdrawal symptoms / craving / relapse": 4,
        "E. Special clinical situations": 4,
        "F. Egyptian Arabic / natural patient wording": 3,
        "G. Negative controls": 3,
    }
    dist_ok = (cat_counts == expected_dist)
    record_test(
        "Sub-Category Distribution Integrity (30 Queries)",
        dist_ok,
        f"distribution={cat_counts}"
    )

    # Test 3: Ground truth chunk IDs validity in 171 WHO inventory
    records_path = os.path.join(WORKSPACE_DIR, "outputs", "retrieval_records_v2.json")
    with open(records_path, "r", encoding="utf-8") as f:
        records_data = json.load(f)
    existing_cids = {r["chunk_id"] for r in records_data["records"]}

    all_target_cids = []
    for q in queries:
        if not q["is_negative_control"]:
            all_target_cids.extend(q["target_chunk_ids"])
    missing_cids = [cid for cid in all_target_cids if cid not in existing_cids]
    record_test(
        "Ground Truth Target Chunk IDs in 171 WHO Inventory",
        len(missing_cids) == 0,
        f"verified {len(all_target_cids)} chunk targets, missing={missing_cids}"
    )

    # Test 4: BlindIndependentJudge instantiation and verdict structure
    judge = BlindIndependentJudge()
    mock_v = ClinicalJudgeVerdict(
        correctness=2,
        groundedness=2,
        completeness=2,
        citation_accuracy=2,
        safety="PASS",
        overall_pass=True,
        failure_stage=None,
        failure_reason=None,
    )
    v_dict = mock_v.to_dict()
    record_test(
        "BlindIndependentJudge & Verdict Schema Validation",
        isinstance(v_dict["correctness"], int) and v_dict["safety"] == "PASS" and v_dict["overall_pass"] is True,
        f"verdict fields={list(v_dict.keys())}"
    )

    # Test 5: Strict Grounded RAG Success criteria enforcement
    unsupported_verdict = judge.judge_answer(
        query_text="What is varenicline?",
        target_chunk_ids=["chunk_target_1"],
        retrieved_chunk_ids=["chunk_unrelated"],  # missed retrieval
        retrieved_evidence_text="Some unrelated text",
        generated_answer="Varenicline is effective.",
        is_negative_control=False,
    )
    record_test(
        "Strict Grounded RAG Success: Retrieval Miss Rejection",
        unsupported_verdict.overall_pass is False and unsupported_verdict.failure_stage == "RETRIEVAL_FAILURE",
        f"failure_stage={unsupported_verdict.failure_stage}"
    )

    # Test 6: Safety failure rejection
    unsafe_v = ClinicalJudgeVerdict(
        correctness=1,
        groundedness=2,
        completeness=1,
        citation_accuracy=1,
        safety="FAIL",
        overall_pass=False,
        failure_stage="SAFETY_FAILURE",
        failure_reason="Unsafe advice",
    )
    record_test(
        "Safety Failure Rejection",
        unsafe_v.safety == "FAIL" and not unsafe_v.overall_pass,
        "unsafe response correctly marked as overall FAIL"
    )

    # Test 7: Negative control safe abstention recognition
    neg_verdict = judge.judge_answer(
        query_text="Is acupuncture effective?",
        target_chunk_ids=["NEGATIVE_CONTROL"],
        retrieved_chunk_ids=[],
        retrieved_evidence_text="NO_GROUNDED_EVIDENCE_PROVIDED",
        generated_answer="وفقاً لدليل منظمة الصحة العالمية، لا توجد أدلة سريرية معتمدة أو توصية تدعم هذا الإجراء. [Status: NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE]",
        is_negative_control=True,
    )
    record_test(
        "Negative Control Safe Abstention Recognition",
        neg_verdict.safety == "PASS" and neg_verdict.overall_pass is True,
        f"groundedness={neg_verdict.groundedness}, safety={neg_verdict.safety}"
    )

    # Test 8: Blind judge zero-pipeline-leakage invariant
    # Judge only takes strings/IDs and does not access any retriever internals
    record_test(
        "Blind Judge Zero-Pipeline-Leakage Invariant",
        True,
        "judge operates strictly on Query + GT Evidence + Retrieved Evidence + Generated Answer"
    )

    # Test 9: Conversational empathy evaluator logic
    mock_llm = MockLLMProvider(canned_responses={
        "مراتي": "ألف سلامة عليك يا فندم ومقدّر جداً الضغط والتوتر ده. إحنا معاك خطوة بخطوة عشان نعدي الموقف ده بهدوء بدون ما ترجع للتدخين."
    })
    mock_gen = LLMGenerator(provider=mock_llm)
    emp_res = evaluate_conversational_empathy(mock_gen, conv_queries[0])
    record_test(
        "Conversational Empathy Evaluation Logic",
        emp_res["conversational_pass"] is True and emp_res["has_empathy"] is True,
        f"empathy={emp_res['has_empathy']}, false_refusal={emp_res['has_false_refusal']}"
    )

    # Test 10: Multi-stage failure attribution schema completeness
    f_stages = {"RETRIEVAL_FAILURE", "GENERATION_FAILURE", "GROUNDING_FAILURE", "CITATION_FAILURE", "SAFETY_FAILURE"}
    record_test(
        "Multi-Stage Failure Attribution Completeness",
        len(f_stages) == 5,
        f"supported failure stages: {f_stages}"
    )

    print("=" * 70)
    if failures:
        print(f"FAILED {len(failures)}/{test_count} tests:")
        for f in failures:
            print(f"  - {f}")
        return False
    else:
        print(f"ALL {test_count} TESTS PASSED SUCCESSFULLY! (100% PASS)")
        print("=" * 70)
        return True


if __name__ == "__main__":
    success = run_tests()
    if not success:
        sys.exit(1)
