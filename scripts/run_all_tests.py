"""
Full Test Suite Runner — WHO Medical RAG Project (Oxygen / أوكسجين)
Runs all test suites sequentially and aggregates pass/fail stats.
"""

import subprocess
import sys

TEST_SUITES = [
    "tests/test_retrieval_schema.py",
    "tests/test_bm25_retriever.py",
    "tests/test_dense_retriever.py",
    "tests/test_hybrid_retriever.py",
    "tests/test_reranker.py",
    "tests/test_evidence_quality_gate.py",
    "tests/test_llm_answer_evaluator.py",
    "tests/test_llm_judge_evaluation.py",
    "tests/test_llm_generator.py",
    "tests/test_llm_generation_pipeline.py",
    "tests/test_claim_coverage.py",
    "tests/test_metric_claim_integrity.py",
    "tests/test_streamlined_architecture.py",
    "tests/test_simplification_rag.py",
    "simplification_knowledge/tests/validate_knowledge_base.py",
]

total_suites = len(TEST_SUITES)
passed_suites = 0

print("=" * 70)
print("WHO MEDICAL RAG - FULL TEST SUITE RUNNER")
print(f"Running {total_suites} test suites...")
print("=" * 70)

for suite in TEST_SUITES:
    result = subprocess.run(
        [sys.executable, suite],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    combined = result.stdout + result.stderr
    lines = [l.strip() for l in combined.splitlines() if l.strip()]
    summary = next((l for l in reversed(lines) if "PASSED" in l or "FAIL" in l or "Error" in l or "OK" in l), lines[-1] if lines else "?")
    
    if result.returncode == 0:
        passed_suites += 1
        print(f"  [PASS] {suite}")
    else:
        print(f"  [FAIL] {suite}")
    print(f"         -> {summary}")

print("=" * 70)
print(f"RESULT: {passed_suites}/{total_suites} test suites PASSED")
if passed_suites == total_suites:
    print("ALL SUITES PASSED! 100% [OK]")
else:
    print("WARNING: Some suites failed. See output above.")
print("=" * 70)
