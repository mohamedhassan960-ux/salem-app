import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from query_understanding import ClinicalQueryUnderstanding
from hybrid_retriever import HybridRetriever
from reranker import ClinicalReranker
from evidence_quality_gate import EvidenceQualityGate

q = "According to the 'Background' section, how many people globally use tobacco, and what specific percentage of these users live in Low- and Middle-Income Countries (LMICs)?"

qu = ClinicalQueryUnderstanding()
pq = qu.parse_query(q)

print("=== 1. QUERY UNDERSTANDING ===")
print("is_arabic:", pq.is_arabic)
print("intents:", pq.detected_intents)
print("interventions:", pq.detected_interventions)
print("expanded_search_query:", pq.expanded_search_query)

ret = HybridRetriever.from_files(
    records_path=os.path.join(os.path.dirname(__file__), "..", "outputs", "retrieval_records_v2.json"),
    dense_npz_path=os.path.join(os.path.dirname(__file__), "..", "outputs", "dense_index_v2.npz"),
    dense_meta_path=os.path.join(os.path.dirname(__file__), "..", "outputs", "dense_metadata_v2.json"),
    model_name=os.path.join(os.path.dirname(__file__), "..", "data", "models", "multilingual-e5-small"),
)

cands = ret.retrieve(pq.expanded_search_query, top_k=20)
print("\n=== 2. TOP 5 RETRIEVED HYBRID CANDIDATES ===")
for i, c in enumerate(cands[:5]):
    print(f"{i+1}. [Chunk: {c.chunk_id}] Sec {c.section_number}: {c.section_title} (Page {c.physical_page_start}) - RRF Score: {c.rrf_score:.4f}")
    print(f"   Snippet: {c.text[:140]}...")

rer = ClinicalReranker()
rk = rer.rerank(cands, pq, top_k=20)
print("\n=== 3. TOP 5 RERANKED CANDIDATES ===")
for i, c in enumerate(rk[:5]):
    print(f"{i+1}. [Chunk: {c.chunk_id}] Sec {c.section_number}: {c.section_title} (Page {c.physical_page_start}) - Score: {c.clinical_score:.4f}")

qg = EvidenceQualityGate()
gate = qg.evaluate_candidates(rk, pq, final_budget_k=5)
print("\n=== 4. QUALITY GATE DECISION ===")
print("is_grounded:", gate.is_grounded_in_guideline)
print("safety_flag:", gate.safety_flag)
print("admitted count:", len(gate.admitted_candidates))
for i, c in enumerate(gate.admitted_candidates[:5]):
    print(f"\n{i+1}. [Chunk: {c.chunk_id}] Sec {c.section_number}: {c.section_title} (Page {c.physical_page_start}) - Tier: {c.quality_tier}")
    print(f"   Gating Reason: {c.gating_reason}")
    print(f"   Text:\n{c.text}\n")
