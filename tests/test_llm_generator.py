"""
Automated Unit Tests — LLM Generator Layer
Medical RAG Project: Oxygen (أوكسجين)
Source Document: WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)

Verifies:
Test 1: MockLLMProvider deterministic instantiation and completion
Test 2: LLMGenerator initialization and system prompt loading
Test 3: Prompt building with safe injection shielding delimiter tags
Test 4: Citation metadata structure and string rendering
Test 5: Handling of Negative Control / Out-of-Scope flags
Test 6: Handling of Insufficient Evidence flags
Test 7: Multi-turn conversation history integration
Test 8: Graceful fallback on provider runtime error
Test 9: Provider auto-detection logic
Test 10: Structure and type integrity of LLMGenerationResponse
"""

import os
import sys
import logging

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
from llm_generator import (
    LLMGenerator,
    MockLLMProvider,
    LLMGenerationResponse,
    CitationItem,
    LLMProvider,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class FailingProvider(LLMProvider):
    """Mock provider that always raises an error to test resilience."""
    @property
    def provider_name(self) -> str:
        return "failing_mock"
    @property
    def model_name(self) -> str:
        return "failing-model-v1"
    def complete(self, system_prompt: str, messages: list, temperature: float = 0.0, max_tokens: int = 600) -> str:
        raise ConnectionError("Simulated upstream network timeout")


def run_tests():
    print("=" * 70)
    print("LLM GENERATOR LAYER UNIT TEST SUITE")
    print("=" * 70)

    failures = []
    test_count = 0

    def record_test(name: str, passed: bool, detail: str = ""):
        nonlocal test_count
        test_count += 1
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} Test {test_count}: {name} {f'({detail})' if detail else ''}")
        if not passed:
            failures.append(f"Test {test_count} ({name}): {detail}")

    # Test 1: MockLLMProvider instantiation and completion
    mock = MockLLMProvider()
    res = mock.complete("System prompt", [{"role": "user", "content": "Hello"}])
    record_test(
        "MockLLMProvider Instantiation & Completion",
        isinstance(res, str) and len(res) > 10,
        f"response length={len(res)}"
    )

    # Test 2: LLMGenerator system prompt loading
    gen = LLMGenerator(provider=mock)
    record_test(
        "LLMGenerator System Prompt Loading",
        bool(gen.system_prompt) and "منظمة الصحة العالمية" in gen.system_prompt,
        f"prompt length={len(gen.system_prompt)}"
    )

    # Test 3: Prompt building with safe injection shielding delimiters
    prompt = gen.build_user_prompt(
        query="What is varenicline?",
        context="WHO evidence text here",
        safety_flag=None,
        is_grounded=True,
    )
    has_fences = "=== RETRIEVED WHO GUIDELINE EVIDENCE (VERBATIM) ===" in prompt and "=== END OF RETRIEVED EVIDENCE ===" in prompt
    record_test(
        "Prompt Building & Injection Delimiter Fencing",
        has_fences,
        "evidence is strictly isolated in delimiter blocks"
    )

    # Test 4: Citation metadata structure and string rendering
    cite = CitationItem(
        source_id=1,
        section_number="3.3.1",
        physical_page_start=45,
        title="Varenicline for Tobacco Cessation",
        chunk_id="chunk_node_L3_3_3_1_varenicline_001"
    )
    cite_tag = cite.to_citation_tag()
    record_test(
        "CitationItem Formatting",
        cite_tag == "[WHO — Section 3.3.1 — Page 45]",
        f"rendered: {cite_tag}"
    )

    # Test 5: Handling of Negative Control / Out-of-Scope flags
    resp_neg = gen.generate(
        query="Is acupuncture effective?",
        context="",
        safety_flag="NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE",
        is_grounded=False,
    )
    record_test(
        "Negative Control Flag Handling",
        resp_neg.grounded is False and resp_neg.safety_status == "NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE",
        f"safety_status={resp_neg.safety_status}, grounded={resp_neg.grounded}"
    )

    # Test 6: Handling of Insufficient Evidence flags
    resp_insuf = gen.generate(
        query="Some vague question",
        context="",
        safety_flag="INSUFFICIENT_EVIDENCE",
        is_grounded=False,
    )
    record_test(
        "Insufficient Evidence Flag Handling",
        resp_insuf.grounded is False and resp_insuf.safety_status == "INSUFFICIENT_EVIDENCE",
        f"safety_status={resp_insuf.safety_status}"
    )

    # Test 7: Multi-turn conversation history integration
    history = [
        {"role": "user", "content": "أنا عايز أبطل تدخين"},
        {"role": "assistant", "content": "خطوة ممتازة يا فندم. معاك خطوة بخطوة."},
    ]
    resp_hist = gen.generate(
        query="ايه الأدوية المتاحة؟",
        context="Varenicline and Bupropion evidence",
        conversation_history=history,
        is_grounded=True,
    )
    record_test(
        "Conversation History Support",
        isinstance(resp_hist, LLMGenerationResponse) and len(mock.call_history[-1]["messages"]) == 3,
        f"messages count in prompt={len(mock.call_history[-1]['messages'])}"
    )

    # Test 8: Graceful fallback on provider runtime error
    failing_gen = LLMGenerator(provider=FailingProvider())
    resp_fail = failing_gen.generate(
        query="فارينيكلين",
        context="Some context",
        is_grounded=True,
    )
    record_test(
        "Graceful Fallback on Upstream Failure",
        bool(resp_fail.error) and len(resp_fail.answer) > 20,
        f"fallback answer delivered, error captured: {resp_fail.error}"
    )

    # Test 9: Provider auto-detection fallback
    auto_gen = LLMGenerator()
    record_test(
        "Provider Auto-Detection Fallback",
        auto_gen.provider is not None,
        f"provider={auto_gen.provider.provider_name}"
    )

    # Test 10: Structure and type integrity of LLMGenerationResponse
    resp_dict = resp_neg.to_dict()
    record_test(
        "LLMGenerationResponse Schema Integrity",
        isinstance(resp_dict, dict) and "answer" in resp_dict and "citations" in resp_dict and "grounded" in resp_dict,
        f"keys={list(resp_dict.keys())}"
    )

    print("=" * 70)
    if failures:
        print(f"FAILED {len(failures)}/{test_count} tests:")
        for f in failures:
            print(f"  - {f}")
        return False
    else:
        print(f"ALL {test_count} TESTS PASSED SUCCESSFULLY! (100% PASS)")
        print("=" * 70)
        return True


if __name__ == "__main__":
    success = run_tests()
    if not success:
        sys.exit(1)
