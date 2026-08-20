import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from query_understanding import ClinicalQueryUnderstanding
from hybrid_retriever import HybridRetriever
from reranker import ClinicalReranker

q = "According to the 'Background' section, how many people globally use tobacco, and what specific percentage of these users live in Low- and Middle-Income Countries (LMICs)?"

qu = ClinicalQueryUnderstanding()
pq = qu.parse_query(q)

ret = HybridRetriever.from_files(
    records_path=os.path.join(os.path.dirname(__file__), "..", "outputs", "retrieval_records_v2.json"),
    dense_npz_path=os.path.join(os.path.dirname(__file__), "..", "outputs", "dense_index_v2.npz"),
    dense_meta_path=os.path.join(os.path.dirname(__file__), "..", "outputs", "dense_metadata_v2.json"),
    model_name=os.path.join(os.path.dirname(__file__), "..", "data", "models", "multilingual-e5-small"),
)

cands = ret.retrieve(pq.expanded_search_query, top_k=20)
rer = ClinicalReranker()

print(f"Total candidates retrieved: {len(cands)}")
for i, c in enumerate(cands[:10]):
    sc = rer.score_candidate(c, pq)
    print(f"\n--- Candidate #{i+1} [{c.chunk_id}] ---")
    print(f"  Title: {c.section_title} (Sec {c.section_number}, Page {c.physical_page_start})")
    print(f"  Hybrid Rank: {c.hybrid_rank} | RRF Score: {c.rrf_score:.4f} | Dense Score: {c.dense_score} | BM25 Score: {c.bm25_score}")
    print(f"  Content Type: {c.content_type} -> CType Weight: {sc.content_type_weight}")
    print(f"  Semantic Score: {sc.semantic_score}")
    print(f"  Intervention Match: {sc.intervention_match_score}")
    print(f"  Population Match: {sc.population_match_score}")
    print(f"  Base Score = ({sc.semantic_score}*0.45 + {sc.intervention_match_score}*0.30 + {sc.population_match_score}*0.25) = {sc.semantic_score*0.45 + sc.intervention_match_score*0.30 + sc.population_match_score*0.25:.4f}")
    print(f"  Final Clinical Score = Base Score * {sc.content_type_weight} = {sc.clinical_score:.4f}")
