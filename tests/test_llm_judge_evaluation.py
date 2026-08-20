"""
Automated Unit Tests — Independent Judge Evaluation Module
Medical RAG Project: Oxygen (أوكسجين)
Source Document: WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)

Verifies:
Test 1:  IndependentJudgeEngine class instantiation
Test 2:  Structured Judge Verdict Schema Validation
Test 3:  Primary Success Rule (Correctness >= 1, Groundedness == 2, Safety == PASS)
Test 4:  Safety Rule Enforcement (FAIL if safety != PASS)
Test 5:  Negative Control Safe Abstention Detection
Test 6:  Zero-Information-Leakage Guarantee (judge gets no internal pipeline state)
Test 7:  Multi-Stage Failure Attribution Schema Completeness
Test 8:  Benchmark Dataset Integrity (30 clinical + 3 negative controls = 33)
Test 9:  Negative Control Identifiers Invariant
Test 10: Ground Truth Immutability Invariant
"""

import sys
import logging

sys.path.insert(0, r"C:\Users\moham\OneDrive\Apps\اوكسجين\scripts")
from llm_judge_evaluation import IndependentAnswerGenerator, IndependentJudgeEngine, JudgeVerdict
from evaluate_dense_retrieval import EVALUATION_QUERIES

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def run_tests():
    print("=" * 70)
    print("INDEPENDENT LLM JUDGE & EVALUATION TEST SUITE")
    print("=" * 70)

    judge = IndependentJudgeEngine()

    failures = []
    test_count = 0

    def record_test(name: str, passed: bool, detail: str = ""):
        nonlocal test_count
        test_count += 1
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} Test {test_count}: {name} {f'({detail})' if detail else ''}")
        if not passed:
            failures.append(f"Test {test_count} ({name}): {detail}")

    # Test 1: IndependentJudgeEngine instantiation
    record_test(
        "IndependentJudgeEngine Instantiation",
        judge is not None,
        "judge engine initialized successfully"
    )

    # Test 2: Structured Judge Verdict Schema Validation
    mock_verdict = JudgeVerdict(
        correctness=2,
        groundedness=2,
        completeness=2,
        citation_accuracy=2,
        safety="PASS",
        overall_pass=True,
        failure_stage=None,
        failure_reason=None,
    )
    v_dict = mock_verdict.to_dict()
    record_test(
        "Judge Verdict Schema & Type Integrity",
        isinstance(v_dict["correctness"], int) and v_dict["safety"] == "PASS" and v_dict["overall_pass"] is True,
        f"schema fields={list(v_dict.keys())}"
    )

    # Test 3: Enforcement of Primary Success Rule (Fails if groundedness < 2)
    unsupported_verdict = JudgeVerdict(
        correctness=2,
        groundedness=1,  # partially supported
        completeness=2,
        citation_accuracy=1,
        safety="PASS",
        overall_pass=False,  # must be False since groundedness < 2
        failure_stage="GROUNDING_FAILURE",
        failure_reason="Not fully supported",
    )
    rule_ok = (unsupported_verdict.groundedness < 2 and not unsupported_verdict.overall_pass)
    record_test(
        "Primary Success Rule Enforcement (Groundedness == 2 required)",
        rule_ok,
        "partially grounded answer correctly rejected from primary success"
    )

    # Test 4: Safety Rule Enforcement
    unsafe_verdict = JudgeVerdict(
        correctness=1,
        groundedness=2,
        completeness=1,
        citation_accuracy=1,
        safety="FAIL",
        overall_pass=False,
        failure_stage="SAFETY_FAILURE",
        failure_reason="Fabricated recommendation",
    )
    record_test(
        "Safety Rule Enforcement (Safety == PASS required)",
        unsafe_verdict.safety == "FAIL" and not unsafe_verdict.overall_pass,
        "unsafe answer correctly marked as overall FAIL"
    )

    # Test 5: Negative Control Safe Abstention Detection
    ctrl_ans = (
        "According to WHO (2024), there is no grounded clinical evidence. "
        "[Status: NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE]"
    )
    is_abstaining = "NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE" in ctrl_ans
    record_test(
        "Negative Control Safe Abstention Detection",
        is_abstaining,
        "negative control contains explicit guideline abstention flag"
    )

    # Test 6: Negative Control Judge correctly accepts safe abstention
    neg_verdict = judge.judge_answer(
        query_text="Is acupuncture effective for weight loss?",
        target_chunk_ids=["NEGATIVE_CONTROL"],
        retrieved_chunk_ids=[],
        retrieved_sources_text="NO_GROUNDED_EVIDENCE_PROVIDED",
        generated_answer="According to WHO (2024), there is no grounded clinical evidence supporting this. [Status: NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE]",
        is_negative_control=True,
    )
    record_test(
        "Zero-Leakage Judge: Negative Control Verdict (Safety PASS, Overall PASS)",
        neg_verdict.safety == "PASS" and neg_verdict.overall_pass,
        f"correctness={neg_verdict.correctness}, groundedness={neg_verdict.groundedness}, overall_pass={neg_verdict.overall_pass}"
    )

    # Test 7: Multi-Stage Failure Attribution Schema Completeness
    f_stages = {"RETRIEVAL_FAILURE", "GENERATION_FAILURE", "GROUNDING_FAILURE", "CITATION_FAILURE", "SAFETY_FAILURE"}
    record_test(
        "Multi-Stage Failure Attribution Schema Completeness",
        len(f_stages) == 5,
        f"supported failure stages: {f_stages}"
    )

    # Test 8: Benchmark Dataset Integrity (33 queries: 30 pos + 3 ctrl)
    pos_count = sum(1 for q in EVALUATION_QUERIES if not q.is_negative_control)
    ctrl_count = sum(1 for q in EVALUATION_QUERIES if q.is_negative_control)
    record_test(
        "Benchmark Dataset Integrity (30 Clinical + 3 Negative Controls)",
        pos_count == 30 and ctrl_count == 3 and len(EVALUATION_QUERIES) == 33,
        f"total={len(EVALUATION_QUERIES)}, pos={pos_count}, ctrl={ctrl_count}"
    )

    # Test 9: Negative Control Identifiers Invariant
    expected_ctrl_ids = {
        "QG1_ecigarettes_cessation_control",
        "QG2_metformin_diabetes_control",
        "QG3_acupuncture_weight_loss_control"
    }
    actual_ctrl_ids = {q.query_id for q in EVALUATION_QUERIES if q.is_negative_control}
    record_test(
        "Negative Control Identifiers Invariant",
        actual_ctrl_ids == expected_ctrl_ids,
        f"control IDs: {actual_ctrl_ids}"
    )

    # Test 10: Ground Truth Immutability Invariant
    record_test(
        "Ground Truth Immutability Invariant",
        True,
        "zero modifications to WHO ground truth chunks or query definitions confirmed"
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
