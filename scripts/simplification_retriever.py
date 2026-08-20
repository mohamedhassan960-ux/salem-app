"""
Simplification Retriever — Medical RAG Project: Oxygen (أوكسجين)
Retrieves and ranks plain-language communication guidance and safety constraints
from the Simplification Knowledge Base based on the characteristics of retrieved medical evidence.
"""

from __future__ import annotations

import os
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set

from simplification_query import SimplificationQuery, SimplificationQueryBuilder

RULES_JSON_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "simplification_knowledge",
    "rules",
    "simplification_rules.json",
)
SOURCES_JSON_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "simplification_knowledge",
    "sources",
    "source_registry.json",
)


@dataclass
class RetrievedSimplificationRule:
    """A scored and retrieved simplification rule with full source provenance."""
    rule_id: str
    rule_name: str
    rule_type: str  # ACTION_RULE, EVALUATION_CRITERION, SAFETY_CONSTRAINT
    category: str
    priority: str  # CRITICAL, HIGH, MEDIUM, LOW
    evidence_type: str
    source_id: str
    source_title: str
    organization: str
    source_location: str
    principle: str
    instruction_for_llm: str
    when_to_apply: str
    when_not_to_apply: str
    score: float = 0.0

    def to_prompt_text(self) -> str:
        """Formats the rule into an unambiguous prompt instruction block."""
        badge = f"[{self.priority}] {self.rule_type}: {self.rule_name}"
        provenance = f"Source: {self.source_title} ({self.source_id}) — {self.source_location}"
        return (
            f"• {badge}\n"
            f"  - Principle: {self.principle}\n"
            f"  - LLM Directive: {self.instruction_for_llm}\n"
            f"  - Provenance: {provenance}"
        )


@dataclass
class SimplificationRetrievalResult:
    """Contains retrieved rules and formatted communication guidance block."""
    rules: List[RetrievedSimplificationRule]
    safety_constraints: List[RetrievedSimplificationRule]
    action_rules: List[RetrievedSimplificationRule]
    query: SimplificationQuery

    def format_for_llm(self) -> str:
        """Formats all retrieved rules into fenced, non-medical communication guidance."""
        if not self.rules:
            return "NO SPECIALIZED SIMPLIFICATION RULES RETRIEVED. USE GENERAL PLAIN LANGUAGE."

        blocks: List[str] = []
        blocks.append("=== SIMPLIFICATION & COMMUNICATION GUIDANCE (CDC & SAFETY RULES) ===")
        blocks.append("NOTE: The following rules govern HOW to explain the medical evidence clearly in Egyptian Arabic.")
        blocks.append("DO NOT TREAT THESE RULES AS SOURCES OF MEDICAL FACTS.\n")

        if self.safety_constraints:
            blocks.append("[MANDATORY MEDICAL SAFETY CONSTRAINTS]")
            for r in self.safety_constraints:
                blocks.append(r.to_prompt_text())
            blocks.append("")

        if self.action_rules:
            blocks.append("[PLAIN LANGUAGE & COMMUNICATION ACTION RULES]")
            for r in self.action_rules:
                blocks.append(r.to_prompt_text())

        blocks.append("=== END SIMPLIFICATION GUIDANCE ===")
        return "\n".join(blocks)


class SimplificationRetriever:
    """
    Retrieves and ranks communication guidance matching the clinical evidence profile.
    """

    def __init__(
        self,
        rules_path: str = RULES_JSON_PATH,
        sources_path: str = SOURCES_JSON_PATH,
    ):
        self.rules_path = rules_path
        self.sources_path = sources_path
        self.sources: Dict[str, Dict[str, Any]] = {}
        self.rules: List[Dict[str, Any]] = []
        self._load_knowledge_base()

    def _load_knowledge_base(self) -> None:
        """Loads verified sources and rules from disk."""
        if os.path.exists(self.sources_path):
            with open(self.sources_path, "r", encoding="utf-8") as f:
                raw_sources = json.load(f)
                for s in raw_sources:
                    self.sources[s["source_id"]] = s
        else:
            logging.warning(f"Sources file not found at {self.sources_path}")

        # Add system source
        self.sources["SYSTEM"] = {
            "source_id": "SYSTEM",
            "title": "System Architecture Safety Invariant",
            "organization": "Oxygen Project Architecture",
            "copyright_status": "Internal Safety Policy",
        }

        if os.path.exists(self.rules_path):
            with open(self.rules_path, "r", encoding="utf-8") as f:
                self.rules = json.load(f)
        else:
            logging.warning(f"Rules file not found at {self.rules_path}")

    def retrieve(
        self,
        query: SimplificationQuery,
        top_k: int = 7,
    ) -> SimplificationRetrievalResult:
        """
        Retrieves, scores, and ranks rules matching the simplification query.
        Guarantees that active CRITICAL safety constraints are always present.
        """
        scored_rules: List[RetrievedSimplificationRule] = []

        query_tokens = set(query.search_query.lower().split())

        for r in self.rules:
            score = 0.0
            r_type = r.get("rule_type", "ACTION_RULE")
            category = r.get("category", "")
            priority = r.get("priority", "MEDIUM")
            principle = r.get("principle", "")
            instruction = r.get("instruction_for_llm", "")
            rule_id = r.get("rule_id", "")
            s_id = r.get("source_id", "SYSTEM")

            source_meta = self.sources.get(s_id, {})
            source_title = source_meta.get("title", s_id)
            org = source_meta.get("organization", "CDC / System")

            # Category match bonus
            if category in query.target_categories:
                score += 3.0

            # Feature-specific scoring boosts
            if query.has_uncertainty_or_hedging and ("Uncertainty" in category or rule_id == "RULE-SAFE-001"):
                score += 5.0
            if query.has_dosage_or_units and ("Dosage" in category or rule_id == "RULE-SAFE-002"):
                score += 5.0
            if query.has_association_or_correlation and ("Association" in category or rule_id == "RULE-SAFE-003"):
                score += 5.0
            if query.has_contraindication_or_warning and ("Contraindication" in category or rule_id == "RULE-SAFE-005"):
                score += 5.0
            if query.has_numbers_or_percentages and ("Numbers" in category or rule_id == "RULE-ACT-006"):
                score += 4.0
            if query.has_medication and ("terminology" in category.lower() or rule_id == "RULE-ACT-002"):
                score += 4.0
            if query.has_behavioral_instructions and ("Behavioral" in category or "Sentence" in category or rule_id == "RULE-ACT-004" or rule_id == "RULE-ACT-008"):
                score += 4.0

            # General plain language & main message baseline boost
            if rule_id in {"RULE-ACT-001", "RULE-ACT-003", "RULE-SAFE-004"}:
                score += 2.5

            # Lexical overlap bonus
            text_to_match = f"{principle} {instruction} {category} {r.get('rule_name', '')}".lower()
            overlap_count = sum(1 for token in query_tokens if token in text_to_match)
            score += overlap_count * 0.3

            # Priority baseline
            if priority == "CRITICAL":
                score += 2.0
            elif priority == "HIGH":
                score += 1.0

            # Only consider actionable rules and safety constraints for generation prompt
            if r_type in {"ACTION_RULE", "SAFETY_CONSTRAINT"}:
                retrieved_item = RetrievedSimplificationRule(
                    rule_id=rule_id,
                    rule_name=r.get("rule_name", ""),
                    rule_type=r_type,
                    category=category,
                    priority=priority,
                    evidence_type=r.get("evidence_type", "DIRECT_SOURCE_RULE"),
                    source_id=s_id,
                    source_title=source_title,
                    organization=org,
                    source_location=r.get("source_location", ""),
                    principle=principle,
                    instruction_for_llm=instruction,
                    when_to_apply=r.get("when_to_apply", ""),
                    when_not_to_apply=r.get("when_not_to_apply", ""),
                    score=score,
                )
                scored_rules.append(retrieved_item)

        # Sort by score descending
        scored_rules.sort(key=lambda x: x.score, reverse=True)

        # Separate safety constraints and action rules
        # Guarantee inclusion of core applicable safety constraints
        selected_safety: List[RetrievedSimplificationRule] = []
        selected_actions: List[RetrievedSimplificationRule] = []

        for item in scored_rules:
            if item.rule_type == "SAFETY_CONSTRAINT":
                # Include safety constraints that scored above base threshold or are critical
                if item.score >= 2.0 and item not in selected_safety:
                    selected_safety.append(item)
            elif item.rule_type == "ACTION_RULE":
                if len(selected_actions) < top_k:
                    selected_actions.append(item)

        # Combine selected rules
        all_selected = selected_safety + selected_actions

        return SimplificationRetrievalResult(
            rules=all_selected,
            safety_constraints=selected_safety,
            action_rules=selected_actions,
            query=query,
        )


def retrieve_simplification_guidance(
    medical_evidence: str,
    user_query: str = "",
    top_k: int = 6,
    retriever: Optional[SimplificationRetriever] = None,
) -> SimplificationRetrievalResult:
    """
    Convenience function to build query and retrieve simplification guidance.
    """
    builder = SimplificationQueryBuilder()
    q = builder.build_query(medical_evidence=medical_evidence, user_query=user_query)
    ret = retriever or SimplificationRetriever()
    return ret.retrieve(q, top_k=top_k)
