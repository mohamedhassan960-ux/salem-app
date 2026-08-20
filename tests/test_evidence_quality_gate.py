"""
Automated Unit Tests — Evidence Quality Gate & Safety Protection
Medical RAG Project: Oxygen (أوكسجين)
Source Document: WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)

Verifies:
Test 1: Quality Gate Initialization & Candidate Evaluation
Test 2: Direct Evidence Priority (Direct admitted before Related)
Test 3: Insufficient Boilerplate Blocking (Acknowledgements/Preface blocked)
Test 4: Potentially Misleading Evidence Blocking (Unproven therapies blocked for standard queries)
Test 5: Negative Control Detection (Metformin out-of-scope)
Test 6: Negative Control Detection (E-Cigarette out-of-scope)
Test 7: Negative Control Detection (Weight loss out-of-scope)
Test 8: Safety Flag Generation (NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE)
Test 9: Budget Enforcement (Top-5 admitted candidates limit)
Test 10: Seamless ContextAssembler Integration
"""

import sys
import logging

sys.path.insert(0, r"C:\Users\moham\OneDrive\Apps\اوكسجين\scripts")
from hybrid_retriever import HybridRetriever
from query_understanding import ClinicalQueryUnderstanding
from reranker import ClinicalReranker
from evidence_quality_gate import EvidenceQualityGate, EvidenceQualityGateResult
from context_assembler import ContextAssembler

RECORDS_PATH = r"C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\retrieval_records_v2.json"
DENSE_NPZ = r"C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\dense_index_v2.npz"
DENSE_META = r"C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\dense_metadata_v2.json"
LOCAL_MODEL = r"C:\Users\moham\OneDrive\Apps\اوكسجين\data\models\multilingual-e5-small"


def run_tests():
    print("=" * 70)
    print("EVIDENCE QUALITY GATE & SAFETY PROTECTION AUTOMATED TEST SUITE")
    print("=" * 70)

    query_engine = ClinicalQueryUnderstanding()
    hybrid = HybridRetriever.from_files(
        records_path=RECORDS_PATH,
        dense_npz_path=DENSE_NPZ,
        dense_meta_path=DENSE_META,
        model_name=LOCAL_MODEL,
        k_rrf=60,
        candidate_pool_size=30,
    )
    reranker = ClinicalReranker()
    gate = EvidenceQualityGate()

    failures = []
    test_count = 0

    def record_test(name: str, passed: bool, detail: str = ""):
        nonlocal test_count
        test_count += 1
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} Test {test_count}: {name} {f'({detail})' if detail else ''}")
        if not passed:
            failures.append(f"Test {test_count} ({name}): {detail}")

    # Test 1: Quality Gate Evaluation on Positive Clinical Query
    q1 = "Varenicline efficacy and adverse events for tobacco cessation"
    pq1 = query_engine.parse_query(q1)
    cands1 = hybrid.retrieve(pq1.expanded_search_query, top_k=20)
    reranked1 = reranker.rerank(cands1, pq1, top_k=20)
    res1 = gate.evaluate_candidates(reranked1, pq1, final_budget_k=5)
    record_test(
        "Quality Gate Evaluation on Clinical Query",
        res1.is_grounded_in_guideline and len(res1.admitted_candidates) > 0,
        f"admitted={len(res1.admitted_candidates)}, direct={res1.direct_evidence_count}"
    )

    # Test 2: Direct Evidence Priority
    admitted_tiers = [item.quality_tier for item in res1.admitted_candidates]
    direct_before_related = True
    seen_related = False
    for t in admitted_tiers:
        if t == "RELATED_EVIDENCE":
            seen_related = True
        elif t == "DIRECT_EVIDENCE" and seen_related:
            direct_before_related = False
            break
    record_test(
        "Direct Evidence Priority in Final Context",
        direct_before_related,
        f"admitted tiers: {admitted_tiers}"
    )

    # Test 3: Insufficient Boilerplate Blocking
    has_insufficient_admitted = any(item.quality_tier == "INSUFFICIENT" for item in res1.admitted_candidates)
    record_test(
        "Insufficient Boilerplate Blocking (Acknowledgements/Preface blocked)",
        not has_insufficient_admitted,
        "zero insufficient boilerplate chunks in final context"
    )

    # Test 4: Potentially Misleading Evidence Blocking
    has_misleading_admitted = any(item.quality_tier == "POTENTIALLY_MISLEADING" for item in res1.admitted_candidates)
    record_test(
        "Potentially Misleading Evidence Blocking",
        not has_misleading_admitted,
        "zero misleading chunks in final context"
    )

    # Test 5: Negative Control (Metformin)
    q_met = "هل دواء الميتفورمين بتاع السكر بيساعد في تبطيل التدخين؟"
    pq_met = query_engine.parse_query(q_met)
    cands_met = hybrid.retrieve(pq_met.expanded_search_query, top_k=20)
    reranked_met = reranker.rerank(cands_met, pq_met, top_k=20)
    res_met = gate.evaluate_candidates(reranked_met, pq_met, final_budget_k=5)
    record_test(
        "Negative Control Detection (Metformin blocked)",
        not res_met.is_grounded_in_guideline and res_met.safety_flag == "NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE",
        f"safety_flag={res_met.safety_flag}"
    )

    # Test 6: Negative Control (E-Cigarettes Endorsement)
    q_ecig = "هل السجائر الإلكترونية والفيب موصى بيها كعلاج رسمي للإقلاع عن التدخين؟"
    pq_ecig = query_engine.parse_query(q_ecig)
    cands_ecig = hybrid.retrieve(pq_ecig.expanded_search_query, top_k=20)
    reranked_ecig = reranker.rerank(cands_ecig, pq_ecig, top_k=20)
    res_ecig = gate.evaluate_candidates(reranked_ecig, pq_ecig, final_budget_k=5)
    record_test(
        "Negative Control Detection (E-Cigarettes blocked)",
        not res_ecig.is_grounded_in_guideline and res_ecig.safety_flag == "NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE",
        f"safety_flag={res_ecig.safety_flag}"
    )

    # Test 7: Negative Control (Weight Loss)
    q_wl = "هل الإبر الصينية بتساعد على إنقاص الوزن وحرق الدهون؟"
    pq_wl = query_engine.parse_query(q_wl)
    cands_wl = hybrid.retrieve(pq_wl.expanded_search_query, top_k=20)
    reranked_wl = reranker.rerank(cands_wl, pq_wl, top_k=20)
    res_wl = gate.evaluate_candidates(reranked_wl, pq_wl, final_budget_k=5)
    record_test(
        "Negative Control Detection (Weight loss blocked)",
        not res_wl.is_grounded_in_guideline and res_wl.safety_flag == "NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE",
        f"safety_flag={res_wl.safety_flag}"
    )

    # Test 8: Safety Flag Generation
    record_test(
        "Safety Flag Integrity for Out-of-Scope Queries",
        res_met.safety_flag == "NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE" and res_1_flag_ok(res1),
        "safety flag appropriately asserted or omitted"
    )

    # Test 9: Budget Enforcement (Top-5 admitted limit)
    record_test(
        "Top-5 Admitted Evidence Budget Enforcement",
        len(res1.admitted_candidates) <= 5,
        f"admitted count = {len(res1.admitted_candidates)}"
    )

    # Test 10: Seamless ContextAssembler Integration
    assembler = ContextAssembler(max_context_tokens=3000)
    ca_sources = res1.to_context_assembler_sources()
    assembled = assembler.assemble(q1, ca_sources)
    record_test(
        "Seamless ContextAssembler Integration",
        assembled.context_token_count > 0 and len(assembled.sources) == len(res1.admitted_candidates),
        f"assembled {len(assembled.sources)} sources, tokens={assembled.context_token_count}"
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


def res_1_flag_ok(res1: EvidenceQualityGateResult) -> bool:
    return res1.safety_flag is None and res1.is_grounded_in_guideline


if __name__ == "__main__":
    success = run_tests()
    if not success:
        sys.exit(1)
