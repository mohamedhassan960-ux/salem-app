import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from query_understanding import ClinicalQueryUnderstanding
from hybrid_retriever import HybridRetriever
from reranker import INTERVENTION_SECTION_MAP, POPULATION_SECTION_MAP

# Load components
qu = ClinicalQueryUnderstanding()
ret = HybridRetriever.from_files(
    records_path=os.path.join(os.path.dirname(__file__), "..", "outputs", "retrieval_records_v2.json"),
    dense_npz_path=os.path.join(os.path.dirname(__file__), "..", "outputs", "dense_index_v2.npz"),
    dense_meta_path=os.path.join(os.path.dirname(__file__), "..", "outputs", "dense_metadata_v2.json"),
    model_name=os.path.join(os.path.dirname(__file__), "..", "data", "models", "multilingual-e5-small"),
)

def simulated_new_rerank(candidates, parsed_query):
    scored = []
    for cand in candidates:
        text_lower = cand.text.lower()
        sec = cand.section_number or ""
        cid = cand.chunk_id
        ctype = cand.content_type

        # 1. Relevance Base: Dense Semantic + Normalized RRF consensus
        dense_rel = cand.dense_score if cand.dense_score is not None else 0.5
        rrf_norm = min(1.0, cand.rrf_score / 0.035) if cand.rrf_score else 0.5
        relevance_score = (dense_rel * 0.70) + (rrf_norm * 0.30)

        # 2. Intervention Match
        intervention_score = 0.5
        if parsed_query.detected_interventions:
            matches = 0
            for intv_key in parsed_query.detected_interventions:
                expected_secs = INTERVENTION_SECTION_MAP.get(intv_key, set())
                if sec in expected_secs or cid in expected_secs:
                    matches += 1.0
                elif any(sec.startswith(es) for es in expected_secs if "." in es):
                    matches += 0.8
                elif intv_key.replace("_", " ") in text_lower:
                    matches += 0.5
            intervention_score = min(1.0, matches / max(1, len(parsed_query.detected_interventions)))

        # 3. Population Match
        population_score = 0.5
        if parsed_query.detected_populations:
            pop_matches = 0
            for pop_key in parsed_query.detected_populations:
                expected_pop_secs = POPULATION_SECTION_MAP.get(pop_key, set())
                if sec in expected_pop_secs or cid in expected_pop_secs:
                    pop_matches += 1.0
                elif pop_key.replace("_", " ") in text_lower:
                    pop_matches += 0.7
                elif pop_key == "pregnant_women" and ("pregnant" in text_lower or "pregnancy" in text_lower):
                    pop_matches += 1.0
                elif pop_key == "adolescents_young_people" and ("adolescent" in text_lower or "young" in text_lower or "children" in text_lower):
                    pop_matches += 1.0
                elif pop_key == "tuberculosis_patients" and ("tuberculosis" in text_lower or "tb" in text_lower):
                    pop_matches += 1.0
                elif pop_key == "seizure_disorder_patients" and ("seizure" in text_lower or "epilepsy" in text_lower):
                    pop_matches += 1.0
            population_score = min(1.0, pop_matches / max(1, len(parsed_query.detected_populations)))

        # 4. Calibrated Content-Type Prior (Additive)
        if ctype == "recommendation":
            ctype_bonus = 0.04
        elif ctype == "evidence":
            ctype_bonus = 0.03
        elif ctype in {"discussion", "implementation", "context", "narrative"}:
            ctype_bonus = 0.00
        elif ctype == "glossary":
            ctype_bonus = -0.02
        elif ctype in {"references", "appendix"}:
            ctype_bonus = -0.06
        else:
            ctype_bonus = 0.00

        # 5. Hub chunk penalty
        hub_penalty = 0.0
        if cid.startswith("chunk_node_L1_acknowledgements") or cid.startswith("chunk_node_L1_preface"):
            hub_penalty = 0.20
        elif ctype == "references" and not ("reference" in parsed_query.raw_query.lower()):
            hub_penalty = 0.15

        # 6. Combined Score
        if parsed_query.detected_interventions or parsed_query.detected_populations:
            base = (relevance_score * 0.50) + (intervention_score * 0.30) + (population_score * 0.20)
        else:
            base = relevance_score

        final_score = max(0.0, min(1.0, base + ctype_bonus - hub_penalty))
        scored.append((final_score, cand))

    scored.sort(key=lambda x: (x[0], -x[1].hybrid_rank), reverse=True)
    return scored

# Test Cases
test_queries = [
    ("Diagnostic: Background & LMIC statistics", "According to the 'Background' section, how many people globally use tobacco, and what specific percentage of these users live in Low- and Middle-Income Countries (LMICs)?", "chunk_node_L2_background"),
    ("Clinical Recommendation: Varenicline Dosing", "What is the recommended dosing schedule and duration for varenicline?", "chunk_sec_3_3_1"),
    ("Implementation: Reducing User Treatment Costs", "How can health systems and policies reduce tobacco user treatment costs in LMICs?", "chunk_sec_3_7_4_3"),
    ("Definition / Context: Brief Advice Definition", "What is the definition and duration of brief advice for tobacco cessation?", "chunk_sec_3_1_1"),
    ("Arabic Query: جرعة دواء الفارينيكلين", "ما هي الجرعة الموصى بها لدواء فارينيكلين وكيف يتم التدرج فيها؟", "chunk_sec_3_3_1"),
]

print("=================================================================")
print("  SIMULATING NEW RERANKER LOGIC ON 5 REGRESSION BENCHMARKS")
print("=================================================================")

for category, q_text, expected_target in test_queries:
    pq = qu.parse_query(q_text)
    cands = ret.retrieve(pq.expanded_search_query, top_k=20)
    reranked = simulated_new_rerank(cands, pq)
    
    top1_score, top1_cand = reranked[0]
    
    # Find rank of expected target
    target_rank = None
    target_score = None
    for rk, (sc, c) in enumerate(reranked, 1):
        if expected_target in c.chunk_id or (c.section_number and expected_target in c.section_number):
            target_rank = rk
            target_score = sc
            break
            
    is_pass = (target_rank is not None and target_rank <= 2)
    print(f"\n[{'PASS' if is_pass else 'FAIL'}] {category}")
    print(f"  Query: {q_text[:70]}...")
    print(f"  Top 1: [{top1_cand.chunk_id}] Sec {top1_cand.section_number}: {top1_cand.section_title} (Page {top1_cand.physical_page_start}) - Score: {top1_score:.4f}")
    if target_rank:
        print(f"  Expected target rank: #{target_rank} (Score: {target_score:.4f})")
    else:
        print(f"  Expected target NOT in Top-20!")
