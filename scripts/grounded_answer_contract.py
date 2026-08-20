"""
Grounded Answer Contract Module — Medical RAG: Oxygen (اوكسجين)
Source Document: WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)

Architectural Principle:
NO GROUNDED EVIDENCE -> NO NORMAL LLM GENERATION.

This module is a deterministic safety contract between the Evidence Quality Gate
/ Claim Validator and the LLM Generator Layer. It enforces the circuit breaker
that prevents the LLM from answering unsupported or out-of-scope clinical
questions from pre-trained memory.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Any, Optional

from evidence_quality_gate import EvidenceQualityGateResult
from claim_validator import ClaimCoverageReport

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class ContractState(str, Enum):
    """Deterministic contract states governing LLM generation eligibility."""
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    ABSTAIN = "ABSTAIN"


@dataclass
class GroundedAnswerContractResult:
    """Structured contract result evaluated prior to any LLM generation call."""
    state: ContractState
    safety_flag: Optional[str]
    is_generation_allowed: bool
    claim_coverage_ratio: float
    deterministic_response: Optional[str]
    reason: str
    supported_claims: List[Dict[str, Any]] = field(default_factory=list)
    unsupported_claims: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["state"] = self.state.value
        return d


class GroundedAnswerContract:
    """
    Deterministic safety layer. Evaluates EvidenceQualityGateResult and
    ClaimCoverageReport, and enforces the rule:
        No Grounded Evidence -> No Normal LLM Generation.
    """

    # Deterministic Arabic abstention templates.
    # Avoid asserting universal WHO non-recommendation; prefer indexed-guideline scope language.
    DETERMINISTIC_RESPONSES: Dict[str, str] = {
        "UNSUPPORTED_INTERVENTION_NOT_VERIFIED": (
            "وفقاً لدليل منظمة الصحة العالمية المتاح في قاعدة المعرفة، لم يتم العثور على دليل أو توصية معتمدة "
            "تدعم هذا التدخل تحديداً للإقلاع عن التدخين. "
            "لذلك لا يمكنني تقديم جرعة أو جدول علاجي له اعتماداً على هذا الدليل."
        ),
        "OUT_OF_SCOPE_PRIMARY_PREVENTION_NOT_COVERED_IN_CESSATION_GUIDELINE": (
            "دليل منظمة الصحة العالمية المستخدم في قاعدة المعرفة مخصص لتقديم إرشادات حول الإقلاع عن استخدام التبغ للمدخنين، "
            "ولا يغطي برامج الوقاية الأولية من بدء التدخين لغير المدخنين أو اليافعين ضمن نطاقه الحالي. "
            "لذلك لا يمكنني تقديم توصية علاجية لهذا الاستخدام اعتماداً على هذا الدليل."
        ),
        "NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE": (
            "لم يتم العثور على دليل كافٍ داخل دليل منظمة الصحة العالمية المستخدم في قاعدة المعرفة "
            "للإجابة عن هذا السؤال بثقة. "
            "لذلك لن أقدّم توصية علاجية غير مدعومة بالمصدر المتاح."
        ),
        "DEFAULT_UNSUPPORTED": (
            "لم يتم العثور على أدلة سريرية كافية في دليل منظمة الصحة العالمية المعتمد لدعم هذا الاستفسار."
        ),
    }

    # Safety flags that map to OUT_OF_SCOPE (population/domain mismatch)
    OUT_OF_SCOPE_FLAGS = frozenset({
        "OUT_OF_SCOPE_PRIMARY_PREVENTION_NOT_COVERED_IN_CESSATION_GUIDELINE",
    })

    # Safety flags that map to UNSUPPORTED (specific un-indexed intervention)
    UNSUPPORTED_FLAGS = frozenset({
        "UNSUPPORTED_INTERVENTION_NOT_VERIFIED",
    })

    # Safety flags that map to ABSTAIN (no guideline evidence at all)
    ABSTAIN_FLAGS = frozenset({
        "NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE",
    })

    @classmethod
    def evaluate(
        cls,
        gate_result: EvidenceQualityGateResult,
        claim_report: ClaimCoverageReport,
    ) -> GroundedAnswerContractResult:
        """
        Deterministically evaluates the contract state.
        Called AFTER EvidenceQualityGate and ClaimCoverageValidator.
        Called BEFORE ContextAssembler / LLMGenerator.
        """
        flag = gate_result.safety_flag
        is_gate_grounded = gate_result.is_grounded_in_guideline
        admitted_count = len(gate_result.admitted_candidates)
        coverage_ratio = claim_report.claim_coverage_ratio

        supported_claims = [c.to_dict() for c in claim_report.claims if c.is_supported]
        unsupported_claims = [c.to_dict() for c in claim_report.claims if not c.is_supported]

        # ── 1. OUT_OF_SCOPE ────────────────────────────────────────────────
        # Primary prevention, population mismatch, domain entirely outside guideline
        if flag in cls.OUT_OF_SCOPE_FLAGS or (
            not is_gate_grounded and flag and "OUT_OF_SCOPE" in flag
        ):
            return GroundedAnswerContractResult(
                state=ContractState.OUT_OF_SCOPE,
                safety_flag=flag,
                is_generation_allowed=False,
                claim_coverage_ratio=0.0,
                deterministic_response=cls.DETERMINISTIC_RESPONSES.get(
                    flag, cls.DETERMINISTIC_RESPONSES["OUT_OF_SCOPE_PRIMARY_PREVENTION_NOT_COVERED_IN_CESSATION_GUIDELINE"]
                ),
                reason="Query falls outside the clinical scope of the WHO adult cessation guideline.",
                supported_claims=[],
                unsupported_claims=unsupported_claims,
            )

        # ── 2. UNSUPPORTED ─────────────────────────────────────────────────
        # Specific named intervention not indexed or verified in guideline corpus
        if flag in cls.UNSUPPORTED_FLAGS:
            return GroundedAnswerContractResult(
                state=ContractState.UNSUPPORTED,
                safety_flag=flag,
                is_generation_allowed=False,
                claim_coverage_ratio=0.0,
                deterministic_response=cls.DETERMINISTIC_RESPONSES["UNSUPPORTED_INTERVENTION_NOT_VERIFIED"],
                reason="Requested specific intervention is unindexed or unsupported in the guideline evidence.",
                supported_claims=[],
                unsupported_claims=unsupported_claims,
            )

        # ── 3. ABSTAIN ─────────────────────────────────────────────────────
        # Negative control / unproven therapy / zero grounded evidence
        if (
            flag in cls.ABSTAIN_FLAGS
            or not is_gate_grounded
            or admitted_count == 0
        ):
            return GroundedAnswerContractResult(
                state=ContractState.ABSTAIN,
                safety_flag=flag or "NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE",
                is_generation_allowed=False,
                claim_coverage_ratio=0.0,
                deterministic_response=cls.DETERMINISTIC_RESPONSES["NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE"],
                reason="Evidence quality gate or claim coverage identified zero grounded supporting evidence.",
                supported_claims=[],
                unsupported_claims=unsupported_claims,
            )

        # ── 4. PARTIALLY_SUPPORTED ─────────────────────────────────────────
        # Evidence exists but satisfies only a subset of the required claims
        if claim_report.grounding_decision == "PARTIALLY_GROUNDED" or (
            0.0 < coverage_ratio < 0.8
        ):
            return GroundedAnswerContractResult(
                state=ContractState.PARTIALLY_SUPPORTED,
                safety_flag=flag,
                is_generation_allowed=True,
                claim_coverage_ratio=coverage_ratio,
                deterministic_response=None,
                reason=(
                    "Evidence partially supports the query claims. "
                    "Generation is permitted but the prompt must explicitly constrain the LLM "
                    "to answer only the supported portion and to state unsupported sub-questions."
                ),
                supported_claims=supported_claims,
                unsupported_claims=unsupported_claims,
            )

        # ── 5. SUPPORTED ───────────────────────────────────────────────────
        return GroundedAnswerContractResult(
            state=ContractState.SUPPORTED,
            safety_flag=flag,
            is_generation_allowed=True,
            claim_coverage_ratio=coverage_ratio,
            deterministic_response=None,
            reason="Admitted evidence fully supports the requested clinical query.",
            supported_claims=supported_claims,
            unsupported_claims=unsupported_claims,
        )
