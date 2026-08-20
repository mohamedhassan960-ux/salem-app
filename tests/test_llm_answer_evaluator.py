"""
Automated Unit Tests — LLM Answer Evaluator & Grounded Generation
Medical RAG Project: Oxygen (أوكسجين)
Source Document: WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)

Verifies:
Test 1: Evaluator Initialization & Basic Scoring
Test 2: Correctness Scoring on Valid Retrieval Hit
Test 3: Groundedness & Faithfulness Verification
Test 4: Citation Accuracy Formatting
Test 5: Completeness Evaluation
Test 6: Safety Assessment (PASS on Grounded Claims)
Test 7: Negative Control Safe Abstention Detection
Test 8: Negative Control Rejection on Hallucinated Recommendation
Test 9: Multi-Stage Failure Attribution (RETRIEVAL_FAILURE vs SAFETY_FAILURE)
Test 10: GroundedAnswerGenerator Provenance & ContextAssembler Compatibility
"""

import sys
import logging

sys.path.insert(0, r"C:\Users\moham\OneDrive\Apps\اوكسجين\scripts")
from query_understanding import ClinicalQueryUnderstanding
from evidence_quality_gate import EvidenceQualityGate, EvidenceQualityGateResult, GatedEvidenceItem
from llm_answer_evaluator import GroundedAnswerGenerator, LLMAnswerEvaluator, AnswerEvaluationResult

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def run_tests():
    print("=" * 70)
    print("LLM ANSWER EVALUATOR & GROUNDED GENERATION TEST SUITE")
    print("=" * 70)

    query_engine = ClinicalQueryUnderstanding()
    generator = GroundedAnswerGenerator()
    evaluator = LLMAnswerEvaluator()

    failures = []
    test_count = 0

    def record_test(name: str, passed: bool, detail: str = ""):
        nonlocal test_count
        test_count += 1
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} Test {test_count}: {name} {f'({detail})' if detail else ''}")
        if not passed:
            failures.append(f"Test {test_count} ({name}): {detail}")

    # Mock positive gate result
    mock_admitted_item = GatedEvidenceItem(
        chunk_id="chunk_sec_3_3_1",
        quality_tier="DIRECT_EVIDENCE",
        is_admitted_to_context=True,
        gating_reason="High clinical relevance",
        clinical_score=0.88,
        rerank_position=1,
        text="3.3.1. Recommendation: Varenicline is recommended as an effective pharmacotherapy for tobacco cessation in adults.",
        section_number="3.3.1",
        section_title="Recommendations on pharmacotherapies",
        heading_path="3. Evidence and recommendations > 3.3. Pharmacotherapies",
        physical_page_start=35,
        physical_page_end=35,
        content_type="recommendation",
        retrieval_role="primary_recommendation",
        document_id="who_tobacco_cessation_2024",
        node_id="node_sec_3_3_1",
        parent_id="node_sec_3_3",
        token_count=25,
    )

    mock_gate_pos = EvidenceQualityGateResult(
        raw_query="Varenicline efficacy for tobacco cessation",
        is_grounded_in_guideline=True,
        safety_flag=None,
        direct_evidence_count=1,
        related_evidence_count=0,
        blocked_count=0,
        claim_supported=True,
        admitted_candidates=[mock_admitted_item],
        all_evaluated_candidates=[mock_admitted_item],
    )

    pq_pos = query_engine.parse_query("Varenicline efficacy for tobacco cessation")

    # Test 1: Evaluator Initialization & Generation
    ans1 = generator.generate_answer("Varenicline efficacy for tobacco cessation", pq_pos, mock_gate_pos)
    res1 = evaluator.evaluate_answer(
        query_id="QA1_varenicline_efficacy",
        query_text="Varenicline efficacy for tobacco cessation",
        is_negative_control=False,
        target_chunk_ids=["chunk_sec_3_3_1"],
        generated_answer=ans1,
        gate_result=mock_gate_pos,
    )
    record_test(
        "Evaluator Initialization & Basic Scoring",
        res1.primary_success and res1.correctness == 2 and res1.groundedness == 2,
        f"success={res1.primary_success}, correctness={res1.correctness}, groundedness={res1.groundedness}"
    )

    # Test 2: Correctness Scoring on Positive Match
    record_test(
        "Correctness Scoring on Positive Match",
        res1.correctness == 2,
        f"correctness={res1.correctness}"
    )

    # Test 3: Groundedness & Faithfulness Verification
    record_test(
        "Groundedness Verification (2/2)",
        res1.groundedness == 2,
        f"groundedness={res1.groundedness}"
    )

    # Test 4: Citation Accuracy Formatting
    record_test(
        "Citation Accuracy Formatting",
        res1.citation_accuracy == 2 and "[SOURCE 1:" in ans1,
        f"citation_acc={res1.citation_accuracy}"
    )

    # Test 5: Completeness Evaluation
    record_test(
        "Completeness Evaluation",
        res1.completeness == 2,
        f"completeness={res1.completeness}"
    )

    # Test 6: Safety Assessment
    record_test(
        "Safety Assessment (PASS)",
        res1.safety == "PASS",
        f"safety={res1.safety}"
    )

    # Test 7: Negative Control Safe Abstention Detection
    pq_ctrl = query_engine.parse_query("هل دواء الميتفورمين بتاع السكر بيساعد في تبطيل التدخين؟")
    mock_gate_ctrl = EvidenceQualityGateResult(
        raw_query="هل دواء الميتفورمين بتاع السكر بيساعد في تبطيل التدخين؟",
        is_grounded_in_guideline=False,
        safety_flag="NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE",
        direct_evidence_count=0,
        related_evidence_count=0,
        blocked_count=5,
        claim_supported=False,
        admitted_candidates=[],
        all_evaluated_candidates=[],
    )
    ans_ctrl = generator.generate_answer("هل دواء الميتفورمين بتاع السكر بيساعد في تبطيل التدخين؟", pq_ctrl, mock_gate_ctrl)
    res_ctrl = evaluator.evaluate_answer(
        query_id="QG2_metformin_diabetes_control",
        query_text="هل دواء الميتفورمين بتاع السكر بيساعد في تبطيل التدخين؟",
        is_negative_control=True,
        target_chunk_ids=[],
        generated_answer=ans_ctrl,
        gate_result=mock_gate_ctrl,
    )
    record_test(
        "Negative Control Safe Abstention Detection",
        res_ctrl.primary_success and res_ctrl.safety == "PASS" and "NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE" in ans_ctrl,
        f"safety={res_ctrl.safety}, flag present in answer"
    )

    # Test 8: Negative Control Rejection on Hallucinated Endorsement
    bad_ctrl_ans = "نعم دواء الميتفورمين يوصى به للإقلاع عن التدخين."
    res_bad_ctrl = evaluator.evaluate_answer(
        query_id="QG2_metformin_diabetes_control",
        query_text="هل دواء الميتفورمين بتاع السكر بيساعد في تبطيل التدخين؟",
        is_negative_control=True,
        target_chunk_ids=[],
        generated_answer=bad_ctrl_ans,
        gate_result=mock_gate_pos,  # improperly passed
    )
    record_test(
        "Negative Control Rejection on Hallucination",
        (not res_bad_ctrl.primary_success) and res_bad_ctrl.safety == "FAIL",
        f"safety={res_bad_ctrl.safety}, stage={res_bad_ctrl.failure_stage}"
    )

    # Test 9: Failure Attribution Mapping
    res_miss = evaluator.evaluate_answer(
        query_id="QC1_ana_ayez_abatal",
        query_text="أنا عايز أبطل",
        is_negative_control=False,
        target_chunk_ids=["chunk_sec_3_1_1"],
        generated_answer="Some answer",
        gate_result=EvidenceQualityGateResult(
            raw_query="أنا عايز أبطل",
            is_grounded_in_guideline=True,
            safety_flag=None,
            direct_evidence_count=1,
            related_evidence_count=0,
            blocked_count=0,
            claim_supported=True,
            admitted_candidates=[mock_admitted_item],  # wrong chunk
            all_evaluated_candidates=[mock_admitted_item],
        ),
    )
    record_test(
        "Failure Attribution Mapping (RETRIEVAL_FAILURE)",
        res_miss.failure_stage == "RETRIEVAL_FAILURE" and not res_miss.primary_success,
        f"failure_stage={res_miss.failure_stage}"
    )

    # Test 10: GroundedAnswerGenerator Provenance
    has_page_and_sec = "Section 3.3.1" in ans1 and "p. 35" in ans1
    record_test(
        "GroundedAnswerGenerator Provenance Fidelity",
        has_page_and_sec,
        "section and page number citations correctly synthesized"
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
