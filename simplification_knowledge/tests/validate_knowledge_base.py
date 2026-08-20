"""
Medical Simplification Knowledge Base Automated Validation Suite
Phase 18 Comprehensive Verification
"""

import json
import sys
from pathlib import Path

# Force UTF-8 on Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCES_FILE = BASE_DIR / "sources" / "source_registry.json"
RULES_FILE = BASE_DIR / "rules" / "simplification_rules.json"
TESTS_FILE = BASE_DIR / "evaluation" / "golden_test_set.json"

VALID_RULE_TYPES = {"ACTION_RULE", "EVALUATION_CRITERION", "SAFETY_CONSTRAINT"}
VALID_PRIORITIES = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
VALID_EVIDENCE_TYPES = {"DIRECT_SOURCE_RULE", "SOURCE_EXAMPLE", "COMMUNICATION_CRITERION", "DERIVED_RULE"}


def load_json(filepath):
    if not filepath.exists():
        raise FileNotFoundError(f"Missing required file: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def run_all_validations():
    print("=" * 75)
    print("STARTING OXYGEN MEDICAL SIMPLIFICATION KNOWLEDGE BASE VALIDATION (PHASE 18)")
    print("=" * 75)

    sources = load_json(SOURCES_FILE)
    rules = load_json(RULES_FILE)
    golden_tests = load_json(TESTS_FILE)

    source_map = {s["source_id"]: s for s in sources}
    source_ids = set()
    rule_ids = set()
    errors = []
    warnings = []

    # Check 1: Every source has a unique source_id
    print("[Check 1/14] Verifying source ID uniqueness and presence...")
    for s in sources:
        s_id = s.get("source_id")
        if not s_id:
            errors.append(f"Source missing source_id: {s.get('title', 'Unknown')}")
        elif s_id in source_ids:
            errors.append(f"Duplicate source_id found: {s_id}")
        else:
            source_ids.add(s_id)

    # Check 2: Every rule has a unique rule_id
    print("[Check 2/14] Verifying rule ID uniqueness and presence...")
    for rule in rules:
        r_id = rule.get("rule_id")
        if not r_id:
            errors.append(f"Rule missing rule_id: {rule.get('rule_name', 'Unknown')}")
        elif r_id in rule_ids:
            errors.append(f"Duplicate rule_id found: {r_id}")
        else:
            rule_ids.add(r_id)

    # Check 3: Every rule references an existing source (or SYSTEM for architectural constraints)
    print("[Check 3/14] Verifying source references...")
    for rule in rules:
        s_id = rule.get("source_id")
        r_type = rule.get("rule_type")
        if not s_id:
            errors.append(f"Rule {rule.get('rule_id')} missing source_id.")
        elif s_id == "SYSTEM":
            if r_type != "SAFETY_CONSTRAINT":
                errors.append(f"Rule {rule.get('rule_id')} has source_id 'SYSTEM' but rule_type is '{r_type}' (must be SAFETY_CONSTRAINT).")
        elif s_id not in source_map:
            errors.append(f"Rule {rule.get('rule_id')} references unknown source_id: '{s_id}'")

    # Check 4: Every rule has source_location
    print("[Check 4/14] Verifying source location traceability...")
    for rule in rules:
        loc = rule.get("source_location")
        if not loc or len(loc.strip()) < 5:
            errors.append(f"Rule {rule.get('rule_id')} missing specific source_location.")

    # Check 5: Every rule has valid evidence_type
    print("[Check 5/14] Verifying evidence_type values...")
    for rule in rules:
        ev_type = rule.get("evidence_type")
        if ev_type not in VALID_EVIDENCE_TYPES:
            errors.append(f"Rule {rule.get('rule_id')} has invalid evidence_type: '{ev_type}'")

    # Check 6: Every ACTION_RULE has when_to_apply
    # Check 7: Every ACTION_RULE has when_not_to_apply
    print("[Check 6/14 & 7/14] Verifying when_to_apply and when_not_to_apply on ACTION_RULES...")
    for rule in rules:
        r_type = rule.get("rule_type")
        if r_type not in VALID_RULE_TYPES:
            errors.append(f"Rule {rule.get('rule_id')} has invalid rule_type: '{r_type}'")
        if r_type == "ACTION_RULE":
            w_apply = rule.get("when_to_apply")
            w_not_apply = rule.get("when_not_to_apply")
            if not w_apply or len(w_apply.strip()) < 8:
                errors.append(f"ACTION_RULE {rule.get('rule_id')} missing valid 'when_to_apply'.")
            if not w_not_apply or len(w_not_apply.strip()) < 5:
                errors.append(f"ACTION_RULE {rule.get('rule_id')} missing valid 'when_not_to_apply'.")

    # Check 8: Every rule has a clear purpose (principle and instruction_for_llm)
    print("[Check 8/14] Verifying clear purpose and instructions...")
    for rule in rules:
        principle = rule.get("principle")
        instruction = rule.get("instruction_for_llm")
        if not principle or len(principle.strip()) < 10:
            errors.append(f"Rule {rule.get('rule_id')} missing concise principle.")
        if not instruction or len(instruction.strip()) < 15:
            errors.append(f"Rule {rule.get('rule_id')} missing clear instruction_for_llm.")

    # Check 9: Derived rules are explicitly labeled
    print("[Check 9/14] Verifying derived rule labeling...")
    for rule in rules:
        ev_type = rule.get("evidence_type")
        if ev_type == "DERIVED_RULE":
            summary = rule.get("source_evidence_summary", "")
            if "derived" not in summary.lower() and "architectural" not in summary.lower():
                warnings.append(f"DERIVED_RULE {rule.get('rule_id')} should explicitly describe derivation in source_evidence_summary.")

    # Check 10: No rule introduces medical facts (rules are meta-linguistic rewriting instructions)
    print("[Check 10/14] Verifying absence of external medical facts in rules...")
    banned_medical_fact_triggers = [
        "treatment of choice is", "first-line therapy is", "cure for", "prescribe exactly",
        "recommended dosage for diabetes is", "etiology is always"
    ]
    for rule in rules:
        instruction = rule.get("instruction_for_llm", "").lower()
        for trigger in banned_medical_fact_triggers:
            if trigger in instruction:
                errors.append(f"Rule {rule.get('rule_id')} appears to introduce an external clinical fact: '{trigger}'")

    # Check 11: No safety constraint is falsely attributed to CDC
    print("[Check 11/14] Verifying safety constraints attribution integrity...")
    for rule in rules:
        if rule.get("rule_type") == "SAFETY_CONSTRAINT":
            s_id = rule.get("source_id")
            if s_id != "SYSTEM":
                errors.append(f"SAFETY_CONSTRAINT {rule.get('rule_id')} must have source_id 'SYSTEM', not '{s_id}'.")

    # Check 12: Every golden test defines must_preserve
    # Check 13: Every golden test defines must_not_change
    print("[Check 12/14 & 13/14] Verifying golden test cases structure (must_preserve & must_not_change)...")
    if len(golden_tests) < 12:
        errors.append(f"Golden test set has {len(golden_tests)} cases; minimum required is 12.")
    for tc in golden_tests:
        t_id = tc.get("test_id")
        med_input = tc.get("medical_input")
        must_preserve = tc.get("must_preserve")
        must_not_change = tc.get("must_not_change")
        safety = tc.get("safety_constraints")

        if not t_id or not med_input:
            errors.append(f"Golden test case missing test_id or medical_input: {t_id}")
        if not must_preserve or not isinstance(must_preserve, list) or len(must_preserve) == 0:
            errors.append(f"Golden test {t_id} missing must_preserve list.")
        if not must_not_change or not isinstance(must_not_change, list) or len(must_not_change) == 0:
            errors.append(f"Golden test {t_id} missing must_not_change list.")
        if not safety or not isinstance(safety, list) or len(safety) == 0:
            errors.append(f"Golden test {t_id} missing safety_constraints list.")

    # Check 14: No unsupported licensing claims exist
    print("[Check 14/14] Verifying licensing evidence across all sources...")
    for s in sources:
        com = s.get("commercial_use")
        ev = s.get("license_evidence")
        if com == "YES":
            if not ev or len(ev.strip()) < 15:
                errors.append(f"Source {s.get('source_id')} claims commercial_use == 'YES' without sufficient license_evidence.")

    # Summary Output
    print("\n" + "=" * 75)
    print("VALIDATION SUMMARY REPORT")
    print("=" * 75)
    print(f"Sources in Registry:          {len(sources)}")
    print(f"Total Extracted Rules:        {len(rules)}")
    print(f"  - ACTION_RULES:             {sum(1 for r in rules if r.get('rule_type') == 'ACTION_RULE')}")
    print(f"  - EVALUATION_CRITERIA:      {sum(1 for r in rules if r.get('rule_type') == 'EVALUATION_CRITERION')}")
    print(f"  - SAFETY_CONSTRAINTS:       {sum(1 for r in rules if r.get('rule_type') == 'SAFETY_CONSTRAINT')}")
    print(f"Golden Test Cases:            {len(golden_tests)}")
    print("-" * 75)
    print(f"Errors:                       {len(errors)}")
    print(f"Warnings:                     {len(warnings)}")

    if warnings:
        print("\nWARNINGS:")
        for w in warnings:
            print(f"  [WARN] {w}")

    if errors:
        print("\nERRORS (VALIDATION FAILED):")
        for e in errors:
            print(f"  [ERROR] {e}")
        print("\nRESULT: FAILED")
        return False
    else:
        print("\nRESULT: ALL 14 VALIDATION CHECKS PASSED (100% COMPLIANT)")
        return True


if __name__ == "__main__":
    success = run_all_validations()
    sys.exit(0 if success else 1)
