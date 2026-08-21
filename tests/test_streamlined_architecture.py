"""
Unit and Integration Tests — Streamlined Architecture (Single Medical RAG + System Prompt)
Medical RAG Project: Oxygen (أوكسجين)
Source Document: WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

from llm_generation_pipeline import GenerationPipeline
from llm_generator import LLMGenerator, MockLLMProvider
from simplification_verifier import SimplificationVerifier


class TestStreamlinedArchitecture(unittest.TestCase):
    """Tests the refactored architecture with internalized communication principles."""

    def setUp(self):
        self.mock_provider = MockLLMProvider()
        self.generator = LLMGenerator(provider=self.mock_provider)
        self.pipeline = GenerationPipeline(llm_generator=self.generator)

    def test_system_prompt_contains_explanation_policy(self):
        """Verifies that the System Prompt has key clinical and communication policies."""
        prompt_text = self.generator.system_prompt
        self.assertIn("سالم", prompt_text)
        self.assertIn("WHO", prompt_text)
        self.assertIn("Identity & Mission", prompt_text)
        self.assertIn("Evidence Application Rule", prompt_text)
        self.assertIn("Communication Style", prompt_text)

    def test_no_dynamic_rule_injection_in_user_prompt(self):
        """Verifies that build_user_prompt does NOT inject CDC/dynamic rule blocks."""
        user_prompt = self.generator.build_user_prompt(
            query="هل دواء الفارينيكلين آمن؟",
            context="Varenicline is recommended with high certainty.",
            citations_metadata=[{"source_id": 1, "section_number": "3.3.1", "physical_page_start": 45, "title": "Varenicline", "chunk_id": "chunk_01"}],
        )
        self.assertIn("=== RETRIEVED WHO GUIDELINE EVIDENCE (VERBATIM) ===", user_prompt)
        self.assertIn("=== AVAILABLE CITATIONS METADATA ===", user_prompt)
        self.assertNotIn("=== SIMPLIFICATION & COMMUNICATION GUIDANCE", user_prompt)
        self.assertNotIn("RULE-ACT", user_prompt)
        self.assertNotIn("RULE-SAFE", user_prompt)

    def test_end_to_end_grounded_medical_query(self):
        """Verifies successful end-to-end execution of a valid clinical query."""
        res = self.pipeline.process("ما هي الجرعة الموصى بها لدواء فارينيكلين؟")
        self.assertIn("answer", res)
        self.assertTrue(res["grounded"])
        self.assertGreater(len(res["citations"]), 0)

    def test_negative_control_unsupported_query(self):
        """Verifies that unsupported queries trigger safety flags and clear lack-of-evidence responses."""
        res = self.pipeline.process("هل العلاج بالليزر معتمد في دليل منظمة الصحة العالمية؟")
        self.assertIn("answer", res)
        self.assertFalse(res.get("grounded", True))
        self.assertIn(res.get("contract_state", ""), ["ABSTAIN", "UNSUPPORTED", "OUT_OF_SCOPE"])

    def test_verifier_catches_false_certainty(self):
        """Verifies that the verifier flags answers that claim 100% cure on probabilistic evidence."""
        verifier = SimplificationVerifier()
        bad_answer = "دواء الفارينيكلين علاج مؤكد 100% ويضمن الشفاء التام بدون أي شك."
        evidence = "Varenicline may increase cessation rates (conditional recommendation)."
        res = verifier.verify(bad_answer, evidence, "هل الدواء مضمون؟")
        self.assertFalse(res.is_valid)
        self.assertIn("UNCERTAINTY_UPGRADED_TO_CERTAINTY", res.failed_checks)

    def test_verifier_verifies_dosage_integrity(self):
        """Verifies that verifier checks numbers and dosages."""
        verifier = SimplificationVerifier()
        good_answer = "تناول فارينيكلين بجرعة 0.5 مجم ثم 1 مجم مرتين يومياً."
        evidence = "Varenicline 0.5 mg daily titrated to 1 mg twice daily."
        res = verifier.verify(good_answer, evidence, "ما هي الجرعة؟")
        self.assertTrue(res.is_valid)
        self.assertIn("DOSAGE_ENTITIES_CHECKED", res.passed_checks)


if __name__ == "__main__":
    unittest.main()
