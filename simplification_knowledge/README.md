# Medical Simplification Knowledge Base (Oxygen Project - Phase 1)

## Executive Summary
This directory contains the foundational, evidence-based, legally verified knowledge base for medical simplification in the **Oxygen** medical RAG system.

### Core Architectural Principle
> **Medical RAG determines:** *"WHAT IS MEDICALLY TRUE?"* (Authoritative medical evidence from PubMed/guidelines)
>
> **Simplification Knowledge Base determines:** *"HOW CAN THAT TRUTH BE EXPLAINED CLEARLY WITHOUT CHANGING ITS MEANING?"* (Plain-language communication & safety guardrails)
>
> ⚠️ **The Simplification Knowledge Base NEVER introduces, modifies, overrides, or supplements clinical facts.**

---

## Directory Layout
```text
simplification_knowledge/
├── README.md                          # Architecture, principles, and directory index
├── sources/
│   └── source_registry.json           # Legally audited 2-source CDC registry
├── rules/
│   └── simplification_rules.json      # 16 structured rules (Actions, Eval Criteria, Safety Constraints)
├── evaluation/
│   └── golden_test_set.json           # 12 clinical test scenarios with explicit must_preserve/must_not_change
├── reports/
│   ├── source_evaluation.md           # In-depth legal licensing & CDC source conversion audit
│   └── rule_validation_report.md      # Rule validation, conflict matrix, baseline evaluation & RAG analysis
└── tests/
    └── validate_knowledge_base.py     # Automated validation suite (14 verification checks)
```

---

## Primary Sources & Roles
1. **SOURCE-001 (CDC Everyday Words for Public Health Communication)**:
   - *Role*: **PRIMARY SIMPLIFICATION SOURCE** (Jargon replacement, familiar words, dual-context definitions).
   - *Status*: U.S. Public Domain (17 U.S.C. § 105), Commercially Reusable.
2. **SOURCE-002 (CDC Clear Communication Index)**:
   - *Role*: **SECONDARY COMMUNICATION QUALITY SOURCE** (Main message first, active voice, short chunks, natural frequencies, risk/benefit balance).
   - *Status*: U.S. Public Domain (17 U.S.C. § 105), Commercially Reusable.

---

## Rule Inventory (16 Entries)
- **8 ACTION_RULES**: Direct generative rewriting instructions for the LLM.
- **3 EVALUATION_CRITERIA**: Quantitative & qualitative benchmarks for assessing clarity.
- **5 SAFETY_CONSTRAINTS**: System-level architectural invariants ensuring 100% medical meaning & claim preservation.

---

## Automated Validation
To execute the automated validation suite (14 checks):
```powershell
python simplification_knowledge/tests/validate_knowledge_base.py
```
**Status:** All 14 checks passed with 100% compliance.

---

## Architectural Decision (Static Rules vs Simplification RAG)
- Total Knowledge Base size: **~1,250 tokens**
- Option Selected: **OPTION A (Static Rule Injection in LLM System Prompt)**
- A secondary vector database or retrieval layer is unnecessary for 16 rules and would only add latency and retrieval failure risks.
