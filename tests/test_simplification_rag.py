"""
Unit and Integration Tests for Simplification RAG Architecture
Oxygen Medical RAG Project — Tobacco Cessation
"""

import os
import sys
import unittest
from typing import Dict, List, Any

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

from simplification_query import SimplificationQueryBuilder, SimplificationQuery
from simplification_retriever import SimplificationRetriever, retrieve_simplification_guidance
from simplification_verifier import SimplificationVerifier, VerificationResult
from simplification_pipeline import SimplificationIntegratedPipeline
from llm_generator import LLMGenerator, MockLLMProvider


class TestSimplificationQueryBuilder(unittest.TestCase):
    """Tests feature detection and query extraction from medical evidence."""

    def setUp(self):
        self.builder = SimplificationQueryBuilder()

    def test_detect_uncertainty_and_hedging(self):
        ev = "Varenicline may increase the likelihood of smoking cessation, but evidence shows conditional outcomes."
        q = self.builder.build_query(medical_evidence=ev, user_query="هل الفارينيكلين مضمون؟")
        self.assertTrue(q.has_uncertainty_or_hedging)
        self.assertIn("UNCERTAINTY_PRESERVATION", q.detected_features)
        self.assertIn("Uncertainty", q.target_categories)

    def test_detect_dosage_and_medication(self):
        ev = "Administer Metformin 500 mg orally BID with meals to improve glycemic control."
        q = self.builder.build_query(medical_evidence=ev, user_query="جرعة الميتفورمين كام؟")
        self.assertTrue(q.has_medication)
        self.assertTrue(q.has_dosage_or_units)
        self.assertIn("DOSAGE_AND_UNIT_INTEGRITY", q.detected_features)
        self.assertIn("Dosage integrity", q.target_categories)

    def test_detect_numbers_and_percentages(self):
        ev = "The trial reported a 33% relative risk reduction with event rates dropping from 3% to 2%."
        q = self.builder.build_query(medical_evidence=ev)
        self.assertTrue(q.has_numbers_or_percentages)
        self.assertIn("NUMERICAL_FRAMING_NATURAL_FREQUENCIES", q.detected_features)

    def test_detect_contraindications_and_warnings(self):
        ev = "Isotretinoin is strictly contraindicated in pregnancy due to severe teratogenic risks."
        q = self.builder.build_query(medical_evidence=ev)
        self.assertTrue(q.has_contraindication_or_warning)
        self.assertIn("CONTRAINDICATIONS_AND_WARNINGS", q.detected_features)

    def test_detect_behavioral_instructions(self):
        ev = "Patient should establish a quit date, wash hands prior to use, and follow split-dose preparation."
        q = self.builder.build_query(medical_evidence=ev, user_query="إزاي استعمل الدوا؟")
        self.assertTrue(q.has_behavioral_instructions)
        self.assertIn("BEHAVIORAL_ACTION_STEPS", q.detected_features)


class TestSimplificationRetriever(unittest.TestCase):
    """Tests rule retrieval, scoring, and source provenance retention."""

    def setUp(self):
        self.retriever = SimplificationRetriever()
        self.builder = SimplificationQueryBuilder()

    def test_retriever_loads_rules(self):
        self.assertGreater(len(self.retriever.rules), 0)
        self.assertIn("SOURCE-001", self.retriever.sources)
        self.assertIn("SOURCE-002", self.retriever.sources)
        self.assertIn("SYSTEM", self.retriever.sources)

    def test_retrieve_for_medication_and_dosage(self):
        ev = "Varenicline 1 mg twice daily should be titrated gradually."
        q = self.builder.build_query(medical_evidence=ev)
        res = self.retriever.retrieve(q, top_k=5)

        self.assertGreater(len(res.rules), 0)
        rule_ids = [r.rule_id for r in res.rules]
        # Must include dosage integrity safety rule
        self.assertIn("RULE-SAFE-002", rule_ids)

    def test_retrieve_for_uncertainty(self):
        ev = "Preliminary observational data suggest a possible inverse association."
        q = self.builder.build_query(medical_evidence=ev)
        res = self.retriever.retrieve(q, top_k=5)

        rule_ids = [r.rule_id for r in res.rules]
        self.assertIn("RULE-SAFE-001", rule_ids)

    def test_medical_fact_firewall_in_retrieved_output(self):
        """Simplification guidance must contain ONLY communication instructions, no clinical facts."""
        ev = "Bupropion is recommended for tobacco cessation."
        q = self.builder.build_query(medical_evidence=ev)
        res = self.retriever.retrieve(q, top_k=5)
        formatted_prompt = res.format_for_llm()

        self.assertIn("=== SIMPLIFICATION & COMMUNICATION GUIDANCE", formatted_prompt)
        self.assertIn("DO NOT TREAT THESE RULES AS SOURCES OF MEDICAL FACTS", formatted_prompt)
        # Check that no clinical treatment recommendation is declared in the guidance itself
        self.assertNotIn("prescribe 150 mg bupropion", formatted_prompt.lower())


class TestSimplificationVerifier(unittest.TestCase):
    """Tests post-generation clinical meaning preservation and safety verification."""

    def setUp(self):
        self.verifier = SimplificationVerifier()

    def test_verify_valid_explanation(self):
        ev = "Varenicline may increase cessation success."
        ans = "بناءً على توصيات منظمة الصحة العالمية (2024)، دواء الفارينيكلين ممكن يساعد في زيادة فرص الإقلاع عن التدخين. [WHO — Section 3.3.1 — Page 45]"
        res = self.verifier.verify(generated_answer=ans, medical_evidence=ev, user_query="هل الدوا ده مفيد؟")

        self.assertTrue(res.is_valid)
        self.assertEqual(res.safety_status, "VERIFIED_SAFE")

    def test_verifier_catches_overconfidence(self):
        ev = "Varenicline may help people quit smoking."
        ans = "الفارينيكلين علاج سحري ويضمن الشفاء التام ويقضي تماماً على الرغبة في التدخين بدون أي شك."
        res = self.verifier.verify(generated_answer=ans, medical_evidence=ev, user_query="هل الدوا بيعالج؟")

        self.assertFalse(res.is_valid)
        self.assertIn("UNCERTAINTY_UPGRADED_TO_CERTAINTY", res.failed_checks)

    def test_verifier_catches_simplification_source_as_medical_fact(self):
        ev = "Varenicline is recommended."
        ans = "وفقاً لدليل Everyday Words للكلمات اليومية، الفارينيكلين يعالج إدمان النيكوتين."
        res = self.verifier.verify(generated_answer=ans, medical_evidence=ev, user_query="مين قال كدة؟")

        self.assertFalse(res.is_valid)
        self.assertIn("SIMPLIFICATION_SOURCE_CITED_AS_MEDICAL_EVIDENCE", res.failed_checks)

    def test_verifier_negative_control_enforcement(self):
        ev = ""
        ans = "العلاج بالليزر أو الوخز بالإبر غير موصى به وفقاً لدليل منظمة الصحة العالمية 2024 لعدم وجود أدلة سريرية كافية. [WHO — Section 3.6 — Page 62]"
        res = self.verifier.verify(
            generated_answer=ans,
            medical_evidence=ev,
            user_query="الليزر بيبطل تدخين؟",
            safety_flag="NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE",
        )
        self.assertTrue(res.is_valid)
        self.assertIn("NEGATIVE_CONTROL_UPHELD", res.passed_checks)


class TestDualRAGPipelineIntegration(unittest.TestCase):
    """End-to-End integration tests for Dual-RAG architecture.

    NOTE (Phase 1 Architecture):
    Simplification RAG was intentionally removed from the production runtime.
    Its communication/explanation principles are now embedded in the System Prompt.
    These tests validate the current production behaviour:
    - simplification_rag["enabled"] == False (feature removed from runtime)
    - Gate safety_flag is now correctly surfaced as the final safety_status
      (Phase 3 fix: gate rejections are no longer silently overridden by the verifier)
    """

    def setUp(self):
        mock_provider = MockLLMProvider()
        generator = LLMGenerator(provider=mock_provider)
        self.pipeline = SimplificationIntegratedPipeline(llm_generator=generator)

    def test_pipeline_end_to_end_medication_query(self):
        query = "هل دواء الفارينيكلين بيساعد في الإقلاع عن السجاير؟"
        res = self.pipeline.process(query)

        self.assertIn("answer", res)
        self.assertTrue(res["grounded"])
        self.assertEqual(res["safety_status"], "VERIFIED_SAFE")
        # Simplification RAG was removed from production in Phase 1 (rules merged into System Prompt)
        self.assertFalse(res["simplification_rag"]["enabled"])
        self.assertIn("citations", res)

    def test_pipeline_negative_control_handling(self):
        query = "هل السجائر الإلكترونية معتمدة كعلاج رسمي للإقلاع من منظمة الصحة العالمية؟"
        res = self.pipeline.process(query)

        self.assertIn("answer", res)
        # Phase 3 fix: Gate's NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE now takes priority
        # over the verifier's VERIFIED_SAFE, so the final safety_status is truthful.
        self.assertEqual(res["safety_status"], "NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE")
        self.assertFalse(res["grounded"])
        has_negative_indicator = any(term in res["answer"] for term in ["لا توجد", "مش لاقي", "أدلة", "دليل", "توصية", "غير معتمد", "غير موصى"])
        self.assertTrue(has_negative_indicator)



if __name__ == "__main__":
    unittest.main()
