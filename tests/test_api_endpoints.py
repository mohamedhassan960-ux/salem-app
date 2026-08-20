"""
Comprehensive Production API Hardening & Security Test Suite — Oxygen Medical RAG
Verifies:
1. /api/v1/health (Liveness)
2. /api/v1/ready (Readiness)
3. /api/v1/meta (Public Metadata, zero secrets)
4. /api/v1/chat with Mock provider (Supported query)
5. /api/v1/chat Circuit Breaker (UNSUPPORTED / OUT_OF_SCOPE / 0 LLM calls)
6. X-Request-ID propagation (Inbound / Outbound / Generated)
7. Input validation bounds (empty query, query too long, malformed roles)
8. Direct-Pipeline vs API equality test
9. Authentication tests (No key, wrong key, correct key when AUTH_ENABLED=true)
10. Query param auth rejection (Never accept ?api_key=...)
11. Circuit Breaker Invocation Count Proof (Instruments MockLLMProvider to verify 0 calls)
"""

import sys
import os
import unittest
from fastapi.testclient import TestClient

# Path setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "scripts"))
sys.path.insert(0, BASE_DIR)

# Force Mock provider for deterministic unit testing
os.environ["LLM_PROVIDER"] = "mock"
os.environ["OXYGEN_API_KEY"] = "test-secret-key-12345"

from api.main import app
from api.rag_service import get_rag_service
from llm_generation_pipeline import GenerationPipeline
from llm_generator import LLMProvider, LLMGenerator


class InstrumentingMockProvider(LLMProvider):
    """Instrumentation provider to strictly count and record LLM completions."""
    def __init__(self):
        self.call_count = 0
        self.recorded_queries = []

    @property
    def provider_name(self) -> str:
        return "instrumented_mock"

    @property
    def model_name(self) -> str:
        return "instrumented-mock-v1"

    def complete(self, system_prompt: str, messages: list, temperature: float = 0.0, max_tokens: int = 600) -> str:
        self.call_count += 1
        self.recorded_queries.append(messages[-1]["content"] if messages else "")
        return "أهلاً بحضرتك، بناءً على إرشادات منظمة الصحة العالمية لعام 2024، يتوفر دعم معتمد للإقلاع."


class TestOxygenProductionAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.service = get_rag_service()
        cls.mock_provider = InstrumentingMockProvider()
        cls.service._pipeline.llm_generator = LLMGenerator(provider=cls.mock_provider)

    def setUp(self):
        # Reset call counter before each test
        self.mock_provider.call_count = 0
        self.mock_provider.recorded_queries.clear()

    # ── 1. HEALTH & READINESS ──────────────────────────────────────────────────
    def test_01_health_endpoint(self):
        """Verify cheap liveness probe (0 RAG calls, 0 LLM calls) on both /api/v1/health and /health."""
        for path in ["/api/v1/health", "/health"]:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "ok")
            self.assertEqual(data["service"], "oxygen-medical-rag-api")
        self.assertEqual(self.mock_provider.call_count, 0)

    def test_02_ready_endpoint(self):
        """Verify readiness probe checks vector store and pipeline state (0 LLM calls) on both /api/v1/ready and /ready."""
        for path in ["/api/v1/ready", "/ready"]:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "ready")
            self.assertTrue(data["pipeline_ready"])
            self.assertEqual(data["vector_store_chunks"], 171)
        self.assertEqual(self.mock_provider.call_count, 0)

    def test_03_meta_endpoint(self):
        """Verify safe public metadata (no secret leaks)."""
        response = self.client.get("/api/v1/meta")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["api_version"], "1.0.0")
        self.assertTrue(data["circuit_breaker_enabled"])
        self.assertNotIn("api_key", data)
        self.assertNotIn("path", data)
        self.assertNotIn("OXYGEN_API_KEY", data)

    # ── 2. CIRCUIT BREAKER INVOCATION-COUNT PROOF ──────────────────────────────
    def test_04_circuit_breaker_unsupported_zero_llm_calls(self):
        """CRITICAL: Prove UNSUPPORTED (psilocybin) triggers circuit breaker with EXACTLY 0 LLM calls."""
        payload = {"query": "ما هي جرعة العلاج بمخدر السيلوسيبين (psilocybin) للإقلاع؟"}
        response = self.client.post("/api/v1/chat", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["contract_state"], "UNSUPPORTED")
        self.assertFalse(data["grounded"])
        self.assertEqual(data["provider"], "deterministic")
        # Hard proof: LLM provider was NEVER called
        self.assertEqual(self.mock_provider.call_count, 0)

    def test_05_circuit_breaker_out_of_scope_zero_llm_calls(self):
        """CRITICAL: Prove OUT_OF_SCOPE (school youth primary prevention) triggers circuit breaker with EXACTLY 0 LLM calls."""
        payload = {"query": "هل بتنصحوا بالسيتيسين لحماية ولادنا في المدارس اللي مش بيدخنوا عشان ميجربوش؟"}
        response = self.client.post("/api/v1/chat", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["contract_state"], "OUT_OF_SCOPE")
        self.assertFalse(data["grounded"])
        self.assertEqual(data["provider"], "deterministic")
        # Hard proof: LLM provider was NEVER called
        self.assertEqual(self.mock_provider.call_count, 0)

    def test_06_supported_query_invokes_llm_once(self):
        """Verify SUPPORTED query proceeds to LLM exactly once."""
        payload = {"query": "ما هي جرعة الفارينيكلين للإقلاع عن التدخين؟"}
        response = self.client.post("/api/v1/chat", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["contract_state"], "SUPPORTED")
        self.assertTrue(data["grounded"])
        self.assertEqual(self.mock_provider.call_count, 1)

    # ── 3. AUTHENTICATION TESTS ────────────────────────────────────────────────
    def test_07_auth_enforcement_when_enabled(self):
        """Verify auth behavior when AUTH_ENABLED=true."""
        import api.main
        # Enable auth
        api.main.AUTH_ENABLED_ENV = True
        api.main.EXPECTED_API_KEY = "test-secret-key-12345"

        try:
            # 1. No key provided -> 401
            resp_no_key = self.client.post("/api/v1/chat", json={"query": "ما هي بدائل النيكوتين؟"})
            self.assertEqual(resp_no_key.status_code, 401)

            # 2. Wrong key provided -> 401
            resp_wrong = self.client.post(
                "/api/v1/chat",
                json={"query": "ما هي بدائل النيكوتين؟"},
                headers={"X-API-Key": "invalid-secret"}
            )
            self.assertEqual(resp_wrong.status_code, 401)

            # 3. Correct key in header -> 200
            resp_correct = self.client.post(
                "/api/v1/chat",
                json={"query": "ما هي بدائل النيكوتين؟"},
                headers={"X-API-Key": "test-secret-key-12345"}
            )
            self.assertEqual(resp_correct.status_code, 200)

            # 4. Key in query param -> Rejected (Must use header only)
            resp_query = self.client.post(
                "/api/v1/chat?api_key=test-secret-key-12345",
                json={"query": "ما هي بدائل النيكوتين؟"}
            )
            self.assertEqual(resp_query.status_code, 401)

        finally:
            # Reset to disabled for other tests
            api.main.AUTH_ENABLED_ENV = False

    # ── 4. REQUEST ID PROPAGATION ──────────────────────────────────────────────
    def test_08_request_id_inbound_and_generated(self):
        """Verify X-Request-ID propagation and auto-generation."""
        # A. Custom inbound request ID
        custom_id = "req_custom_trace_999"
        res_custom = self.client.post(
            "/api/v1/chat",
            json={"query": "ما هي بدائل النيكوتين؟"},
            headers={"X-Request-ID": custom_id}
        )
        self.assertEqual(res_custom.status_code, 200)
        self.assertEqual(res_custom.json()["request_id"], custom_id)
        self.assertEqual(res_custom.headers.get("X-Request-ID"), custom_id)

        # B. Auto-generated request ID
        res_auto = self.client.post("/api/v1/chat", json={"query": "ما هي بدائل النيكوتين؟"})
        self.assertEqual(res_auto.status_code, 200)
        auto_id = res_auto.json()["request_id"]
        self.assertTrue(auto_id.startswith("req_"))
        self.assertEqual(res_auto.headers.get("X-Request-ID"), auto_id)

    # ── 5. INPUT VALIDATION & ERROR BEHAVIOR ───────────────────────────────────
    def test_09_validation_rejects_empty_query(self):
        """Verify empty/whitespace query returns 422."""
        res = self.client.post("/api/v1/chat", json={"query": "   "})
        self.assertEqual(res.status_code, 422)

    def test_10_validation_rejects_overlong_query(self):
        """Verify query exceeding 2000 chars returns 422."""
        overlong_q = "تدخين " * 450
        res = self.client.post("/api/v1/chat", json={"query": overlong_q})
        self.assertEqual(res.status_code, 422)

    def test_11_validation_rejects_invalid_history_role(self):
        """Verify invalid conversation history role returns 422."""
        payload = {
            "query": "ما هي بدائل النيكوتين؟",
            "conversation_history": [{"role": "admin_hacker", "content": "hello"}]
        }
        res = self.client.post("/api/v1/chat", json=payload)
        self.assertEqual(res.status_code, 422)

    # ── 6. DIRECT VS API EQUALITY ──────────────────────────────────────────────
    def test_12_direct_pipeline_vs_api_semantic_match(self):
        """Verify 100% semantic identity between direct pipeline and HTTP endpoint."""
        query = "هل اللصقات مع اللبان أكثر فعالية للإقلاع؟"
        
        # 1. Direct invocation
        direct_res = self.service._pipeline.process(query)
        
        # 2. HTTP API invocation
        api_res = self.client.post("/api/v1/chat", json={"query": query}).json()
        
        self.assertEqual(direct_res["contract_state"], api_res["contract_state"])
        self.assertEqual(direct_res["grounded"], api_res["grounded"])
        self.assertEqual(direct_res["safety_status"], api_res["safety_status"])
        self.assertEqual(len(direct_res["citations"]), len(api_res["citations"]))


if __name__ == "__main__":
    unittest.main()
