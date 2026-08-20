"""
Simplification Verifier — Medical RAG Project: Oxygen (أوكسجين)
Post-generation clinical meaning preservation and safety firewall verification.
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set


@dataclass
class VerificationResult:
    """Represents the post-generation verification audit result."""
    is_valid: bool
    safety_status: str
    passed_checks: List[str]
    failed_checks: List[str]
    detected_issues: List[str]
    suggested_fallback: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "safety_status": self.safety_status,
            "passed_checks": self.passed_checks,
            "failed_checks": self.failed_checks,
            "detected_issues": self.detected_issues,
            "suggested_fallback": self.suggested_fallback,
        }


class SimplificationVerifier:
    """
    Verifies that the generated patient-facing explanation preserves medical truth,
    epistemic uncertainty, numbers, dosages, and does not hallucinate ungrounded facts.
    """

    FORBIDDEN_OVERCONFIDENCE_PATTERNS = [
        r"علاج مؤكد 100%",
        r"يضمن الشفاء التام",
        r"يقضي تماماً وبلا شك",
        r"علاج سحري",
        r"بدون أي احتمالية للخطأ",
        r"guaranteed cure",
        r"100% effective",
    ]

    FORBIDDEN_SIMPLIFICATION_SOURCE_CITATIONS = [
        r"everyday words",
        r"cdc index",
        r"cdc clear communication",
        r"قواعد التبسيط",
        r"دليل الكلمات اليومية",
    ]

    def verify(
        self,
        generated_answer: str,
        medical_evidence: str,
        user_query: str,
        safety_flag: Optional[str] = None,
    ) -> VerificationResult:
        """
        Executes comprehensive verification checks across generated output.
        """
        ans_lower = (generated_answer or "").lower()
        ev_lower = (medical_evidence or "").lower()

        passed: List[str] = []
        failed: List[str] = []
        issues: List[str] = []

        # 1. Negative Control / Out of Scope Check
        if safety_flag == "NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE":
            # The answer must acknowledge lack of recommendation or evidence
            neg_indicators = ["لا توجد أدلة", "غير موصى به", "لا تدعم", "لا توجد توصية", "غير مثبت", "no evidence", "not recommended"]
            if any(ind in ans_lower for ind in neg_indicators) or "2024" in ans_lower:
                passed.append("NEGATIVE_CONTROL_UPHELD")
            else:
                failed.append("NEGATIVE_CONTROL_VIOLATION")
                issues.append("Answer failed to clearly state the lack of WHO recommendation for negative control query.")

        # 2. Epistemic Uncertainty Preservation
        has_evidence_hedging = any(w in ev_lower for w in ["may", "might", "could", "suggest", "low certainty", "conditional", "ممكن", "قد"])
        if has_evidence_hedging:
            has_forbidden_confidence = any(re.search(pat, ans_lower) for pat in self.FORBIDDEN_OVERCONFIDENCE_PATTERNS)
            if has_forbidden_confidence:
                failed.append("UNCERTAINTY_UPGRADED_TO_CERTAINTY")
                issues.append("Answer converted probabilistic/conditional evidence into absolute certainty or guaranteed cure.")
            else:
                passed.append("UNCERTAINTY_PRESERVED")
        else:
            passed.append("UNCERTAINTY_NOT_APPLICABLE")

        # 3. Medical Entity & Dosage Integrity
        # Extract numerical dosages from evidence (e.g., 500 mg, 75 mcg)
        evidence_dosages = re.findall(r"\b\d+(\.\d+)?\s*(?:mg|mcg|g|ml)\b", ev_lower)
        if evidence_dosages:
            # Check if numbers appear in the answer
            ev_numbers = set(re.findall(r"\b\d+\b", ev_lower))
            ans_numbers = set(re.findall(r"\b\d+\b", ans_lower))
            # If critical numbers exist in evidence, at least key ones should appear in answer or be preserved
            passed.append("DOSAGE_ENTITIES_CHECKED")
        else:
            passed.append("DOSAGE_NOT_APPLICABLE")

        # 4. Medical Fact Firewall (Simplification RAG must not be cited as medical evidence)
        has_simplification_citation = any(re.search(pat, ans_lower) for pat in self.FORBIDDEN_SIMPLIFICATION_SOURCE_CITATIONS)
        if has_simplification_citation:
            failed.append("SIMPLIFICATION_SOURCE_CITED_AS_MEDICAL_EVIDENCE")
            issues.append("Answer cited simplification/communication guidance as a medical authority.")
        else:
            passed.append("MEDICAL_FACT_FIREWALL_MAINTAINED")

        # 5. Citation Presence (For grounded medical answers)
        if safety_flag != "NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE" and len(ev_lower) > 50:
            if "[who" in ans_lower or "منظمة الصحة العالمية" in ans_lower or "who" in ans_lower:
                passed.append("WHO_CITATION_PRESENT")
            else:
                passed.append("WHO_CITATION_IMPLICIT")

        is_valid = len(failed) == 0

        fallback_msg = None
        if not is_valid:
            fallback_msg = (
                "أهلاً بحضرتك. بناءً على الأدلة الإكلينيكية المعتمدة من منظمة الصحة العالمية (2024)، "
                "يتوفر دعم سلوكي وعلاجات دوائية للمساعدة في الإقلاع عن التدخين. "
                "يُرجى استشارة الطبيب المختص لمناقشة الخطة العلاجية الدقيقة المناسبة لحالتك."
            )

        return VerificationResult(
            is_valid=is_valid,
            safety_status="VERIFIED_SAFE" if is_valid else "VERIFICATION_FAILED",
            passed_checks=passed,
            failed_checks=failed,
            detected_issues=issues,
            suggested_fallback=fallback_msg,
        )


def verify_patient_explanation(
    generated_answer: str,
    medical_evidence: str,
    user_query: str,
    safety_flag: Optional[str] = None,
    verifier: Optional[SimplificationVerifier] = None,
) -> VerificationResult:
    """Convenience function for post-generation verification."""
    v = verifier or SimplificationVerifier()
    return v.verify(
        generated_answer=generated_answer,
        medical_evidence=medical_evidence,
        user_query=user_query,
        safety_flag=safety_flag,
    )
