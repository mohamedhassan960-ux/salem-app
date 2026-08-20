"""
Simplification Query Extractor — Medical RAG Project: Oxygen (أوكسجين)
Extracts communication needs and characteristics from retrieved Medical RAG evidence
to query the Simplification Knowledge Base without leaking medical diagnostic searches.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set


@dataclass
class SimplificationQuery:
    """Represents a structured query to the Simplification Knowledge Base."""
    search_query: str
    detected_features: List[str]
    target_categories: List[str]
    has_medication: bool = False
    has_dosage_or_units: bool = False
    has_numbers_or_percentages: bool = False
    has_uncertainty_or_hedging: bool = False
    has_association_or_correlation: bool = False
    has_contraindication_or_warning: bool = False
    has_behavioral_instructions: bool = False
    has_technical_terminology: bool = False
    is_egyptian_dialect: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "search_query": self.search_query,
            "detected_features": self.detected_features,
            "target_categories": self.target_categories,
            "has_medication": self.has_medication,
            "has_dosage_or_units": self.has_dosage_or_units,
            "has_numbers_or_percentages": self.has_numbers_or_percentages,
            "has_uncertainty_or_hedging": self.has_uncertainty_or_hedging,
            "has_association_or_correlation": self.has_association_or_correlation,
            "has_contraindication_or_warning": self.has_contraindication_or_warning,
            "has_behavioral_instructions": self.has_behavioral_instructions,
            "has_technical_terminology": self.has_technical_terminology,
            "is_egyptian_dialect": self.is_egyptian_dialect,
        }


class SimplificationQueryBuilder:
    """
    Builds a communication-oriented retrieval query from retrieved clinical evidence
    and the patient query, preventing the Simplification RAG from performing medical diagnosis.
    """

    # Lexical triggers in medical evidence
    UNCERTAINTY_TRIGGERS = {
        "may", "might", "could", "suggest", "suggests", "suggested", "preliminary",
        "low certainty", "very low certainty", "moderate certainty", "conditional",
        "inconclusive", "unproven", "insufficient evidence", "potential", "possible"
    }

    ASSOCIATION_TRIGGERS = {
        "associated with", "correlated with", "correlation", "observational",
        "cohort study", "link between", "linked to", "incidence of", "odds ratio",
        "relative risk", "risk factor"
    }

    CONTRAINDICATION_TRIGGERS = {
        "contraindicated", "contraindication", "black box warning", "do not use",
        "pregnant", "pregnancy", "lactation", "severe renal", "adverse reaction",
        "fatal", "warning", "caution", "emergency", "anaphylaxis", "angioedema"
    }

    MEDICATION_TRIGGERS = {
        "varenicline", "bupropion", "nrt", "nicotine replacement", "patch", "gum",
        "lozenge", "inhaler", "nasal spray", "cytisine", "pharmacotherapy",
        "medication", "drug", "prescribe", "titrate", "mg", "mcg", "dose", "daily"
    }

    BEHAVIORAL_TRIGGERS = {
        "step", "steps", "instruction", "counseling", "behavioral support",
        "brief advice", "quit date", "action plan", "wash", "take with", "prior to",
        "fasting", "empty stomach", "session", "support"
    }

    def build_query(
        self,
        medical_evidence: str,
        user_query: str = "",
        is_egyptian_dialect: bool = True,
    ) -> SimplificationQuery:
        """
        Analyzes the medical evidence text and constructs a simplification query.
        """
        ev_lower = (medical_evidence or "").lower()
        uq_lower = (user_query or "").lower()
        combined = f"{ev_lower} {uq_lower}"

        features: List[str] = []
        target_cats: Set[str] = set()

        # 1. Uncertainty / Hedging
        has_unc = any(re.search(rf"\b{re.escape(w)}\b", ev_lower) for w in self.UNCERTAINTY_TRIGGERS)
        if has_unc:
            features.append("UNCERTAINTY_PRESERVATION")
            target_cats.add("Uncertainty")

        # 2. Association vs Causation
        has_assoc = any(w in ev_lower for w in self.ASSOCIATION_TRIGGERS)
        if has_assoc:
            features.append("ASSOCIATION_VS_CAUSATION")
            target_cats.add("Association vs Causation")

        # 3. Contraindications / Red Flags
        has_contra = any(w in ev_lower for w in self.CONTRAINDICATION_TRIGGERS)
        if has_contra:
            features.append("CONTRAINDICATIONS_AND_WARNINGS")
            target_cats.add("Contraindications & Warnings")
            target_cats.add("Risk communication")

        # 4. Medication & Dosage
        has_med = any(re.search(rf"\b{re.escape(w)}\b", ev_lower) for w in self.MEDICATION_TRIGGERS)
        has_dose = bool(re.search(r"\b\d+(\.\d+)?\s*(mg|mcg|g|ml|tablets?|pills?|times?|daily|bid|tid|q\d+h)\b", ev_lower))
        if has_med:
            features.append("PHARMACOLOGICAL_ENTITIES")
            target_cats.add("Medical terminology")
        if has_dose:
            features.append("DOSAGE_AND_UNIT_INTEGRITY")
            target_cats.add("Dosage integrity")

        # 5. Numbers & Percentages
        has_num = bool(re.search(r"\b\d+(\.\d+)?\s*(%|percent|out of|\/\d+)\b", ev_lower)) or bool(re.search(r"\b\d{2,}\b", ev_lower))
        if has_num:
            features.append("NUMERICAL_FRAMING_NATURAL_FREQUENCIES")
            target_cats.add("Numbers")
            target_cats.add("Risk communication")

        # 6. Behavioral & Procedural Instructions
        has_beh = any(w in ev_lower for w in self.BEHAVIORAL_TRIGGERS) or any(w in uq_lower for w in ["إزاي", "كيف", "طريقة", "جرعة", "استخدام", "خطوات"])
        if has_beh:
            features.append("BEHAVIORAL_ACTION_STEPS")
            target_cats.add("Behavioral instructions")
            target_cats.add("Sentence structure")

        # Default foundational categories always targeted
        target_cats.add("Plain language")
        target_cats.add("Main-point prioritization")
        target_cats.add("Chunking")

        # Build search query string for retriever
        query_terms = [
            "plain language medical explanation",
            "clear communication everyday words",
        ]
        if has_unc:
            query_terms.append("preserve uncertainty hedging modal verbs")
        if has_med or has_dose:
            query_terms.append("medication names exact dosage units freezing")
        if has_num:
            query_terms.append("natural frequencies numbers in context statistics")
        if has_contra:
            query_terms.append("contraindication safety warnings emergency red flags")
        if has_assoc:
            query_terms.append("observational association vs direct causation")
        if has_beh:
            query_terms.append("active voice chronological sequential steps")

        search_query_str = " ".join(query_terms)

        return SimplificationQuery(
            search_query=search_query_str,
            detected_features=features,
            target_categories=sorted(list(target_cats)),
            has_medication=has_med,
            has_dosage_or_units=has_dose,
            has_numbers_or_percentages=has_num,
            has_uncertainty_or_hedging=has_unc,
            has_association_or_correlation=has_assoc,
            has_contraindication_or_warning=has_contra,
            has_behavioral_instructions=has_beh,
            has_technical_terminology=has_med or has_dose or ("syndrome" in ev_lower or "therapy" in ev_lower),
            is_egyptian_dialect=is_egyptian_dialect,
        )
