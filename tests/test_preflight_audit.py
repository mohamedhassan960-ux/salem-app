"""
Pre-Flight Architectural Audit Test Suite
Medical RAG — WHO Tobacco Cessation Guideline (2024)

Performs comprehensive in-memory dry run audit on all 112 nodes without writing production outputs.
Generates audit findings for outputs/verbatim_slicer_preflight_audit.md.
"""

import sys
import os
import re
import json

sys.path.insert(0, r'C:\Users\moham\OneDrive\Apps\اوكسجين\scripts')
from verbatim_structural_slicer import VerbatimStructuralSlicer

def run_preflight_audit():
    src_path = r'C:\Users\moham\OneDrive\Apps\اوكسجين\data\who_extracted.txt'
    map_path = r'C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\structure_map_v2.json'

    slicer = VerbatimStructuralSlicer(src_path, map_path)
    slicer.load_resources()

    all_nodes = slicer.nodes
    print(f"Auditing all {len(all_nodes)} nodes in Structure Map v2...")

    results = []
    status_counts = {}
    failed_nodes = []
    parent_child_stats = []

    for node in all_nodes:
        res = slicer.slice_node(node)
        results.append(res)
        st = res['extraction_status']
        status_counts[st] = status_counts.get(st, 0) + 1
        if st != 'SUCCESS':
            failed_nodes.append(res)

    print("\n--- EXTRACTION STATUS SUMMARY ---")
    for st, count in status_counts.items():
        print(f"  {st}: {count} nodes")

    if failed_nodes:
        print(f"\n--- FAILED NODES ({len(failed_nodes)}) ---")
        for fn in failed_nodes:
            print(f"  Node: {fn['node_id']} | Title: {fn['title']} | Status: {fn['extraction_status']} | StartFound: {fn['start_boundary_found']} | EndFound: {fn['end_boundary_found']}")

    # Check parent vs children duplication statistics
    node_map = {n['node_id']: n for n in all_nodes}
    res_map = {r['node_id']: r for r in results}
    
    parent_nodes = [n for n in all_nodes if n.get('children')]
    print(f"\nTotal Branch/Parent Nodes with children: {len(parent_nodes)}")
    leaf_nodes = [n for n in all_nodes if not n.get('children')]
    print(f"Total Leaf Nodes (terminal sections): {len(leaf_nodes)}")

    total_words_extracted_all_nodes = sum(r['word_count'] for r in results)
    total_words_leaf_nodes = sum(res_map[n['node_id']]['word_count'] for n in leaf_nodes if n['node_id'] in res_map)
    print(f"Total words across all 112 nodes (including parents): {total_words_extracted_all_nodes:,}")
    print(f"Total words across {len(leaf_nodes)} LEAF nodes: {total_words_leaf_nodes:,}")

    return {
        'total_nodes': len(all_nodes),
        'status_counts': status_counts,
        'failed_nodes': failed_nodes,
        'leaf_count': len(leaf_nodes),
        'parent_count': len(parent_nodes),
        'total_words_all': total_words_extracted_all_nodes,
        'total_words_leaf': total_words_leaf_nodes,
        'results': results
    }

if __name__ == '__main__':
    audit_data = run_preflight_audit()
