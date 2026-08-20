"""Diagnostic: trace gate behavior for the two failing pipeline test queries."""
import sys, os, logging
logging.disable(logging.CRITICAL)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from query_understanding import ClinicalQueryUnderstanding
from hybrid_retriever import HybridRetriever
from reranker import ClinicalReranker
from evidence_quality_gate import EvidenceQualityGate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
qu = ClinicalQueryUnderstanding()
hybrid = HybridRetriever.from_files(
    records_path=os.path.join(ROOT, "outputs", "retrieval_records_v2.json"),
    dense_npz_path=os.path.join(ROOT, "outputs", "dense_index_v2.npz"),
    dense_meta_path=os.path.join(ROOT, "outputs", "dense_metadata_v2.json"),
    model_name=os.path.join(ROOT, "data", "models", "multilingual-e5-small"),
    k_rrf=60, candidate_pool_size=30,
)
reranker = ClinicalReranker()
gate = EvidenceQualityGate()

test_queries = [
    ("Test 3 (e-cigarettes)", "هل السجائر الإلكترونية معتمدة كعلاج رسمي للإقلاع من منظمة الصحة العالمية؟"),
    ("Test 10 (metformin)", "هل دواء الميتفورمين بيعالج التدخين في دليل منظمة الصحة؟"),
    # Also from test_evidence_quality_gate.py Test 5 and 6 - these PASS there, so diagnose what differs
    ("Gate Test 5 (metformin ar)", "هل دواء الميتفورمين بتاع السكر بيساعد في تبطيل التدخين؟"),
    ("Gate Test 6 (ecig ar)", "هل السجائر الإلكترونية والفيب موصى بيها كعلاج رسمي للإقلاع عن التدخين؟"),
]

for label, q in test_queries:
    pq = qu.parse_query(q)
    cands = hybrid.retrieve(pq.expanded_search_query, top_k=20)
    reranked = reranker.rerank(cands, pq, top_k=20)
    res = gate.evaluate_candidates(reranked, pq, final_budget_k=5)
    print(f"\n[{label}]")
    print(f"  Query: {q[:65]}")
    print(f"  is_out_of_scope: {pq.is_out_of_scope}")
    print(f"  out_of_scope_reasons: {pq.out_of_scope_reasons}")
    print(f"  gate.is_grounded_in_guideline: {res.is_grounded_in_guideline}")
    print(f"  gate.safety_flag: {res.safety_flag}")
    print(f"  admitted_count: {len(res.admitted_candidates)}")
    print(f"  direct_evidence_count: {res.direct_evidence_count}")
    print(f"  related_evidence_count: {res.related_evidence_count}")
    if res.admitted_candidates:
        print(f"  TOP admitted: [{res.admitted_candidates[0].chunk_id}] tier={res.admitted_candidates[0].quality_tier}")
