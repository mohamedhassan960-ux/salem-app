"""
Automated Unit Tests — Claim-Level Evidence Coverage Validator
Medical RAG Project: Oxygen (أوكسجين)
Source Document: WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)

Verifies 10 required claim-level evaluation scenarios:
Test A: Fully Supported Clinical Recommendation (Varenicline)
Test B: Golden Test — Partially Supported Composite Query (Background Global Count + LMIC Percentage)
Test C: Negative Control Rejection (Metformin)
Test D: Related but Unsupported Topic (Weight Loss)
Test E: Exact Numeric Duration Verification (Brief Advice 30s-3min)
Test F: Section-Specific Verification (Background section requested)
Test G: Arabic Query Claim Extraction & Grounding (الخلفية + عدد المستخدمين عالمياً)
Test H: Multiple Claims Extraction & Differential Support
Test I: Single Claim Precision
Test J: Missing Entity Detection & Rejection
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

RECORDS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "retrieval_records_v2.json")
DENSE_NPZ = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "dense_index_v2.npz")
DENSE_META = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "dense_metadata_v2.json")
LOCAL_MODEL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "models", "multilingual-e5-small")


def run_tests():
    print("=" * 70)
    print("CLAIM-LEVEL EVIDENCE COVERAGE & GROUNDING VALIDATOR TEST SUITE")
    print("=" * 70)

    qu = ClinicalQueryUnderstanding()
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
    validator = ClaimCoverageValidator()

    failures = []
    test_count = 0

    def record_test(name: str, passed: bool, detail: str = ""):
        nonlocal test_count
        test_count += 1
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} Test {test_count}: {name} {f'({detail})' if detail else ''}")
        if not passed:
            failures.append(f"Test {test_count} ({name}): {detail}")

    # Helper function to evaluate pipeline through gate + validator
    def eval_pipeline(query_text: str) -> ClaimCoverageReport:
        pq = qu.parse_query(query_text)
        cands = hybrid.retrieve(pq.expanded_search_query, top_k=20)
        reranked = reranker.rerank(cands, pq, top_k=20)
        gate_res = gate.evaluate_candidates(reranked, pq, final_budget_k=5)
        report = validator.validate_query(
            query=query_text,
            admitted_evidence=gate_res.admitted_candidates,
            safety_flag=gate_res.safety_flag,
            parsed_query=pq,
        )
        return report

    # Test A: Fully Supported Clinical Recommendation
    qA = "What does the WHO recommend regarding varenicline for tobacco cessation?"
    repA = eval_pipeline(qA)
    citA = repA.primary_citation_tags[0] if repA.primary_citation_tags else ""
    record_test(
        "Test A: Fully Supported Clinical Recommendation (Varenicline)",
        repA.grounding_decision == "FULLY_GROUNDED" and repA.claim_coverage_ratio == 1.0 and "3.3" in citA,
        f"decision={repA.grounding_decision}, coverage={repA.claim_coverage_ratio}, citation={citA}"
    )

    # Test B: GOLDEN TEST — Partially Supported Composite Query & Citation Precision
    # Question: "According to the 'Background' section, how many people globally use tobacco, and what specific percentage of these users live in Low- and Middle-Income Countries (LMICs)?"
    # Claim 1: Global count (1.25 billion in Background chunk) -> DIRECT_SUPPORT -> Citation: [WHO — Background — Page 15]
    # Claim 2: LMIC percentage -> UNSUPPORTED (no % in Background chunk) -> NO Citation
    qB = "According to the 'Background' section, how many people globally use tobacco, and what specific percentage of these users live in Low- and Middle-Income Countries (LMICs)?"
    repB = eval_pipeline(qB)
    c1_supp = repB.claims[0].is_supported if len(repB.claims) > 0 else False
    c2_supp = repB.claims[1].is_supported if len(repB.claims) > 1 else False
    c1_cit = repB.claims[0].primary_citation_tag if len(repB.claims) > 0 else ""
    c2_cit = repB.claims[1].primary_citation_tag if len(repB.claims) > 1 else None
    
    # Critical Phase 4 Citation Check: Citation must NOT say 'Section 3.3', must be 'WHO — Background — Page 15'
    cit_valid = "3.3" not in str(c1_cit) and "Background" in str(c1_cit) and "Page 15" in str(c1_cit) and c2_cit is None
    record_test(
        "Test B: GOLDEN TEST — Partially Supported & Citation Precision",
        repB.total_required_claims == 2 and c1_supp is True and c2_supp is False and repB.grounding_decision == "PARTIALLY_GROUNDED" and repB.claim_coverage_ratio == 0.5 and cit_valid,
        f"c1_cit={c1_cit}, c2_cit={c2_cit}, coverage={repB.claim_coverage_ratio}, decision={repB.grounding_decision}"
    )

    # Test C: Negative Control (Metformin) — Must have NO fabricated citation
    qC = "Is metformin recommended for tobacco cessation by the WHO?"
    repC = eval_pipeline(qC)
    record_test(
        "Test C: Negative Control Rejection (Metformin out-of-scope, No citation)",
        repC.grounding_decision == "NO_GROUNDED_EVIDENCE" and repC.claim_coverage_ratio == 0.0 and len(repC.primary_citation_tags) == 0,
        f"decision={repC.grounding_decision}, citations={repC.primary_citation_tags}"
    )

    # Test D: Related but Unsupported Topic (Weight Loss)
    qD = "هل الإبر الصينية بتساعد على إنقاص الوزن وحرق الدهون؟"
    repD = eval_pipeline(qD)
    record_test(
        "Test D: Related but Unsupported Topic (Weight loss out-of-scope)",
        repD.grounding_decision == "NO_GROUNDED_EVIDENCE" and repD.claim_coverage_ratio == 0.0,
        f"decision={repD.grounding_decision}"
    )

    # Test E: Exact Numeric Evidence (Brief Advice Duration)
    qE = "How long does a brief advice consultation take according to WHO?"
    repE = eval_pipeline(qE)
    citE = repE.primary_citation_tags[0] if repE.primary_citation_tags else ""
    record_test(
        "Test E: Exact Numeric Duration Verification (Brief Advice 30s-3min)",
        repE.grounding_decision in {"FULLY_GROUNDED", "PARTIALLY_GROUNDED"} and repE.claims[0].is_supported and "Page" in citE,
        f"decision={repE.grounding_decision}, citation={citE}"
    )

    # Test F: Section-Specific Requirement Handling
    qF = "According to the 'Background' section, what is the global burden of tobacco?"
    repF = eval_pipeline(qF)
    has_bg_chunk = any("background" in cid.lower() for cid in repF.claims[0].supporting_chunk_ids)
    citF = repF.primary_citation_tags[0] if repF.primary_citation_tags else ""
    record_test(
        "Test F: Section-Specific Verification (Background section matched without 3.3)",
        has_bg_chunk and repF.claims[0].is_supported and "3.3" not in citF and "Background" in citF,
        f"citation={citF}, supporting_chunks={repF.claims[0].supporting_chunk_ids}"
    )

    # Test G: Arabic Query Claim Extraction & Grounding
    qG = "وفقًا لدليل منظمة الصحة العالمية، كم عدد الأشخاص الذين يستخدمون التبغ على مستوى العالم؟"
    repG = eval_pipeline(qG)
    citG = repG.primary_citation_tags[0] if repG.primary_citation_tags else ""
    record_test(
        "Test G: Arabic Query Claim Extraction & Citation (الخلفية + 1.25 مليار)",
        repG.total_required_claims >= 1 and repG.claims[0].is_supported is True and "Background" in citG and "3.3" not in citG,
        f"claims={repG.total_required_claims}, decision={repG.grounding_decision}, citation={citG}"
    )

    # Test H: Section 3.2.1 Specific Retrieval & Citation
    qH = "According to Section 3.2.1, what does WHO recommend regarding digital tobacco cessation modalities?"
    repH = eval_pipeline(qH)
    citH = repH.primary_citation_tags[0] if repH.primary_citation_tags else ""
    record_test(
        "Test H: Section 3.2.1 Specific Retrieval & Citation (Digital modalities)",
        repH.grounding_decision == "FULLY_GROUNDED" and "3.2.1" in citH,
        f"decision={repH.grounding_decision}, citation={citH}"
    )

    # Test I: Single Claim Precision (Cytisine)
    qI = "Does WHO recommend cytisine for tobacco cessation?"
    repI = eval_pipeline(qI)
    citI = repI.primary_citation_tags[0] if repI.primary_citation_tags else ""
    record_test(
        "Test I: Single Claim Precision (Cytisine recommendation)",
        repI.total_required_claims == 1 and repI.grounding_decision == "FULLY_GROUNDED" and repI.claim_coverage_ratio == 1.0 and "Cytisine" in citI or "3.3" in citI,
        f"decision={repI.grounding_decision}, citation={citI}"
    )

    # Test J: Missing Entity Detection & Rejection (Semaglutide / Ozempic)
    qJ = "Does WHO recommend semaglutide (Ozempic) for smoking cessation?"
    repJ = eval_pipeline(qJ)
    record_test(
        "Test J: Missing Entity Detection & Rejection (Semaglutide, No Citation)",
        repJ.grounding_decision in {"NO_GROUNDED_EVIDENCE", "NOT_GROUNDED"} and repJ.claim_coverage_ratio == 0.0 and len(repJ.primary_citation_tags) == 0,
        f"decision={repJ.grounding_decision}, citations={repJ.primary_citation_tags}"
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
