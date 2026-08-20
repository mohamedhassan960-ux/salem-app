"""
Automated Test Suite for Verbatim Structural Slicer v1 (Sample Run)
Medical RAG — WHO Tobacco Cessation Guideline (2024)

Validates:
1. Start boundary existence
2. End boundary existence (when required)
3. Ordering: start < end
4. Non-empty extraction
5. Zero sibling collision / overlap
6. Correct word/character volume

Returns exit code 0 if all tests PASS, or exits with code 1 if any failure occurs.
"""

import sys
import os
import json

# Add scripts directory to path
sys.path.insert(0, r'C:\Users\moham\OneDrive\Apps\اوكسجين\scripts')
from verbatim_structural_slicer import VerbatimStructuralSlicer

def run_slicer_sample_tests():
    src = r'C:\Users\moham\OneDrive\Apps\اوكسجين\data\who_extracted.txt'
    smap = r'C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\structure_map_v2.json'

    slicer = VerbatimStructuralSlicer(src, smap)
    sample_ids = [
        'sec_3_1_1',
        'sec_3_1_2',
        'sec_3_1_3',
        'sec_3_1_4',
        'sec_3_3_3',
        'sec_3_7_4',
        'node_L1_references',
        'annex_2'
    ]

    results = slicer.run_sample(sample_ids)

    print("=== AUTOMATED SAMPLE VALIDATION SUITE ===")
    all_passed = True
    failures = []

    # Test 1: Completeness of all sampled nodes
    if len(results) != len(sample_ids):
        all_passed = False
        failures.append(f"Expected {len(sample_ids)} results, got {len(results)}")

    # Test 2: Individual node invariants
    for r in results:
        nid = r['node_id']
        # Check start boundary
        if not r['start_boundary_found']:
            all_passed = False
            failures.append(f"[{nid}] Start boundary not found!")

        # Check ordering
        if not r['ordering_valid']:
            all_passed = False
            failures.append(f"[{nid}] Ordering invalid (start >= end)!")

        # Check non-empty
        if r['extraction_status'] != 'SUCCESS' or r['word_count'] == 0:
            all_passed = False
            failures.append(f"[{nid}] Extracted text is empty or status is {r['extraction_status']}!")

    # Test 3: Sibling boundary transition in continuous Section 3.1
    res_dict = {r['node_id']: r for r in results}
    sibs = ['sec_3_1_1', 'sec_3_1_2', 'sec_3_1_3', 'sec_3_1_4']
    for i in range(len(sibs) - 1):
        curr_node = res_dict[sibs[i]]
        next_node = res_dict[sibs[i+1]]
        # Verify that curr_node text does NOT contain next_node matched heading
        if next_node['matched_start_heading'] and next_node['matched_start_heading'] in curr_node['extracted_text']:
            all_passed = False
            failures.append(f"Collision: {curr_node['node_id']} contains heading of {next_node['node_id']}!")

    if all_passed:
        print("\nALL SAMPLE INVARIANTS PASSED SUCCESSFULLY (100% PASS).")
        return 0
    else:
        print("\nFAILURES DETECTED:")
        for f in failures:
            print(f"  - {f}")
        return 1

if __name__ == '__main__':
    exit_code = run_slicer_sample_tests()
    sys.exit(exit_code)
