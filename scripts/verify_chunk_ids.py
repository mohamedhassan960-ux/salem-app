import json

with open('outputs/retrieval_records_v2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

all_ids = {r['chunk_id']: r for r in data['records']}
print(f"Loaded {len(all_ids)} chunk IDs from retrieval_records_v2.json")

test_ids = [
    'chunk_node_L3_3_3_1_pharmacological_inte_p01',
    'chunk_node_L3_3_3_1_pharmacological_inte_p02',
    'chunk_node_L5_cytisine',
    'chunk_node_L3_3_3_2_pharmacological_inte',
    'chunk_node_L3_interventions_for_smokele',
    'chunk_node_L4_nrt',
    'chunk_node_L3_3_1_1_brief_advice',
    'chunk_node_L3_3_1_2_individual_behaviour',
    'chunk_node_L3_3_1_3_group_behavioural_su',
    'chunk_node_L3_3_2_digital_tobacco_cessa',
    'chunk_node_L3_digital_tobacco_cessation',
    'chunk_node_L3_3_1_4_telephone_counselling_',
    'chunk_node_L3_combination_of_behavioura',
    'chunk_node_L3_3_4_combination_of_behav',
    'chunk_node_L3_general_p01',
    'chunk_node_L5_varenicline',
    'chunk_node_L3_3_6_system_level_interve',
    'chunk_node_L3_system_level_intervention',
    'chunk_node_L1_glossary_of_terms_p26',
    'chunk_node_L3_traditional_complementary',
    'chunk_node_L3_3_5_traditional_complemen',
    'chunk_node_L2_products'
]

missing = [cid for cid in test_ids if cid not in all_ids]
if missing:
    print(f"MISSING IDs: {missing}")
else:
    print("ALL target chunk IDs VERIFIED in 171 retrieval records!")
    for cid in test_ids:
        r = all_ids[cid]
        print(f"  OK: {cid} | p.{r['provenance'].get('physical_page_start')} | {r['hierarchy'].get('section_title')}")
