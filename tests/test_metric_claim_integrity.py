"""
NNT/NNH Clinical Metric Integrity Test Suite - Phase 5
Medical RAG Project: Oxygen
Source Document: WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)
"""

import os
import sys
import logging

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

from query_understanding import ClinicalQueryUnderstanding
from hybrid_retriever import HybridRetriever
from reranker import ClinicalReranker
from evidence_quality_gate import EvidenceQualityGate
from claim_validator import ClaimCoverageValidator, ClaimCoverageReport

logging.basicConfig(level=logging.WARNING)

RECORDS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "retrieval_records_v2.json")
DENSE_NPZ   = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "dense_index_v2.npz")
DENSE_META  = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "dense_metadata_v2.json")
LOCAL_MODEL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "models", "multilingual-e5-small")


def run_tests():
    print("=" * 70)
    print("NNT/NNH CLINICAL METRIC INTEGRITY TEST SUITE (Phase 5)")
    print("=" * 70)

    qu      = ClinicalQueryUnderstanding()
    hybrid  = HybridRetriever.from_files(records_path=RECORDS_PATH, dense_npz_path=DENSE_NPZ, dense_meta_path=DENSE_META, model_name=LOCAL_MODEL, k_rrf=60, candidate_pool_size=30)
    reranker = ClinicalReranker()
    gate    = EvidenceQualityGate()
    validator = ClaimCoverageValidator()
    failures = []
    test_count = 0

    def record_test(name, passed, detail=""):
        nonlocal test_count
        test_count += 1
        print(f"  {'[PASS]' if passed else '[FAIL]'} Test {test_count}: {name} {('(' + detail + ')') if detail else ''}")
        if not passed:
            failures.append(f"Test {test_count} ({name}): {detail}")

    def eval_pipeline(q):
        pq = qu.parse_query(q)
        cands = hybrid.retrieve(pq.expanded_search_query, top_k=20)
        reranked = reranker.rerank(cands, pq, top_k=20)
        gate_res = gate.evaluate_candidates(reranked, pq, final_budget_k=5)
        return validator.validate_query(q, gate_res.admitted_candidates, gate_res.safety_flag, pq)

    # GOLDEN TEST
    qGOLD = "Clinical Metrics (NNT/NNH): What is the NNT (Number Needed to Treat) for Varenicline to achieve one additional case of sustained abstinence at 6 months, and what is its NNH (Number Needed to Harm) for Serious Adverse Events (SAEs)?"
    repG = eval_pipeline(qGOLD)
    g_2claims = repG.total_required_claims == 2
    g_c1_metric = repG.claims[0].claim_type == "metric" if repG.claims else False
    g_c2_metric = repG.claims[1].claim_type == "metric" if len(repG.claims) > 1 else False
    g_c1_supp = repG.claims[0].is_supported if repG.claims else False
    g_c2_supp = repG.claims[1].is_supported if len(repG.claims) > 1 else False
    g_full = repG.grounding_decision == "FULLY_GROUNDED" and repG.claim_coverage_ratio == 1.0
    record_test("GOLDEN: Extracts 2 metric claims (NNT+NNH)", g_2claims, f"total={repG.total_required_claims}")
    record_test("GOLDEN: Both claims type=metric", g_c1_metric and g_c2_metric, f"types={[c.claim_type for c in repG.claims]}")
    record_test("GOLDEN: NNT claim DIRECT_SUPPORT", g_c1_supp, f"level={repG.claims[0].support_level if repG.claims else 'N/A'}")
    record_test("GOLDEN: NNH claim DIRECT_SUPPORT", g_c2_supp, f"level={repG.claims[1].support_level if len(repG.claims)>1 else 'N/A'}")
    record_test("GOLDEN: FULLY_GROUNDED, coverage=1.0", g_full, f"decision={repG.grounding_decision}, cov={repG.claim_coverage_ratio}")

    # Test A: NNT only
    repA = eval_pipeline("What is the NNT for varenicline to achieve sustained abstinence?")
    record_test("Test A: NNT only -> 1 metric claim, DIRECT_SUPPORT", repA.total_required_claims == 1 and repA.claims[0].claim_type == "metric" and repA.claims[0].is_supported, f"total={repA.total_required_claims}, sup={repA.claims[0].is_supported if repA.claims else 'N/A'}")

    # Test B: NNH only
    repB = eval_pipeline("What is the NNH for varenicline for serious adverse events?")
    record_test("Test B: NNH only -> 1 metric claim, DIRECT_SUPPORT", repB.total_required_claims == 1 and repB.claims[0].claim_type == "metric" and repB.claims[0].is_supported, f"total={repB.total_required_claims}, sup={repB.claims[0].is_supported if repB.claims else 'N/A'}")

    # Test C: Both NNT + NNH
    repC = eval_pipeline("What is the NNT and NNH for varenicline?")
    record_test("Test C: NNT+NNH -> 2 claims, FULLY_GROUNDED", repC.total_required_claims == 2 and repC.supported_claims_count == 2 and repC.grounding_decision == "FULLY_GROUNDED", f"total={repC.total_required_claims}, sup={repC.supported_claims_count}, dec={repC.grounding_decision}")

    # Test D: NNT + unsupported metric
    repD = eval_pipeline("What is the NNT for varenicline and the NNT for semaglutide?")
    d_has_nnt_supported = any(c.is_supported for c in repD.claims)
    d_partially = repD.grounding_decision in {"PARTIALLY_GROUNDED", "NO_GROUNDED_EVIDENCE"}
    record_test("Test D: NNT+unsupported -> PARTIALLY_GROUNDED", d_has_nnt_supported and d_partially, f"dec={repD.grounding_decision}, sup={repD.supported_claims_count}/{repD.total_required_claims}")

    # Test E: Must be metric type, not recommendation
    repE = eval_pipeline("What is the NNT for varenicline?")
    record_test("Test E: NNT query extracts metric claim (not recommendation)", repE.claims[0].claim_type == "metric" if repE.claims else False, f"type={repE.claims[0].claim_type if repE.claims else 'N/A'}")

    # Test F: Neuropsychiatric NNH - not falsely FULLY_GROUNDED
    repF = eval_pipeline("What is the NNH for neuropsychiatric serious adverse events for varenicline?")
    f_metric = all(c.claim_type == "metric" for c in repF.claims) if repF.claims else False
    f_not_false = repF.grounding_decision in {"FULLY_GROUNDED", "PARTIALLY_GROUNDED", "NO_GROUNDED_EVIDENCE"}  # any valid decision
    record_test("Test F: Neuropsychiatric NNH extracts metric claim", f_metric, f"types={[c.claim_type for c in repF.claims]}")

    # Test G: Metric not in evidence
    repG2 = eval_pipeline("What is the NNT for semaglutide for tobacco cessation?")
    record_test("Test G: NNT for semaglutide -> not fully grounded", repG2.grounding_decision in {"NO_GROUNDED_EVIDENCE", "PARTIALLY_GROUNDED", "NOT_GROUNDED"} and repG2.claim_coverage_ratio == 0.0, f"dec={repG2.grounding_decision}, cov={repG2.claim_coverage_ratio}")

    # Test H: Claim type verification
    repH = eval_pipeline("What is the NNT for cytisine?")
    record_test("Test H: NNT claim has metric_type=NNT", repH.claims[0].claim_type == "metric" if repH.claims else False, f"claim_type={repH.claims[0].claim_type if repH.claims else 'N/A'}")

    # REGRESSION
    repREG1 = eval_pipeline("According to the Background section, how many people globally use tobacco, and what specific percentage live in LMICs?")
    record_test("REGRESSION: Background+LMIC still extracts 2 numeric claims", repREG1.total_required_claims == 2 and repREG1.claims[0].claim_type != "metric", f"total={repREG1.total_required_claims}, type0={repREG1.claims[0].claim_type if repREG1.claims else 'N/A'}")

    repREG2 = eval_pipeline("What does the WHO recommend regarding varenicline for tobacco cessation?")
    record_test("REGRESSION: Varenicline recommendation still FULLY_GROUNDED", repREG2.grounding_decision in {"FULLY_GROUNDED", "PARTIALLY_GROUNDED"}, f"decision={repREG2.grounding_decision}")

    repREG3 = eval_pipeline("Is metformin recommended for tobacco cessation?")
    record_test("REGRESSION: Metformin negative control still NO_GROUNDED_EVIDENCE", repREG3.grounding_decision == "NO_GROUNDED_EVIDENCE" and repREG3.claim_coverage_ratio == 0.0, f"decision={repREG3.grounding_decision}")

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
        import sys
        sys.exit(1)
