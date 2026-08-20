"""
Evidence Quality Gate & Claim-Specific Evidence Validator — Medical RAG: Oxygen (أوكسجين)
Source Document: WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)

Applies rigorous clinical evidence gating and claim-specific validation:
1. Architectural Axiom: SEMANTIC SIMILARITY IS NOT MEDICAL EVIDENCE.
2. Evidence Classification Tiers:
   - DIRECT_EVIDENCE / DIRECT_SUPPORT: Directly evaluates/recommends the requested clinical intervention.
   - PARTIAL_SUPPORT: Directly addresses relevant symptoms/mechanisms (e.g. withdrawal headache).
   - RELATED_BUT_NOT_SUPPORTING: Topic-relevant (smoking cessation) but does NOT support the specific intervention/claim.
   - INSUFFICIENT: Generic boilerplate (acknowledgements, preface).
   - IRRELEVANT: Unrelated medical domain (orthopedics, diabetes, etc.).
   - POTENTIALLY_MISLEADING: Contradicts safety or misapplies unproven therapies.
   - NO_EVIDENCE: No compatible evidence found.

3. Negative Control & Out-of-Scope Guard:
   - General semantic similarity about tobacco cessation NEVER establishes support for an unsupported or unproven intervention.
   - If no direct/compatible evidence exists for the query's specific intervention, the gate REJECTS all candidates,
     setting is_grounded = False and safety_flag = "NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE" (triggering safe abstention).
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Set, Tuple

from reranker import RerankedCandidate
from query_understanding import ClinicalQueryRepresentation

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


@dataclass
class GatedEvidenceItem:
    """A reranked candidate enriched with evidence quality tier and gating decision."""
    chunk_id: str
    quality_tier: str                       # DIRECT_EVIDENCE, PARTIAL_SUPPORT, RELATED_BUT_NOT_SUPPORTING, INSUFFICIENT, IRRELEVANT, POTENTIALLY_MISLEADING
    is_admitted_to_context: bool            # True if passed into final LLM context
    gating_reason: str
    clinical_score: float
    rerank_position: int
    text: str
    section_number: Optional[str]
    section_title: str
    heading_path: str
    physical_page_start: Optional[int]
    physical_page_end: Optional[int]
    content_type: str
    retrieval_role: str
    document_id: str
    node_id: str
    parent_id: str
    token_count: int
    claim_supported: bool = False
    intervention_match: bool = False
    entity_match: bool = False
    evidence_decision: str = "REJECT"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EvidenceQualityGateResult:
    """Complete output of the Evidence Quality Gate for a single query."""
    raw_query: str
    is_grounded_in_guideline: bool          # False if out-of-scope or no direct/related evidence found
    safety_flag: Optional[str]              # e.g. NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE
    direct_evidence_count: int
    related_evidence_count: int
    blocked_count: int
    claim_supported: bool
    admitted_candidates: List[GatedEvidenceItem]
    all_evaluated_candidates: List[GatedEvidenceItem]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "raw_query": self.raw_query,
            "is_grounded_in_guideline": self.is_grounded_in_guideline,
            "safety_flag": self.safety_flag,
            "direct_evidence_count": self.direct_evidence_count,
            "related_evidence_count": self.related_evidence_count,
            "blocked_count": self.blocked_count,
            "claim_supported": self.claim_supported,
            "admitted_candidates": [c.to_dict() for c in self.admitted_candidates],
            "all_evaluated_candidates": [c.to_dict() for c in self.all_evaluated_candidates],
        }

    def to_context_assembler_sources(self) -> List[Dict[str, Any]]:
        """Converts admitted evidence items into dictionaries formatted for ContextAssembler."""
        sources = []
        for rank_idx, item in enumerate(self.admitted_candidates, start=1):
            dist = max(0.0, 1.0 - item.clinical_score)
            sources.append({
                "chunk_id": item.chunk_id,
                "document_id": item.document_id,
                "node_id": item.node_id,
                "parent_id": item.parent_id,
                "section_number": item.section_number,
                "section_title": item.section_title,
                "chunk_index": 0,
                "chunk_count": 1,
                "content_type": item.content_type,
                "physical_page_start": item.physical_page_start,
                "physical_page_end": item.physical_page_end,
                "token_count": item.token_count,
                "word_count": len(item.text.split()),
                "character_count": len(item.text),
                "source_type": "verbatim",
                "retrieval_role": item.retrieval_role,
                "split_reason": None,
                "distance": round(dist, 4),
                "rank": rank_idx,
                "text": item.text,
            })
        return sources


class EvidenceQualityGate:
    """
    Evaluates evidence quality and applies claim-specific medical safety filtering.
    """

    DIRECT_SCORE_THRESHOLD: float = 0.58
    RELATED_SCORE_THRESHOLD: float = 0.42

    INTERVENTION_KEYWORD_PATTERNS: Dict[str, List[str]] = {
        "varenicline": ["varenicline", "champix", "فارينيكلين", "تشامبكس"],
        "bupropion_sr": ["bupropion", "zyban", "wellbutrin", "بوبروبيون", "زيبان", "ويلبيوترين"],
        "cytisine": ["cytisine", "tabex", "سيتيسين", "سيتيزين", "تابيكس"],
        "nrt": ["nicotine replacement", "nrt", "بدائل النيكوتين", "بديل النيكوتين"],
        "nrt_patch": ["patch", "transdermal", "لصقة", "لزقة", "لزقه"],
        "nrt_gum": ["gum", "لبان", "علكة", "لبانة"],
        "nrt_spray_inhaler": ["spray", "inhaler", "بخاخ", "استنشاق"],
        "brief_advice": ["brief advice", "مشورة موجزة", "نصيحة موجزة", "30 seconds", "3 minutes"],
        "individual_counselling": ["individual", "فردية", "استشارة فردية", "جلسات فردية"],
        "group_counselling": ["group", "جماعية", "مجموعات", "دعم جماعي"],
        "digital_messaging": ["text messaging", "sms", "smartphone", "app", "تطبيق", "رسائل", "رسايل"],
        "quitline": ["quitline", "toll-free", "خط ساخن", "تليفون"],
        "unproven_alternatives": ["acupuncture", "laser", "hypnotherapy", "hypnosis", "إبر صينية", "ليزر", "تنويم", "اعشاب", "أعشاب", "ساونا", "sauna"],
    }

    def __init__(
        self,
        direct_threshold: float = DIRECT_SCORE_THRESHOLD,
        related_threshold: float = RELATED_SCORE_THRESHOLD,
    ):
        self.direct_threshold = direct_threshold
        self.related_threshold = related_threshold

    def _extract_query_specific_targets(self, parsed_query: ClinicalQueryRepresentation) -> Set[str]:
        """Identifies specific interventions or concepts explicitly demanded by the query."""
        raw_lower = parsed_query.raw_query.lower()
        targets: Set[str] = set()

        for group_name, patterns in self.INTERVENTION_KEYWORD_PATTERNS.items():
            for pat in patterns:
                if pat in raw_lower:
                    targets.add(group_name)
                    break
        return targets

    def _extract_unsupported_candidate_interventions(self, parsed_query: ClinicalQueryRepresentation, target_groups: Set[str]) -> List[str]:
        """Identifies candidate specific named interventions/therapies not recognized in guideline inventory."""
        if target_groups or parsed_query.detected_interventions:
            return []
        raw_lower = parsed_query.raw_query.lower()
        patterns = [
            r'\b(?:dosage|dose|taper\s+schedule)\s+of\s+(?:an?\s+)?(?:unlisted\s+)?([a-z0-9\-\_]+)',
            r'\b(?:is|does|about)\s+(?:a\s+)?(?:fictional\s+)?([a-z0-9\-\_]+)\s+(?:recommended|supported|effective|used|prescribed|appropriate|advise)',
            r'\b(?:drug|medication|agent|compound|psychedelic|substance|pill)\s+(?:called|named)?\s*([a-z0-9\-\_]+)',
            r'\b([a-z0-9\-\_]+)\-assisted\b',
            r'\b([a-z0-9\-\_]+)\s+(?:psychotherapy|pharmacotherapy|therapy|treatment|assisted)',
        ]
        GENERIC_WORDS = {
            "what", "which", "who", "the", "a", "an", "this", "that", "these", "those", "recommended",
            "pharmacological", "pharmacotherapy", "pharmacotherapies", "intervention", "interventions",
            "treatment", "treatments", "therapy", "therapies", "behavioral", "behavioural", "support",
            "clinical", "standard", "first-line", "medical", "cessation", "smoking", "tobacco", "unlisted",
            "fictional", "general", "oral", "digital", "counselling", "counseling", "advice", "guideline",
            "who", "duration", "outcome", "outcomes", "evidence", "review", "reviews", "called", "named"
        }
        extracted: List[str] = []
        for pat in patterns:
            matches = re.findall(pat, raw_lower)
            for m in matches:
                m_clean = m.strip()
                if m_clean and m_clean not in GENERIC_WORDS and len(m_clean) > 2:
                    extracted.append(m_clean)
        return list(set(extracted))

    def _check_chunk_mentions_target(
        self,
        chunk_text: str,
        target_groups: Set[str],
        parsed_query: Optional[ClinicalQueryRepresentation] = None,
    ) -> bool:
        """Verifies if chunk text explicitly addresses any of the targeted intervention groups."""
        if not target_groups:
            return True
        text_lower = chunk_text.lower()
        is_combo_query = parsed_query is not None and (
            "COMBINATION_THERAPY" in parsed_query.detected_intents
            or "combination_therapy" in parsed_query.detected_interventions
        )
        for group in target_groups:
            patterns = list(self.INTERVENTION_KEYWORD_PATTERNS.get(group, []))
            # If the query explicitly seeks combination therapy involving NRT, authorize combination NRT terminology
            if is_combo_query and group in {"nrt_patch", "nrt_gum", "nrt_spray_inhaler", "nrt"}:
                patterns.extend(["combination nrt", "combination nicotine replacement", "علاج تعويضي مركب", "بدائل النيكوتين المركبة"])
            for pat in patterns:
                if pat in text_lower:
                    return True
        return False

    def evaluate_candidates(
        self,
        candidates: List[RerankedCandidate],
        parsed_query: ClinicalQueryRepresentation,
        final_budget_k: int = 5,
    ) -> EvidenceQualityGateResult:
        """
        Classifies all candidates using claim-specific evidence validation and selects Top-K evidence.
        """
        raw_lower = parsed_query.raw_query.lower()

        # 1. Immediate Out-of-Scope / Domain Mismatch Guard
        # Only permit candidate evaluation if a specific proven guideline intervention is explicitly requested alongside
        SPECIFIC_PROVEN_INTERVENTIONS = {
            "varenicline", "bupropion_sr", "cytisine", "nicotine_replacement_therapy",
            "nrt_transdermal_patch", "nrt_gum", "combination_therapy", "brief_advice",
            "physician_brief_advice_or_counselling", "individual_intensive_counselling",
            "group_behavioural_counselling", "toll_free_quitline", "mobile_text_messaging_sms",
            "digital_smartphone_interventions", "ai_chatbot_interventions"
        }
        has_specific_proven = any(i in SPECIFIC_PROVEN_INTERVENTIONS for i in parsed_query.detected_interventions)
        
        # Domain Mismatch: The guideline strictly addresses tobacco cessation in adult smokers.
        # Primary prevention of tobacco initiation in non-smokers or youth is out of guideline scope.
        is_prevention_intent = "PRIMARY_PREVENTION" in parsed_query.detected_intents or any(
            p in raw_lower for p in ["prevention of initiation", "prevent initiation", "primary prevention", "never smoked", "non-smoker", "non smoker"]
        )
        if is_prevention_intent and ("non_smokers" in parsed_query.detected_populations or "adolescents_young_people" in parsed_query.detected_populations or "PRIMARY_PREVENTION" in parsed_query.detected_intents):
            return EvidenceQualityGateResult(
                raw_query=parsed_query.raw_query,
                is_grounded_in_guideline=False,
                safety_flag="OUT_OF_SCOPE_PRIMARY_PREVENTION_NOT_COVERED_IN_CESSATION_GUIDELINE",
                direct_evidence_count=0,
                related_evidence_count=0,
                blocked_count=len(candidates),
                claim_supported=False,
                admitted_candidates=[],
                all_evaluated_candidates=[],
            )

        if parsed_query.is_out_of_scope and not has_specific_proven:
            return EvidenceQualityGateResult(
                raw_query=parsed_query.raw_query,
                is_grounded_in_guideline=False,
                safety_flag="NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE",
                direct_evidence_count=0,
                related_evidence_count=0,
                blocked_count=len(candidates),
                claim_supported=False,
                admitted_candidates=[],
                all_evaluated_candidates=[],
            )

        # Check for unproven / negative control queries
        is_unproven_query = any(k in raw_lower for k in [
            "ليزر", "laser", "ساونا", "sauna", "تعرق", "أعشاب", "اعشاب", "عشبة",
            "القديس يوحنا", "سانت جون", "st john", "سجائر عشبية", "سجاير عشبية",
            "إبر صينية", "ابر صينية", "وخز بالإبر", "acupuncture", "تنويم مغناطيسي", "hypnotherapy", "فيب", "e-cigarette", "vape"
        ])

        # ABSOLUTE DRUG BLOCKLIST — runs unconditionally before any target_group logic.
        # These substances are NOT covered in the WHO 2024 tobacco cessation guideline under any circumstance.
        # A query mentioning them must be blocked even if it also mentions legitimate interventions.
        ABSOLUTE_DRUG_BLOCKLIST: Dict[str, str] = {
            "psilocybin": "سيلوسيبين",
            "psylocibin": "سيلوسيبين",
            "سيلوسيبين": "سيلوسيبين",
            "ketamine": "كيتامين",
            "كيتامين": "كيتامين",
            "mdma": "mdma",
            "lsd": "lsd",
            "ibogaine": "ibogaine",
            "ayahuasca": "ayahuasca",
            "مخدر السيلوسيبين": "سيلوسيبين",
            "سيلوسايبين": "سيلوسيبين",
        }
        for blocklist_term in ABSOLUTE_DRUG_BLOCKLIST:
            if blocklist_term in raw_lower:
                logging.info(
                    f"[EvidenceGate] ABSOLUTE_BLOCKLIST hit: '{blocklist_term}' detected in query. "
                    f"Blocking ALL candidates — substance not in WHO 2024 guideline."
                )
                return EvidenceQualityGateResult(
                    raw_query=parsed_query.raw_query,
                    is_grounded_in_guideline=False,
                    safety_flag="UNSUPPORTED_INTERVENTION_NOT_VERIFIED",
                    direct_evidence_count=0,
                    related_evidence_count=0,
                    blocked_count=len(candidates),
                    claim_supported=False,
                    admitted_candidates=[],
                    all_evaluated_candidates=[],
                )

        target_groups = self._extract_query_specific_targets(parsed_query)
        has_specific_drug_query = any(g in target_groups for g in ["varenicline", "bupropion_sr", "cytisine", "nrt_patch", "nrt_gum", "nrt_spray_inhaler"])

        # Unsupported Specific Intervention Guard:
        # If the query asks about a specific named therapy/drug not recognized in guideline inventory,
        # verify whether any candidate chunk explicitly supports it. If no recognized target exists
        # and unindexed specific candidate interventions were requested, strictly abstain.
        unsupported_candidates = self._extract_unsupported_candidate_interventions(parsed_query, target_groups)
        if unsupported_candidates and not is_unproven_query and not has_specific_proven:
            # Check if any candidate chunk verbatim text actually contains the candidate intervention
            has_matching_chunk = False
            for cand in candidates:
                cand_lower = cand.text.lower()
                if any(cand_intervention in cand_lower for cand_intervention in unsupported_candidates):
                    has_matching_chunk = True
                    break
            if not has_matching_chunk:
                return EvidenceQualityGateResult(
                    raw_query=parsed_query.raw_query,
                    is_grounded_in_guideline=False,
                    safety_flag="UNSUPPORTED_INTERVENTION_NOT_VERIFIED",
                    direct_evidence_count=0,
                    related_evidence_count=0,
                    blocked_count=len(candidates),
                    claim_supported=False,
                    admitted_candidates=[],
                    all_evaluated_candidates=[],
                )

        evaluated: List[GatedEvidenceItem] = []
        direct_items: List[GatedEvidenceItem] = []
        related_items: List[GatedEvidenceItem] = []

        for cand in candidates:
            cid = cand.chunk_id
            sec = cand.section_number or ""
            ctype = cand.content_type
            score = cand.clinical_score
            cand_text = cand.text

            tier = "IRRELEVANT"
            reason = "Default initial state"
            claim_supported = False
            intervention_match = False
            entity_match = False
            decision = "REJECT"

            # Check boilerplate
            if cid.startswith("chunk_node_L1_acknowledgements") or cid.startswith("chunk_node_L1_preface"):
                tier = "INSUFFICIENT"
                reason = "Generic organizational preface / acknowledgements boilerplate"
                decision = "REJECT"

            # Check Section 3.6 (Unproven therapies)
            elif sec.startswith("3.6"):
                if is_unproven_query:
                    tier = "DIRECT_EVIDENCE"
                    reason = "Direct WHO Section 3.6 evidence confirming lack of recommendation for unproven intervention."
                    claim_supported = True
                    intervention_match = True
                    entity_match = True
                    decision = "ADMIT"
                else:
                    tier = "POTENTIALLY_MISLEADING"
                    reason = "Unproven alternative therapy section irrelevant to standard clinical query"
                    decision = "REJECT"

            # Check unproven query with standard cessation chunks
            elif is_unproven_query:
                tier = "RELATED_BUT_NOT_SUPPORTING"
                reason = f"Chunk discusses general cessation/pharmacotherapy ({sec}) but does NOT support unproven query topic."
                claim_supported = False
                intervention_match = False
                decision = "REJECT"

            # Check specific drug queries
            elif has_specific_drug_query:
                chunk_mentions_drug = self._check_chunk_mentions_target(cand_text, target_groups, parsed_query)
                if chunk_mentions_drug and score >= self.direct_threshold:
                    tier = "DIRECT_EVIDENCE"
                    reason = f"High clinical relevance ({score:.3f}) with specific drug/intervention match."
                    claim_supported = True
                    intervention_match = True
                    entity_match = True
                    decision = "ADMIT"
                elif chunk_mentions_drug and score >= self.related_threshold:
                    tier = "PARTIAL_SUPPORT"
                    reason = f"Specific drug match in section ({sec}) with moderate score ({score:.3f})."
                    claim_supported = True
                    intervention_match = True
                    entity_match = True
                    decision = "ADMIT"
                else:
                    tier = "RELATED_BUT_NOT_SUPPORTING"
                    reason = f"General cessation context ({sec}) without specific target drug match."
                    claim_supported = False
                    intervention_match = False
                    decision = "REJECT"

            # General Tobacco Cessation / Behavioral / Symptom queries
            elif score >= self.direct_threshold and (cand.intervention_match_score >= 0.5 or cand.population_match_score >= 0.5 or ctype == "recommendation"):
                tier = "DIRECT_EVIDENCE"
                reason = f"High clinical relevance ({score:.3f}) with intervention/population match"
                claim_supported = True
                intervention_match = True
                entity_match = True
                decision = "ADMIT"

            elif score >= self.related_threshold or ctype in {"evidence", "recommendation"}:
                tier = "RELATED_EVIDENCE"
                reason = f"Contextually relevant chapter ({sec}) supporting general cessation query."
                claim_supported = True
                intervention_match = True
                decision = "ADMIT"

            else:
                tier = "IRRELEVANT"
                reason = f"Below minimum relevance threshold ({score:.3f} < {self.related_threshold})"
                decision = "REJECT"

            item = GatedEvidenceItem(
                chunk_id=cid,
                quality_tier=tier,
                is_admitted_to_context=False,
                gating_reason=reason,
                clinical_score=cand.clinical_score,
                rerank_position=cand.rerank_position,
                text=cand.text,
                section_number=cand.section_number,
                section_title=cand.section_title,
                heading_path=cand.heading_path,
                physical_page_start=cand.physical_page_start,
                physical_page_end=cand.physical_page_end,
                content_type=cand.content_type,
                retrieval_role=cand.retrieval_role,
                document_id=cand.document_id,
                node_id=cand.node_id,
                parent_id=cand.parent_id,
                token_count=cand.token_count,
                claim_supported=claim_supported,
                intervention_match=intervention_match,
                entity_match=entity_match,
                evidence_decision=decision,
            )
            evaluated.append(item)

            if tier in {"DIRECT_EVIDENCE", "PARTIAL_SUPPORT"}:
                direct_items.append(item)
            elif tier == "RELATED_EVIDENCE":
                related_items.append(item)

        # 2. Admission Policy
        admitted: List[GatedEvidenceItem] = []

        if (is_unproven_query or has_specific_drug_query) and len(direct_items) == 0:
            admitted = []
        else:
            for item in direct_items[:final_budget_k]:
                item.is_admitted_to_context = True
                admitted.append(item)

            remaining_slots = final_budget_k - len(admitted)
            if remaining_slots > 0 and len(direct_items) > 0 and not is_unproven_query:
                for item in related_items[:remaining_slots]:
                    item.is_admitted_to_context = True
                    admitted.append(item)
            elif remaining_slots > 0 and not has_specific_drug_query and not is_unproven_query:
                for item in related_items[:remaining_slots]:
                    item.is_admitted_to_context = True
                    admitted.append(item)

        # 3. Overall Grounding Check
        is_grounded = len(admitted) > 0 and not is_unproven_query
        safety_flag = None
        if is_unproven_query or not is_grounded:
            is_grounded = False
            safety_flag = "NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE"

        return EvidenceQualityGateResult(
            raw_query=parsed_query.raw_query,
            is_grounded_in_guideline=is_grounded,
            safety_flag=safety_flag,
            direct_evidence_count=len(direct_items),
            related_evidence_count=len(related_items),
            blocked_count=len(evaluated) - len(admitted),
            claim_supported=is_grounded,
            admitted_candidates=admitted,
            all_evaluated_candidates=evaluated,
        )
