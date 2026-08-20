"""
Claim-Level Evidence Coverage & Grounding Validator — Medical RAG: Oxygen (أوكسجين)
Source Document: WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)

Architectural Principle:
WHO provenance != Claim support
Medical relevance != Claim support
High retrieval score != Claim support
DIRECT_EVIDENCE chunk != Automatically grounded answer

This module implements deterministic, claim-level evidence mapping:
Question -> Required Claims -> Evidence Extraction & Mapping -> Claim Support Evaluation -> Coverage Ratio -> Grounding Decision
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Set, Tuple

from query_understanding import ClinicalQueryRepresentation

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


@dataclass
class ClaimRequirement:
    """A distinct verifiable requirement extracted from the user's question."""
    claim_id: str
    claim_text: str
    claim_type: str                         # numeric, percentage, recommendation, intervention, factual, definition, population, section_specific, out_of_scope, metric
    required_entities: List[str] = field(default_factory=list)
    required_section: Optional[str] = None  # e.g. "background", "3.3.1"
    numeric_required: bool = False          # True if specific number/count is requested
    percentage_required: bool = False       # True if specific percentage/rate is requested
    keywords: List[str] = field(default_factory=list)
    subject_entity: Optional[str] = None    # Specific subject entity (e.g. semaglutide, metformin)
    # --- Phase 5: Metric-level precision fields ---
    metric_type: Optional[str] = None       # "NNT", "NNH", "RR", "OR", "HR", "CI", "absolute_risk", "relative_risk"
    metric_outcome: Optional[str] = None    # e.g. "sustained_abstinence", "serious_adverse_events"
    metric_comparator: Optional[str] = None # e.g. "placebo", "bupropion"
    metric_time_point: Optional[str] = None # e.g. "6_months"
    required_value_patterns: List[str] = field(default_factory=list)  # Specific numeric strings to look for in evidence
    metric_required: bool = False           # True if a specific metric value must be present in evidence

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ClaimEvidenceCitation:
    """Provenance metadata for an evidence citation directly attached to a supported claim."""
    claim_id: str
    chunk_id: str
    section_number: Optional[str] = None
    section_title: Optional[str] = None
    heading_path: Optional[str] = None
    physical_page_start: Optional[int] = None
    source_name: str = "WHO"
    evidence_text: str = ""
    support_level: str = "DIRECT_SUPPORT"
    relevance_score: float = 0.0

    def to_citation_string(self) -> str:
        """
        Dynamically renders faithful citation without fabricating missing metadata:
        - If both section_number and section_title exist:
          '[WHO — Section 3.2.1 — Digital tobacco cessation modalities — Page 32]'
        - If only section_number:
          '[WHO — Section 3.3 — Page 45]'
        - If only section_title:
          '[WHO — Background — Page 15]'
        - If only page:
          '[WHO — Page 15]'
        - Never fabricates '3.3' or guessed section numbers.
        """
        parts = [self.source_name]
        sec_num_clean = (self.section_number or "").strip()
        sec_title_clean = (self.section_title or "").strip()

        if sec_num_clean and sec_title_clean:
            if sec_title_clean.lower().startswith(sec_num_clean.lower()):
                sec_title_clean = sec_title_clean[len(sec_num_clean):].strip(" .-:\t")
            if sec_title_clean:
                parts.append(f"Section {sec_num_clean} — {sec_title_clean}")
            else:
                parts.append(f"Section {sec_num_clean}")
        elif sec_num_clean:
            parts.append(f"Section {sec_num_clean}")
        elif sec_title_clean:
            parts.append(sec_title_clean)

        if self.physical_page_start is not None:
            parts.append(f"Page {self.physical_page_start}")

        return f"[{' — '.join(parts)}]"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["citation_tag"] = self.to_citation_string()
        return d


@dataclass
class ClaimValidationResult:
    """Validation result for a single question claim against retrieved/admitted evidence."""
    claim_id: str
    claim_text: str
    claim_type: str
    support_level: str                      # DIRECT_SUPPORT, PARTIAL_SUPPORT, UNSUPPORTED
    is_supported: bool                      # True if DIRECT_SUPPORT or PARTIAL_SUPPORT
    supporting_chunk_ids: List[str] = field(default_factory=list)
    support_reason: str = ""
    matched_entities: List[str] = field(default_factory=list)
    missing_entities: List[str] = field(default_factory=list)
    citations: List[ClaimEvidenceCitation] = field(default_factory=list)
    primary_citation: Optional[ClaimEvidenceCitation] = None
    primary_citation_tag: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "claim_id": self.claim_id,
            "claim_text": self.claim_text,
            "claim_type": self.claim_type,
            "support_level": self.support_level,
            "is_supported": self.is_supported,
            "supporting_chunk_ids": self.supporting_chunk_ids,
            "support_reason": self.support_reason,
            "matched_entities": self.matched_entities,
            "missing_entities": self.missing_entities,
            "citations": [c.to_dict() for c in self.citations],
            "primary_citation": self.primary_citation.to_dict() if self.primary_citation else None,
            "primary_citation_tag": self.primary_citation_tag,
        }
        return d


@dataclass
class ClaimCoverageReport:
    """Comprehensive claim coverage evaluation report for the full query."""
    raw_query: str
    total_required_claims: int
    supported_claims_count: int
    partially_supported_claims_count: int
    unsupported_claims_count: int
    claim_coverage_ratio: float             # 0.0 to 1.0 (supported_claims / total_required_claims)
    grounding_decision: str                 # FULLY_GROUNDED, PARTIALLY_GROUNDED, NOT_GROUNDED, NO_GROUNDED_EVIDENCE
    claims: List[ClaimValidationResult]
    overall_reason: str
    citations: List[ClaimEvidenceCitation] = field(default_factory=list)
    primary_citation_tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "raw_query": self.raw_query,
            "total_required_claims": self.total_required_claims,
            "supported_claims_count": self.supported_claims_count,
            "partially_supported_claims_count": self.partially_supported_claims_count,
            "unsupported_claims_count": self.unsupported_claims_count,
            "claim_coverage_ratio": self.claim_coverage_ratio,
            "grounding_decision": self.grounding_decision,
            "claims": [c.to_dict() for c in self.claims],
            "overall_reason": self.overall_reason,
            "citations": [c.to_dict() for c in self.citations],
            "primary_citation_tags": self.primary_citation_tags,
        }


class ClaimCoverageValidator:
    """
    Deterministic Claim-Level Evidence Coverage Validator.
    Deconstructs queries into semantic claim requirements, maps evidence to each claim,
    and calculates true Question-Claim Coverage.
    """

    # Section keyword mapping
    SECTION_KEYWORDS: Dict[str, List[str]] = {
        "background": ["background", "خلفية", "الخلفية", "مقدمة", "المقدمة"],
        "recommendation": ["recommendation", "recommendations", "توصية", "توصيات"],
        "implementation": ["implementation", "تطبيق", "تنفيذ"],
        "cost": ["cost", "cost-effectiveness", "تكلفة", "اقتصاديات"],
        "unproven": ["unproven", "alternative", "غير مثبتة", "بديلة"],
    }

    # Entity keyword mapping for clinical detection
    ENTITY_MAP: Dict[str, List[str]] = {
        "varenicline": ["varenicline", "champix", "فارينيكلين", "تشامبكس"],
        "bupropion": ["bupropion", "zyban", "wellbutrin", "بوبروبيون", "زيبان", "ويلبيوترين"],
        "cytisine": ["cytisine", "tabex", "سيتيسين", "سيتيزين", "تابيكس"],
        "nrt": ["nicotine replacement", "nrt", "بدائل النيكوتين", "بديل النيكوتين"],
        "nrt_patch": ["patch", "transdermal", "لصقة", "لزقة", "لزقه"],
        "nrt_gum": ["gum", "علكة", "لبان", "لبانة"],
        "brief_advice": ["brief advice", "مشورة موجزة", "نصيحة موجزة"],
        "counselling": ["counselling", "استشارة", "جلسات"],
        "digital_cessation": ["text messaging", "sms", "smartphone", "app", "تطبيق", "رسائل"],
        "quitline": ["quitline", "toll-free", "خط ساخن", "تليفون"],
        "lmic": ["lmic", "lmics", "low- and middle-income", "low and middle income", "الدول منخفضة ومتوسطة الدخل", "منخفضة ومتوسطة الدخل"],
        "global_users": ["global", "globally", "worldwide", "عالمياً", "عالميا", "حول العالم", "في العالم", "مستوى العالم", "على مستوى العالم", "العالمي", "عالمي"],
        "metformin": ["metformin", "ميتفورمين", "الميتفورمين"],
        "e_cigarettes": ["e-cigarette", "e-cigarettes", "vape", "vaping", "سجائر إلكترونية", "سجائر الكترونية", "فيب", "شيشة إلكترونية"],
        "acupuncture": ["acupuncture", "إبر صينية", "ابر صينية"],
        "laser": ["laser", "ليزر"],
        "hypnotherapy": ["hypnotherapy", "hypnosis", "تنويم مغناطيسي", "تنويم"],
    }

    STOP_WORDS = {
        "what", "does", "the", "who", "for", "and", "how", "many", "much", "why", "when", "where",
        "which", "with", "this", "that", "from", "into", "over", "after", "about", "tobacco", "smoking",
        "cessation", "adults", "guideline", "guidelines", "clinical", "recommend", "recommended", "recommendation",
        "recommendations", "help", "quit", "quitting", "people", "treatment", "adult", "guide", "according",
        "section", "sections", "chapter", "page", "statement", "report", "document", "world", "health",
        "organization", "give", "tell", "explain", "describe", "discuss", "stated", "mentioned", "contains",
        "هل", "ما", "ماذا", "هو", "هي", "في", "من", "عن", "على", "إلى", "الى", "دليل", "منظمة",
        "الصحة", "العالمية", "التدخين", "الإقلاع", "الاقلاع", "علاج", "توصية", "توصيات", "قسم", "فصل", "صفحة"
    }

    def __init__(self):
        pass

    def _extract_subject_candidates(self, query: str) -> List[str]:
        """Extracts candidate specific medical entities / foreign nouns from the query."""
        tokens = re.findall(r"[\w\-]+", query.lower())
        candidates = [t for t in tokens if t not in self.STOP_WORDS and len(t) > 3 and not t.isdigit()]
        # Remove any words that match known section names
        clean_candidates = []
        for c in candidates:
            if not any(c in patterns for patterns in self.SECTION_KEYWORDS.values()):
                clean_candidates.append(c)
        return clean_candidates

    def extract_claims(self, query: str, parsed_query: Optional[ClinicalQueryRepresentation] = None) -> List[ClaimRequirement]:
        """
        Extracts verifiable claims/requirements from the user's natural language question.
        Handles single and composite questions in English and Arabic.
        """
        q_lower = query.lower().strip()
        claims: List[ClaimRequirement] = []

        # 1. Check for Explicit Section Requirement
        explicit_section = None
        for sec_name, sec_patterns in self.SECTION_KEYWORDS.items():
            for pat in sec_patterns:
                if pat in q_lower:
                    explicit_section = sec_name
                    break
            if explicit_section:
                break

        # 2. Check for Negative Control / Out-of-scope Entities
        out_of_scope_entities = []
        for ent in ["metformin", "semaglutide", "ozempic", "e_cigarettes", "acupuncture", "laser", "hypnotherapy"]:
            patterns = self.ENTITY_MAP.get(ent, [ent])
            if any(p in q_lower for p in patterns):
                out_of_scope_entities.append(ent)

        SPECIFIC_PROVEN_INTERVENTIONS = {
            "varenicline", "bupropion_sr", "cytisine", "nicotine_replacement_therapy",
            "nrt_transdermal_patch", "nrt_gum", "combination_therapy", "brief_advice",
            "physician_brief_advice_or_counselling", "individual_intensive_counselling",
            "group_behavioural_counselling", "toll_free_quitline", "mobile_text_messaging_sms",
            "digital_smartphone_interventions", "ai_chatbot_interventions"
        }
        has_specific_proven = any(i in SPECIFIC_PROVEN_INTERVENTIONS for i in (parsed_query.detected_interventions if parsed_query else []))

        if parsed_query and parsed_query.is_out_of_scope and not has_specific_proven:
            claims.append(ClaimRequirement(
                claim_id="claim_1",
                claim_text=f"WHO evaluation of unsupported/out-of-scope intervention ({', '.join(out_of_scope_entities) if out_of_scope_entities else 'out_of_scope'})",
                claim_type="out_of_scope",
                required_entities=out_of_scope_entities,
                required_section=explicit_section,
                keywords=out_of_scope_entities,
            ))
            return claims

        # 3. PRIORITY BRANCH: Clinical Metric Queries (NNT, NNH, RR, OR, HR, CI, etc.)
        # Must check BEFORE generic drug recommendation branch to prevent false 100% grounding.
        # E.g.: "What is the NNT for varenicline?" → 1 metric claim (NNT, numeric value required)
        # E.g.: "What is the NNT and NNH for varenicline?" → 2 metric claims (NNT + NNH, each requiring numeric value)
        METRIC_KEYWORDS = {
            "NNT": ["nnt", "number needed to treat", "number-needed-to-treat"],
            "NNH": ["nnh", "number needed to harm", "number-needed-to-harm"],
            "RR":  ["relative risk", " rr ", "risk ratio"],
            "OR":  ["odds ratio", " or ", "adjusted or"],
            "HR":  ["hazard ratio", " hr ", "hazard"],
            "CI":  ["confidence interval", " ci ", "95%"],
            "ARR": ["absolute risk reduction", "arr"],
            "ARI": ["absolute risk increase", "ari"],
        }

        detected_metrics: List[Tuple[str, str]] = []   # (metric_type, matched_pattern)
        for metric_type, patterns in METRIC_KEYWORDS.items():
            for pat in patterns:
                if pat in q_lower:
                    detected_metrics.append((metric_type, pat))
                    break

        if detected_metrics:
            # Identify which known clinical drug entities are in query
            metric_drug_entities = []
            for drug in ["varenicline", "bupropion", "cytisine", "nrt", "nrt_patch", "nrt_gum"]:
                patterns = self.ENTITY_MAP.get(drug, [])
                if any(p in q_lower for p in patterns):
                    metric_drug_entities.append(drug)

            # Detect unknown/out-of-scope drugs in the query (e.g. semaglutide, ozempic, metformin)
            OUT_OF_SCOPE_DRUGS = {
                "semaglutide": ["semaglutide", "ozempic", "wegovy"],
                "metformin": ["metformin"],
                "e_cigarettes": ["e-cigarette", "e-cigarettes", "vape", "vaping"],
                "acupuncture": ["acupuncture"],
                "laser": ["laser therapy"],
                "hypnotherapy": ["hypnotherapy", "hypnosis"],
            }
            metric_out_of_scope = []
            for oos, pats in OUT_OF_SCOPE_DRUGS.items():
                if any(p in q_lower for p in pats):
                    metric_out_of_scope.append(oos)

            # Build final entity requirement list:
            # - If known drugs found → use them
            # - If unknown/OOS drugs found → also include them (ensures evidence entity check fails)
            # - If neither → default to varenicline (most common NNT/NNH query subject)
            all_metric_entities = metric_drug_entities + metric_out_of_scope
            if not all_metric_entities:
                all_metric_entities = ["varenicline"]

            # Identify outcome context for each metric
            OUTCOME_KEYWORDS = {
                "sustained_abstinence": ["sustained abstinence", "continuous abstinence", "smoking abstinence", "abstinence at 6", "long-term abstinence", "abstinence"],
                "serious_adverse_events": ["serious adverse event", "saes", "sae", "serious adverse", "adverse events"],
                "neuropsychiatric": ["neuropsychiatric", "psychiatric", "npsychiatric"],
                "cardiovascular": ["cardiovascular", "cardiac", "heart"],
            }
            TIME_POINT_KEYWORDS = {
                "6_months": ["6 month", "6-month", "six month", "at 6"],
                "12_months": ["12 month", "12-month", "one year"],
                "52_weeks": ["52 week", "52-week"],
            }

            def detect_outcome(text: str) -> Optional[str]:
                for outcome, kws in OUTCOME_KEYWORDS.items():
                    if any(kw in text for kw in kws):
                        return outcome
                return None

            def detect_time_point(text: str) -> Optional[str]:
                for tp, kws in TIME_POINT_KEYWORDS.items():
                    if any(kw in text for kw in kws):
                        return tp
                return None

            # Pair detected metrics with detected drugs
            # If multiple drugs (e.g. varenicline + semaglutide), generate a metric claim per drug!
            target_drugs = all_metric_entities if all_metric_entities else ["varenicline"]
            claim_idx = 1

            for drug_name in target_drugs:
                for metric_type, _ in detected_metrics:
                    outcome = detect_outcome(q_lower)
                    time_pt = detect_time_point(q_lower)

                    metric_kws = [metric_type.lower(), drug_name]
                    if metric_type == "NNT":
                        metric_kws += ["nnt", "number needed to treat"]
                        value_patterns = ["nnt", "number needed to treat"]
                    elif metric_type == "NNH":
                        metric_kws += ["nnh", "number needed to harm", "adverse", "sae", "harm"]
                        value_patterns = ["nnh", "number needed to harm"]
                    elif metric_type == "RR":
                        metric_kws += ["relative risk", "risk ratio", "rr"]
                        value_patterns = ["relative risk", "risk ratio"]
                    elif metric_type == "OR":
                        metric_kws += ["odds ratio", "or"]
                        value_patterns = ["odds ratio"]
                    elif metric_type == "HR":
                        metric_kws += ["hazard ratio", "hr"]
                        value_patterns = ["hazard ratio"]
                    else:
                        metric_kws += [metric_type.lower()]
                        value_patterns = [metric_type.lower()]

                    outcome_text = outcome.replace("_", " ") if outcome else "clinical outcome"
                    time_text = time_pt.replace("_", " ") if time_pt else ""

                    claim_text = f"{metric_type} for {drug_name}"
                    if outcome:
                        claim_text += f" — outcome: {outcome_text}"
                    if time_pt:
                        claim_text += f" at {time_text}"

                    claims.append(ClaimRequirement(
                        claim_id=f"claim_{claim_idx}",
                        claim_text=claim_text,
                        claim_type="metric",
                        required_entities=[drug_name],
                        required_section=explicit_section,
                        numeric_required=True,
                        metric_required=True,
                        keywords=metric_kws,
                        metric_type=metric_type,
                        metric_outcome=outcome,
                        metric_comparator="placebo",
                        metric_time_point=time_pt,
                        required_value_patterns=value_patterns,
                    ))
                    claim_idx += 1
            return claims

        # 4. Composite Query Decomposition: Count + Percentage
        # E.g.: "how many people globally use tobacco, and what specific percentage live in LMICs?"
        # Arabic: "كام عدد مستخدمي التبغ عالمياً وإيه نسبة اللي عايشين في LMICs؟"
        has_count_query = any(w in q_lower for w in [
            "how many", "number of", "how many people", "كم عدد", "كام عدد", "عدد مستخدمي", "عدد المدخنين", "كم شخص"
        ])
        has_percentage_query = any(w in q_lower for w in [
            "percentage", "percent", "proportion", "what specific percentage", "ما نسبة", "نسبة", "ايه نسبة", "إيه نسبة", "كم نسبة"
        ])

        if has_count_query and has_percentage_query:
            # Claim 1: Global count
            claims.append(ClaimRequirement(
                claim_id="claim_1",
                claim_text="Global tobacco-user count",
                claim_type="numeric",
                required_entities=["global_users"],
                required_section=explicit_section,
                numeric_required=True,
                percentage_required=False,
                keywords=["billion", "million", "tobacco", "globally", "users", "1.25", "8", "عالمياً", "مليار", "مليون"],
            ))
            # Claim 2: Percentage living in LMICs
            claims.append(ClaimRequirement(
                claim_id="claim_2",
                claim_text="Percentage of tobacco users living in LMICs",
                claim_type="percentage",
                required_entities=["lmic"],
                required_section=explicit_section,
                numeric_required=False,
                percentage_required=True,
                keywords=["lmic", "lmics", "percentage", "%", "low- and middle-income", "الدول منخفضة ومتوسطة الدخل", "نسبة"],
            ))
            return claims

        elif has_count_query:
            # Single Count Claim
            claims.append(ClaimRequirement(
                claim_id="claim_1",
                claim_text="Quantitative count/frequency specified in query",
                claim_type="numeric",
                required_entities=["global_users"] if any(g in q_lower for g in self.ENTITY_MAP["global_users"]) else [],
                required_section=explicit_section,
                numeric_required=True,
                percentage_required=False,
                keywords=["number", "count", "عدد", "كم"],
            ))
            return claims

        elif has_percentage_query:
            # Single Percentage Claim
            claims.append(ClaimRequirement(
                claim_id="claim_1",
                claim_text="Percentage/rate statistic specified in query",
                claim_type="percentage",
                required_entities=["lmic"] if any(l in q_lower for l in self.ENTITY_MAP["lmic"]) else [],
                required_section=explicit_section,
                numeric_required=False,
                percentage_required=True,
                keywords=["percentage", "%", "rate", "نسبة"],
            ))
            return claims

        # 4. Clinical Drug Recommendation & Dosing Claims
        drug_entities = []
        for drug in ["varenicline", "bupropion", "cytisine", "nrt", "nrt_patch", "nrt_gum"]:
            patterns = self.ENTITY_MAP.get(drug, [])
            if any(p in q_lower for p in patterns):
                drug_entities.append(drug)

        has_dosing_query = any(w in q_lower for w in [
            "dose", "dosing", "schedule", "duration", "how to take", "titration", "جرعة", "جرعه", "مدة", "تدرج", "طريقة الاستخدام"
        ])
        has_recommendation_query = any(w in q_lower for w in [
            "recommend", "recommendation", "recommended", "efficacy", "effective", "first-line", "توصية", "فعالية", "هل موصى", "علاج"
        ])

        if drug_entities:
            if has_dosing_query and has_recommendation_query:
                # Two claims: Recommendation + Dosing
                claims.append(ClaimRequirement(
                    claim_id="claim_1",
                    claim_text=f"WHO recommendation and efficacy for {', '.join(drug_entities)}",
                    claim_type="recommendation",
                    required_entities=drug_entities,
                    required_section=explicit_section,
                    keywords=drug_entities + ["recommend", "effective", "توصية"],
                ))
                claims.append(ClaimRequirement(
                    claim_id="claim_2",
                    claim_text=f"Dosing schedule and administration protocol for {', '.join(drug_entities)}",
                    claim_type="numeric",
                    required_entities=drug_entities,
                    required_section=explicit_section,
                    numeric_required=True,
                    keywords=drug_entities + ["mg", "day", "weeks", "daily", "جرعة", "ملجم", "أيام", "اسابيع"],
                ))
                return claims
            elif has_dosing_query:
                claims.append(ClaimRequirement(
                    claim_id="claim_1",
                    claim_text=f"Dosing schedule and protocol for {', '.join(drug_entities)}",
                    claim_type="numeric",
                    required_entities=drug_entities,
                    required_section=explicit_section,
                    numeric_required=True,
                    keywords=drug_entities + ["mg", "day", "daily", "جرعة"],
                ))
                return claims
            else:
                claims.append(ClaimRequirement(
                    claim_id="claim_1",
                    claim_text=f"WHO recommendation regarding {', '.join(drug_entities)}",
                    claim_type="recommendation",
                    required_entities=drug_entities,
                    required_section=explicit_section,
                    keywords=drug_entities + ["recommend", "first-line", "توصية"],
                ))
                return claims

        # 5. Brief Advice / Consultation Duration
        if any(w in q_lower for w in ["brief advice", "مشورة موجزة", "نصيحة موجزة", "duration", "take", "time", "دقائق", "ثواني", "وقت"]):
            claims.append(ClaimRequirement(
                claim_id="claim_1",
                claim_text="Definition and duration of brief tobacco cessation advice",
                claim_type="definition",
                required_entities=["brief_advice"],
                required_section=explicit_section,
                numeric_required=True,
                keywords=["brief advice", "30 seconds", "3 minutes", "مشورة موجزة", "ثانية", "دقائق"],
            ))
            return claims

        # 6. Implementation / Policy / Cost
        if any(w in q_lower for w in ["cost", "treatment cost", "reduce", "health systems", "policy", "تكلفة", "تكاليف", "أنظمة صحية", "تأمين"]):
            claims.append(ClaimRequirement(
                claim_id="claim_1",
                claim_text="Health system and policy strategies to reduce tobacco treatment costs in LMICs",
                claim_type="intervention",
                required_entities=["lmic"] if any(l in q_lower for l in self.ENTITY_MAP["lmic"]) else [],
                required_section=explicit_section,
                keywords=["cost", "insurance", "tax", "policy", "lmic", "تكلفة", "تأمين"],
            ))
            return claims

        # 7. Generic Subject Entity Identification (e.g. semaglutide, ozempic, etc.)
        subject_candidates = self._extract_subject_candidates(query)
        claims.append(ClaimRequirement(
            claim_id="claim_1",
            claim_text=f"Clinical guidance for: {query[:80]}",
            claim_type="factual",
            required_entities=subject_candidates,
            required_section=explicit_section,
            keywords=subject_candidates,
            subject_entity=subject_candidates[0] if subject_candidates else None,
        ))
        return claims

    def _evaluate_single_claim(
        self,
        claim: ClaimRequirement,
        admitted_evidence: List[Any],
    ) -> ClaimValidationResult:
        """
        Evaluates whether the admitted evidence chunks provide DIRECT_SUPPORT, PARTIAL_SUPPORT, or UNSUPPORTED for a claim.
        Enforces strict per-chunk section and entity matching.
        """
        if not admitted_evidence:
            return ClaimValidationResult(
                claim_id=claim.claim_id,
                claim_text=claim.claim_text,
                claim_type=claim.claim_type,
                support_level="UNSUPPORTED",
                is_supported=False,
                supporting_chunk_ids=[],
                support_reason="No admitted evidence available in context.",
                matched_entities=[],
                missing_entities=claim.required_entities,
            )

        if claim.claim_type == "out_of_scope":
            return ClaimValidationResult(
                claim_id=claim.claim_id,
                claim_text=claim.claim_text,
                claim_type=claim.claim_type,
                support_level="UNSUPPORTED",
                is_supported=False,
                supporting_chunk_ids=[],
                support_reason="Query targets an unsupported intervention with zero approved clinical evidence in WHO guideline.",
                matched_entities=[],
                missing_entities=claim.required_entities,
            )

        supporting_chunks: List[str] = []
        matched_entities: Set[str] = set()
        missing_entities: Set[str] = set(claim.required_entities)

        for cand in admitted_evidence:
            cid = getattr(cand, "chunk_id", "")
            text = getattr(cand, "text", "")
            text_lower = text.lower()
            sec_title = (getattr(cand, "section_title", "") or "").lower()
            sec_num = (getattr(cand, "section_number", "") or "").lower()
            heading_path = (getattr(cand, "heading_path", "") or "").lower()

            # A. Check if THIS chunk matches the required section
            chunk_matches_section = True
            if claim.required_section:
                sec_target = claim.required_section.lower()
                patterns = self.SECTION_KEYWORDS.get(sec_target, [sec_target])
                chunk_matches_section = any(p in sec_title or p in heading_path or p in cid.lower() for p in patterns)

            # B. Check Entity matches in THIS chunk
            chunk_matched_ents = set()
            for ent in claim.required_entities:
                patterns = self.ENTITY_MAP.get(ent, [ent])
                if any(p in text_lower for p in patterns):
                    chunk_matched_ents.add(ent)
                    matched_entities.add(ent)
                    if ent in missing_entities:
                        missing_entities.remove(ent)

            # C. Check Numeric / Percentage in THIS chunk
            chunk_has_numeric = False
            chunk_has_percentage = False

            numbers_found = re.findall(r"\b\d+[\d,\.]*\b", text_lower)
            percentages_found = re.findall(r"\b\d+[\d\.]*\s*%", text_lower) or re.findall(r"\b\d+[\d\.]*\s*percent", text_lower)

            if numbers_found or any(k in text_lower for k in ["billion", "million", "seconds", "minutes", "weeks", "mg", "مليار", "مليون", "دقائق", "ثانية"]):
                chunk_has_numeric = True

            if percentages_found or any(k in text_lower for k in ["%", "percent", "percentage", "proportion", "proportions", "نسبة"]):
                chunk_has_percentage = True

            # D. Evaluate if THIS chunk directly supports the claim
            # Must satisfy all active constraints for this claim in this specific chunk
            chunk_valid = True

            if claim.required_section and not chunk_matches_section:
                chunk_valid = False

            if claim.required_entities:
                # If entities are required, at least one target entity must be present in THIS chunk
                if not chunk_matched_ents:
                    chunk_valid = False

            if claim.numeric_required and not chunk_has_numeric:
                chunk_valid = False

            if claim.percentage_required and not chunk_has_percentage:
                chunk_valid = False

            # Check keyword relevance
            matched_kws = [kw for kw in claim.keywords if kw.lower() in text_lower]
            if len(matched_kws) == 0 and not chunk_matched_ents:
                chunk_valid = False

            # E. Metric-specific strict value matching (Phase 5)
            # For NNT/NNH/RR/OR claims: chunk must contain the metric keyword AND at least one value pattern
            if claim.metric_required and chunk_valid:
                metric_label_found = claim.metric_type and claim.metric_type.lower() in text_lower
                value_found = any(vp in text_lower for vp in claim.required_value_patterns) if claim.required_value_patterns else False
                if not (metric_label_found or value_found):
                    # Metric label or value pattern must be present
                    chunk_valid = False

            if chunk_valid:
                supporting_chunks.append(cid)

        # Determine Final Support Level
        # Case A: Missing critical entities across all admitted chunks
        if claim.required_entities and len(missing_entities) > 0:
            return ClaimValidationResult(
                claim_id=claim.claim_id,
                claim_text=claim.claim_text,
                claim_type=claim.claim_type,
                support_level="UNSUPPORTED",
                is_supported=False,
                supporting_chunk_ids=[],
                support_reason=f"Admitted evidence lacks required clinical entities: {list(missing_entities)}.",
                matched_entities=list(matched_entities),
                missing_entities=list(missing_entities),
                citations=[],
                primary_citation=None,
                primary_citation_tag=None,
            )

        # Case B: Direct Support Verified in one or more chunks
        if supporting_chunks:
            # Build ClaimEvidenceCitation objects for supporting chunks, ranked by relevance and section match
            supporting_cands = [c for c in admitted_evidence if getattr(c, "chunk_id", "") in supporting_chunks]
            
            def score_supporting_cand(cand) -> float:
                s = getattr(cand, "clinical_score", 0.0)
                sec_t = (getattr(cand, "section_title", "") or "").lower()
                cid_c = getattr(cand, "chunk_id", "").lower()
                if claim.required_section and any(p in sec_t or p in cid_c for p in self.SECTION_KEYWORDS.get(claim.required_section.lower(), [])):
                    s += 10.0
                return s

            supporting_cands.sort(key=score_supporting_cand, reverse=True)
            built_citations: List[ClaimEvidenceCitation] = []

            for cand in supporting_cands:
                cit = ClaimEvidenceCitation(
                    claim_id=claim.claim_id,
                    chunk_id=getattr(cand, "chunk_id", ""),
                    section_number=getattr(cand, "section_number", None),
                    section_title=getattr(cand, "section_title", None),
                    heading_path=getattr(cand, "heading_path", None),
                    physical_page_start=getattr(cand, "physical_page_start", None),
                    source_name="WHO",
                    evidence_text=getattr(cand, "text", ""),
                    support_level="DIRECT_SUPPORT",
                    relevance_score=getattr(cand, "clinical_score", 0.0),
                )
                built_citations.append(cit)

            primary_cit = built_citations[0] if built_citations else None
            primary_tag = primary_cit.to_citation_string() if primary_cit else None

            return ClaimValidationResult(
                claim_id=claim.claim_id,
                claim_text=claim.claim_text,
                claim_type=claim.claim_type,
                support_level="DIRECT_SUPPORT",
                is_supported=True,
                supporting_chunk_ids=supporting_chunks[:3],
                support_reason=f"Fully supported by {len(supporting_chunks)} admitted evidence chunk(s) satisfying all constraints ({', '.join(supporting_chunks[:2])}).",
                matched_entities=list(matched_entities),
                missing_entities=[],
                citations=built_citations,
                primary_citation=primary_cit,
                primary_citation_tag=primary_tag,
            )

        # Case C: Constraints failed (e.g. section mismatch, percentage missing, or metric value not found)
        if claim.claim_type == "metric":
            metric_label = claim.metric_type or "metric"
            drug_label = ", ".join(claim.required_entities) if claim.required_entities else "drug"
            return ClaimValidationResult(
                claim_id=claim.claim_id,
                claim_text=claim.claim_text,
                claim_type=claim.claim_type,
                support_level="UNSUPPORTED",
                is_supported=False,
                supporting_chunk_ids=[],
                support_reason=f"No admitted evidence chunk explicitly contains {metric_label} value for {drug_label}. "
                               f"Generic efficacy evidence about the drug does NOT satisfy a specific {metric_label} claim. "
                               f"Value patterns searched: {claim.required_value_patterns}",
                matched_entities=list(matched_entities),
                missing_entities=list(missing_entities),
                citations=[],
                primary_citation=None,
                primary_citation_tag=None,
            )

        if claim.required_section:
            return ClaimValidationResult(
                claim_id=claim.claim_id,
                claim_text=claim.claim_text,
                claim_type=claim.claim_type,
                support_level="UNSUPPORTED",
                is_supported=False,
                supporting_chunk_ids=[],
                support_reason=f"Requested section '{claim.required_section}' in WHO guideline does not contain the required statistic/information.",
                matched_entities=list(matched_entities),
                missing_entities=list(missing_entities),
                citations=[],
                primary_citation=None,
                primary_citation_tag=None,
            )

        return ClaimValidationResult(
            claim_id=claim.claim_id,
            claim_text=claim.claim_text,
            claim_type=claim.claim_type,
            support_level="UNSUPPORTED",
            is_supported=False,
            supporting_chunk_ids=[],
            support_reason="No admitted evidence chunk directly affirms this requirement with all necessary constraints.",
            matched_entities=list(matched_entities),
            missing_entities=list(missing_entities),
            citations=[],
            primary_citation=None,
            primary_citation_tag=None,
        )

    def validate_query(
        self,
        query: str,
        admitted_evidence: List[Any],
        safety_flag: Optional[str] = None,
        parsed_query: Optional[ClinicalQueryRepresentation] = None,
    ) -> ClaimCoverageReport:
        """
        Main entry point: Validates all extracted claims for a query against admitted evidence chunks.
        """
        # 1. Out-of-Scope / Negative Control Guard (Only if no admitted evidence exists or no valid clinical interventions)
        if (safety_flag == "NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE" or (parsed_query and parsed_query.is_out_of_scope and not parsed_query.detected_interventions)) and not admitted_evidence:
            extracted = self.extract_claims(query, parsed_query)
            evaluated = [
                ClaimValidationResult(
                    claim_id=c.claim_id,
                    claim_text=c.claim_text,
                    claim_type=c.claim_type,
                    support_level="UNSUPPORTED",
                    is_supported=False,
                    supporting_chunk_ids=[],
                    support_reason="Negative control / out-of-scope query has no grounded evidence in WHO guideline.",
                    matched_entities=[],
                    missing_entities=c.required_entities,
                    citations=[],
                    primary_citation=None,
                    primary_citation_tag=None,
                )
                for c in extracted
            ]
            return ClaimCoverageReport(
                raw_query=query,
                total_required_claims=len(extracted),
                supported_claims_count=0,
                partially_supported_claims_count=0,
                unsupported_claims_count=len(extracted),
                claim_coverage_ratio=0.0,
                grounding_decision="NO_GROUNDED_EVIDENCE",
                claims=evaluated,
                overall_reason="Query asks for unsupported intervention (e.g. unapproved medication/method) without WHO evidence.",
                citations=[],
                primary_citation_tags=[],
            )

        # 2. Extract Claims
        claims = self.extract_claims(query, parsed_query)
        total_claims = len(claims)

        # 3. Evaluate Each Claim
        evaluated_claims: List[ClaimValidationResult] = []
        direct_count = 0
        partial_count = 0
        unsupported_count = 0
        all_citations: List[ClaimEvidenceCitation] = []
        primary_tags: List[str] = []

        for claim in claims:
            res = self._evaluate_single_claim(claim, admitted_evidence)
            evaluated_claims.append(res)
            if res.support_level == "DIRECT_SUPPORT":
                direct_count += 1
            elif res.support_level == "PARTIAL_SUPPORT":
                partial_count += 1
            else:
                unsupported_count += 1

            if res.citations:
                all_citations.extend(res.citations)
            if res.primary_citation_tag and res.primary_citation_tag not in primary_tags:
                primary_tags.append(res.primary_citation_tag)

        # 4. Calculate True Claim Coverage Ratio
        # Direct support counts as 1.0, Partial support counts as 0.5
        coverage_score = (direct_count * 1.0) + (partial_count * 0.5)
        coverage_ratio = round(coverage_score / total_claims, 2) if total_claims > 0 else 0.0

        # 5. Determine Overall Grounding Decision
        if coverage_ratio >= 1.0:
            decision = "FULLY_GROUNDED"
            reason = f"All {total_claims} required question claims are directly supported by admitted evidence."
        elif coverage_score > 0.0:
            decision = "PARTIALLY_GROUNDED"
            reason = f"{direct_count + partial_count} of {total_claims} claims supported. Some required information is missing in guideline evidence."
        else:
            decision = "NO_GROUNDED_EVIDENCE"
            reason = "Zero required claims are supported by admitted evidence."

        return ClaimCoverageReport(
            raw_query=query,
            total_required_claims=total_claims,
            supported_claims_count=direct_count,
            partially_supported_claims_count=partial_count,
            unsupported_claims_count=unsupported_count,
            claim_coverage_ratio=coverage_ratio,
            grounding_decision=decision,
            claims=evaluated_claims,
            overall_reason=reason,
            citations=all_citations,
            primary_citation_tags=primary_tags,
        )
