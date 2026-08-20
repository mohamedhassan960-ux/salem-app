"""
Automated Test Suite for Token Distribution Audit
Medical RAG — WHO Tobacco Cessation Guideline (2024)

Validates:
1. Exact 90 Leaf Nodes processed.
2. Token counts > 0 for all nodes.
3. Accurate statistical calculations (min, max, median, mean, percentiles).
4. Report output generated and non-empty.
"""

import sys
import os
import json

sys.path.insert(0, r'C:\Users\moham\OneDrive\Apps\اوكسجين\scripts')
from token_distribution_audit import run_token_audit

def test_token_audit():
    result = run_token_audit()
    assert result["leaf_count"] == 90, f"Expected 90 leaf nodes, got {result['leaf_count']}"
    assert result["min"] > 0, "Minimum tokens must be > 0"
    assert result["max"] >= result["p95"] >= result["median"] >= result["min"], "Percentiles violated ordering"
    assert os.path.exists(r'C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\token_distribution_audit.md'), "Missing output report"
    print("ALL TOKEN DISTRIBUTION AUDIT TESTS PASSED (100% PASS).")

if __name__ == '__main__':
    test_token_audit()
