import sys, os
sys.path.insert(0, 'scripts')
from query_understanding import ClinicalQueryUnderstanding
from hybrid_retriever import HybridRetriever
from reranker import ClinicalReranker
from evidence_quality_gate import EvidenceQualityGate
from claim_validator import ClaimCoverageValidator

qu = ClinicalQueryUnderstanding()
hybrid = HybridRetriever.from_files(
    records_path='outputs/retrieval_records_v2.json',
    dense_npz_path='outputs/dense_index_v2.npz',
    dense_meta_path='outputs/dense_metadata_v2.json',
    model_name='data/models/multilingual-e5-small',
    k_rrf=60, candidate_pool_size=30,
)
reranker = ClinicalReranker()
gate = EvidenceQualityGate()
val = ClaimCoverageValidator()

qF = "According to the 'Background' section, what is the global burden of tobacco?"
pq = qu.parse_query(qF)
cands = hybrid.retrieve(pq.expanded_search_query, top_k=20)
reranked = reranker.rerank(cands, pq, top_k=20)
gate_res = gate.evaluate_candidates(reranked, pq, final_budget_k=5)

claims = val.extract_claims(qF, pq)
print("Extracted claims:")
for c in claims:
    print(" ", c)

print("\nEvaluating against admitted:")
for cand in gate_res.admitted_candidates:
    print(f"Cand: {cand.chunk_id} | SecTitle: {cand.section_title} | Heading: {cand.heading_path}")
    res = val._evaluate_single_claim(claims[0], [cand])
    print(f"  Result: {res.support_level} | Reason: {res.support_reason}")

rep = val.validate_query(qF, gate_res.admitted_candidates, gate_res.safety_flag, pq)
print("\nFinal report:", rep.to_dict())
