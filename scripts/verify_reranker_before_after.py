import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from query_understanding import ClinicalQueryUnderstanding
from hybrid_retriever import HybridRetriever
from reranker import ClinicalReranker

# Load components
qu = ClinicalQueryUnderstanding()
ret = HybridRetriever.from_files(
    records_path=os.path.join(os.path.dirname(__file__), "..", "outputs", "retrieval_records_v2.json"),
    dense_npz_path=os.path.join(os.path.dirname(__file__), "..", "outputs", "dense_index_v2.npz"),
    dense_meta_path=os.path.join(os.path.dirname(__file__), "..", "outputs", "dense_metadata_v2.json"),
    model_name=os.path.join(os.path.dirname(__file__), "..", "data", "models", "multilingual-e5-small"),
)
reranker = ClinicalReranker()

# Diagnostic Query
diag_q = "According to the 'Background' section, how many people globally use tobacco, and what specific percentage of these users live in Low- and Middle-Income Countries (LMICs)?"
pq_diag = qu.parse_query(diag_q)
cands_diag = ret.retrieve(pq_diag.expanded_search_query, top_k=20)
reranked_diag = reranker.rerank(cands_diag, pq_diag, top_k=5)

print("=== DIAGNOSTIC QUERY AFTER REFACTORING ===")
print("Query:", diag_q)
print("\nTop 5 Candidates after Clinical Reranking:")
for i, c in enumerate(reranked_diag, 1):
    print(f"#{i} [{c.chunk_id}] Sec {c.section_number}: {c.section_title} (Page {c.physical_page_start}) - Clinical Score: {c.clinical_score:.4f} (Hybrid Initial Rank: {c.initial_hybrid_rank})")

# 5 Regression Tests
print("\n" + "="*70)
print("=== REGRESSION BENCHMARK SUITE ===")
print("="*70)

benchmarks = [
    ("Test 1: Statistical / Background", "According to the 'Background' section, how many people globally use tobacco, and what specific percentage of these users live in Low- and Middle-Income Countries (LMICs)?", "chunk_node_L2_background"),
    ("Test 2: Clinical Recommendation", "What is the recommended dosing schedule and duration for varenicline?", "chunk_sec_3_3_1"),
    ("Test 3: Implementation", "How can health systems and policies reduce tobacco user treatment costs in LMICs?", "chunk_sec_3_7_4_3"),
    ("Test 4: Definition / Context", "What is the definition and duration of brief advice for tobacco cessation?", "chunk_sec_3_1_1"),
    ("Test 5: Arabic Query", "ما هي الجرعة الموصى بها لدواء فارينيكلين وكيف يتم التدرج فيها؟", "chunk_sec_3_3_1"),
]

for title, q_text, exp_target in benchmarks:
    pq = qu.parse_query(q_text)
    cands = ret.retrieve(pq.expanded_search_query, top_k=20)
    res = reranker.rerank(cands, pq, top_k=5)
    
    top1 = res[0]
    target_hit = any(exp_target in c.chunk_id or (c.section_number and exp_target in c.section_number) for c in res[:2])
    status = "PASS" if target_hit else "FAIL"
    print(f"\n[{status}] {title}")
    print(f"  Top-1: [{top1.chunk_id}] Sec {top1.section_number}: {top1.section_title} (Page {top1.physical_page_start}) - Score: {top1.clinical_score:.4f}")
    target_rank = next((idx for idx, c in enumerate(res, 1) if exp_target in c.chunk_id or (c.section_number and exp_target in c.section_number)), None)
    print(f"  Target chunk rank: #{target_rank}")
