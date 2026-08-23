"""
LLM Generator Layer — Medical RAG Project: Oxygen (أوكسجين)
Provider-Agnostic LLM Client & Response Generator

Design Principles:
- Provider Agnostic: Supports Mock, OpenAI-compatible (LM Studio, vLLM, OpenAI, Groq), Gemini, and Anthropic.
- Zero Hardcoded Secrets: Reads API keys and endpoints strictly from environment variables.
- Resilient & Safe: Graceful fallback on API timeouts or network errors.
- Medical Grounding & Provenance: Injects assembled verbatim WHO context with explicit citation metadata.
- Prompt Injection Defense: Context chunks are isolated in strict delimiter blocks.
"""

from __future__ import annotations

import os
import sys
import json
import time
import re
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Union

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Auto-load .env file from project root if available
def _load_env_file() -> None:
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip().strip("\"'")
                    if k and k not in os.environ:
                        os.environ[k] = v

_load_env_file()

DEFAULT_SYSTEM_PROMPT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "prompts",
    "clinical_assistant_system.txt"
)


@dataclass
class CitationItem:
    """Provenance metadata for an evidence citation."""
    source_id: int
    section_number: str
    physical_page_start: Optional[int]
    title: str
    chunk_id: str

    def to_citation_tag(self) -> str:
        sec = f"Section {self.section_number}" if self.section_number else self.title
        page = f"Page {self.physical_page_start}" if self.physical_page_start is not None else ""
        parts = [p for p in ["WHO", sec, page] if p]
        return f"[{' — '.join(parts)}]"


@dataclass
class LLMGenerationResponse:
    """Structured response returned by the LLM Generator."""
    answer: str
    citations: List[Dict[str, Any]]
    grounded: bool
    safety_status: str
    provider: str
    model: str
    raw_response: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LLMProvider(ABC):
    """Abstract interface for LLM inference providers."""

    @abstractmethod
    def complete(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 600,
    ) -> str:
        """Sends a completion request and returns the raw response string."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        pass


class MockLLMProvider(LLMProvider):
    """
    Deterministic mock provider for unit testing and offline development.
    Produces medically faithful, empathetic Egyptian-Arabic responses without external API calls.
    """

    def __init__(self, model_name: str = "mock-clinical-v1", canned_responses: Optional[Dict[str, str]] = None):
        self._model_name = model_name
        self._canned_responses = canned_responses or {}
        self.call_history: List[Dict[str, Any]] = []

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def model_name(self) -> str:
        return self._model_name

    def complete(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 600,
    ) -> str:
        self.call_history.append({
            "system_prompt": system_prompt,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        })

        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_msg = m.get("content", "")
                break

        # Check canned responses
        for k, v in self._canned_responses.items():
            if k.lower() in last_user_msg.lower():
                return v

        # 1. Negative Control / Out of Scope Check
        if "[STATUS: NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE]" in last_user_msg:
            return (
                "أهلاً بحضرتك. وفقاً لدليل منظمة الصحة العالمية للعلاج السريري للإقلاع عن التبغ (2024)، "
                "لا توجد أدلة سريرية معتمدة أو توصية رسمية تدعم استخدام هذا الإجراء كوسيلة معتمدة للإقلاع عن التدخين. "
                "[WHO — Section 3.6 — Page 62]"
            )

        # 2. Emotional / Off-Topic / Personal Situation
        if any(w in last_user_msg for w in ["متخانق", "مراتي", "الجو حر", "امتحان", "مضغوط", "الشغل", "تعبان"]):
            return (
                "ألف سلامة عليك، ومقدّر جداً الضغط والتوتر اللي بتمر بيه. "
                "المواقف دي طبيعي تزوّد الرغبة في التدخين، بس خليك واثق إننا نقدر نعديها خطوة خطوة بهدوء بدون ما نرجع للسيجارة."
            )

        # 3. English Query Check
        if "varenicline" in last_user_msg.lower() or "efficacy" in last_user_msg.lower() or "what is" in last_user_msg.lower():
            return (
                "Based on the WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024), "
                "varenicline is recommended as an effective first-line pharmacological treatment with high certainty evidence. "
                "[WHO — Section 3.3.1 — Page 45]"
            )

        # 4. Standard Medical Evidence Synthesis (Egyptian Arabic)
        if "فارينيكلين" in last_user_msg or "دوا" in last_user_msg or "أدوية" in last_user_msg or "تبطل" in last_user_msg:
            return (
                "بناءً على توصيات منظمة الصحة العالمية (2024)، يعتبر دواء فارينيكلين من العلاجات الدوائية الفعالة "
                "للخط الأول للإقلاع عن التدخين بأدلة علمية عالية اليقين. "
                "[WHO — Section 3.3.1 — Page 45]\n"
                "وينصح باستشارة الطبيب لتحديد الجرعة المناسبة لحالتك."
            )

        return (
            "وفقاً للأدلة الإكلينيكية لمنظمة الصحة العالمية (2024)، يتوفر دعم سلوكي وعلاجات دوائية معتمدة "
            "تساعد في تخفيف أعراض الانسحاب وتحقيق الإقلاع التام. [WHO — Section 3.1 — Page 20]"
        )


class OpenAICompatibleProvider(LLMProvider):
    """
    OpenAI-compatible client (works with LM Studio, vLLM, OpenAI, Groq, Ollama, DeepSeek).
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout_seconds: int = 120,
    ):
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL") or "http://localhost:1234/v1").rstrip("/")
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("LLM_API_KEY") or "lm-studio"
        self._model_name = model_name or os.environ.get("LLM_MODEL") or "google/gemma-4-e4b"
        # Read timeout from environment variable if present, else use passed parameter/default
        env_timeout = os.environ.get("LLM_TIMEOUT_SECONDS")
        if env_timeout and env_timeout.isdigit():
            self.timeout = int(env_timeout)
        else:
            self.timeout = timeout_seconds

    @property
    def provider_name(self) -> str:
        return "openai_compatible"

    @property
    def model_name(self) -> str:
        return self._model_name

    def complete(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 600,
    ) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        full_messages = [{"role": "system", "content": system_prompt}] + messages

        payload = {
            "model": self._model_name,
            "messages": full_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                msg = data["choices"][0]["message"]
                content   = msg.get("content", "") or ""
                reasoning = msg.get("reasoning_content", "") or ""

                # Primary: use content field if non-empty (most models)
                if content.strip():
                    return content.strip()

                # Fallback for thinking-only models (Gemma-4, Qwen3 reasoning variants):
                # reasoning_content may contain the full thinking + answer as one block.
                # Try to extract text after </think> or after thinking process header.
                if reasoning.strip():
                    # Strip common thinking-block wrappers
                    cleaned = reasoning
                    for tag in ["</think>", "</thinking>", "</Thinking>"]:
                        if tag in cleaned:
                            cleaned = cleaned.split(tag, 1)[-1]
                            break
                    # If no tag found, skip lines that look like thinking process headers
                    else:
                        lines = cleaned.split("\n")
                        skip_patterns = ["thinking process", "بالتفكير", "let me think", "analysis:", "step 1", "step1"]
                        start_idx = 0
                        for j, line in enumerate(lines):
                            if any(p in line.lower() for p in skip_patterns):
                                start_idx = j + 1
                        cleaned = "\n".join(lines[start_idx:])
                    return cleaned.strip()

                return ""
            else:
                error_msg = f"HTTP {resp.status_code}: {resp.text}"
                logging.error(f"OpenAICompatibleProvider Error: {error_msg}")
                raise RuntimeError(error_msg)
        except Exception as e:
            logging.error(f"OpenAICompatibleProvider request failed: {e}")
            raise


class GeminiProvider(LLMProvider):
    """
    Google Gemini API Provider.
    API key is read exclusively from GEMINI_API_KEY or GOOGLE_API_KEY environment variables.
    No key is hardcoded in this file.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = (
            api_key
            or os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
            or os.environ.get("LLM_API_KEY")
        )
        # Prefer GEMINI_MODEL env var, fall back to gemini-3.6-flash
        self._model_name = (
            model_name
            or os.environ.get("GEMINI_MODEL")
            or os.environ.get("LLM_MODEL")
            or "gemini-3.6-flash"
        )

    @property
    def provider_name(self) -> str:
        return "google_gemini"

    @property
    def model_name(self) -> str:
        return self._model_name

    def complete(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 2048,
    ) -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set. Set it as an environment variable.")

        # Key is passed only in the URL query param (Gemini REST API standard). Never logged.
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self._model_name}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}

        # Build contents from messages — only user/assistant turns (no full history)
        contents = []
        for m in messages:
            role = "user" if m["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m["content"]}]})

        # Ensure ample token headroom for reasoning/thinking tokens + full clinical response
        effective_max_tokens = max(max_tokens, 2048)

        payload = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": effective_max_tokens,
            },
        }

        for attempt in range(5):
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=35)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if not candidates:
                        return ""
                    parts = candidates[0].get("content", {}).get("parts", [])
                    # Exclude thought/reasoning scratchpad parts to avoid leaking internal reasoning
                    text_parts = [
                        p.get("text", "")
                        for p in parts
                        if isinstance(p, dict) and "text" in p and not p.get("thought", False)
                    ]
                    if not text_parts:
                        text_parts = [p.get("text", "") for p in parts if isinstance(p, dict) and "text" in p]
                    # Log token usage (safe — no secrets)
                    usage = data.get("usageMetadata", {})
                    if usage:
                        logging.info(
                            "[GeminiProvider] tokens: input=%s output=%s total=%s",
                            usage.get("promptTokenCount", "?"),
                            usage.get("candidatesTokenCount", "?"),
                            usage.get("totalTokenCount", "?"),
                        )
                    return "".join(text_parts).strip()
                elif resp.status_code == 404:
                    # Model retirement fallback by Google
                    fallback_models = ["gemini-3.6-flash", "gemini-flash-latest", "gemini-2.5-flash"]
                    next_model = None
                    for fm in fallback_models:
                        if fm != self._model_name:
                            next_model = fm
                            break
                    if next_model and attempt < 3:
                        logging.warning(f"Gemini model {self._model_name} returned 404. Trying fallback model {next_model}.")
                        self._model_name = next_model
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self._model_name}:generateContent?key={self.api_key}"
                        continue
                    else:
                        raise RuntimeError(f"Gemini API Error 404: {resp.text}")
                elif resp.status_code in [429, 503, 500, 502]:
                    if attempt >= 2:
                        raise RuntimeError(f"Gemini API rate limit / server busy ({resp.status_code}): {resp.text[:200]}")
                    wait_time = min(2.0, 1.0 * (attempt + 1))
                    logging.warning(f"Gemini {resp.status_code} (attempt {attempt+1}/3). Quick wait {wait_time:.1f}s...")
                    time.sleep(wait_time)
                else:
                    raise RuntimeError(f"Gemini API Error {resp.status_code}: {resp.text[:300]}")
            except requests.exceptions.RequestException as e:
                if attempt == 4:
                    raise
                logging.warning(f"Gemini request exception: {e}. Retrying in 5s...")
                time.sleep(5)
        raise RuntimeError("Gemini API call failed after 5 retries due to persistent rate limiting or server demand.")


class GroqProvider(OpenAICompatibleProvider):
    """Groq Cloud API Provider (OpenAI-compatible)."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None, timeout_seconds: int = 45):
        groq_api_key = api_key or os.environ.get("GROQ_API_KEY") or os.environ.get("LLM_API_KEY")
        groq_model = model_name or os.environ.get("GROQ_MODEL") or os.environ.get("LLM_MODEL") or "openai/gpt-oss-120b"
        super().__init__(
            base_url="https://api.groq.com/openai/v1",
            api_key=groq_api_key,
            model_name=groq_model,
            timeout_seconds=timeout_seconds,
        )

    @property
    def provider_name(self) -> str:
        return "groq"


class NvidiaNimProvider(OpenAICompatibleProvider):
    """NVIDIA NIM Hosted Inference Provider (OpenAI-compatible)."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None, timeout_seconds: int = 300):
        nvidia_api_key = api_key or os.environ.get("NVIDIA_API_KEY") or os.environ.get("LLM_API_KEY")
        nvidia_model = model_name or os.environ.get("NVIDIA_MODEL") or os.environ.get("LLM_MODEL") or "openai/gpt-oss-120b"
        super().__init__(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=nvidia_api_key,
            model_name=nvidia_model,
            timeout_seconds=timeout_seconds,
        )

    @property
    def provider_name(self) -> str:
        return "nvidia"


class LLMGenerator:
    """
    Main LLM Generator Layer.
    Translates retrieved WHO evidence into empathetic, culturally natural Egyptian-Arabic clinical answers.
    """

    def __init__(
        self,
        provider: Optional[LLMProvider] = None,
        system_prompt_path: str = DEFAULT_SYSTEM_PROMPT_PATH,
    ):
        self.provider = provider or self._auto_detect_provider()
        self.system_prompt = self._load_system_prompt(system_prompt_path)

    def _auto_detect_provider(self) -> LLMProvider:
        """Auto-detects configured LLM provider from environment variables."""
        p_name = os.environ.get("LLM_PROVIDER", "").lower()
        if p_name == "mock":
            return MockLLMProvider()
        elif p_name == "nvidia" or p_name == "nim":
            return NvidiaNimProvider()
        elif p_name == "groq":
            return GroqProvider()
        elif p_name == "gemini":
            return GeminiProvider()
        elif p_name == "openai" or p_name == "openai_compatible":
            return OpenAICompatibleProvider()
        # Default Provider: Gemini if configured, otherwise Nvidia if key exists, otherwise Gemini
        if os.environ.get("NVIDIA_API_KEY") and not os.environ.get("GEMINI_API_KEY"):
            return NvidiaNimProvider()
        return GeminiProvider()

    def _load_system_prompt(self, path: str) -> str:
        """Loads clinical assistant system prompt from disk."""
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
        logging.warning(f"System prompt file not found at {path}. Using default inline prompt.")
        return (
            "أنت طبيب ومرشد سلوكي للإقلاع عن التدخين بمشروع أوكسجين. "
            "تحدث بالعامية المصرية الدافئة، واستند حصرياً لأدلة منظمة الصحة العالمية 2024 المرفقة."
        )

    def build_user_prompt(
        self,
        query: str,
        context: str,
        citations_metadata: Optional[List[Dict[str, Any]]] = None,
        safety_flag: Optional[str] = None,
        is_grounded: bool = True,
        contract_state: Optional[str] = None,
        unsupported_claims: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Builds a secure, injection-shielded, contract-state-aware prompt for the LLM."""
        prompt_parts: List[str] = []

        # 1. Contract State (Phase 5 explicit declaration)
        effective_state = contract_state or ("GROUNDED_EVIDENCE_AVAILABLE" if is_grounded else "INSUFFICIENT_EVIDENCE")
        if safety_flag:
            prompt_parts.append(f"[STATUS: {safety_flag}]")
        prompt_parts.append(f"[CONTRACT STATE: {effective_state}]")

        # 2. Retrieved WHO Evidence Block (Fenced to prevent prompt injection)
        prompt_parts.append("\n=== RETRIEVED WHO GUIDELINE EVIDENCE (VERBATIM) ===")
        if context and context.strip():
            prompt_parts.append(context.strip())
        else:
            prompt_parts.append("NO RETRIEVED EVIDENCE AVAILABLE FOR THIS QUERY.")
        prompt_parts.append("=== END OF RETRIEVED EVIDENCE ===\n")

        # 3. Available Citations Metadata
        if citations_metadata:
            prompt_parts.append("=== AVAILABLE CITATIONS METADATA ===")
            for item in citations_metadata:
                sec = item.get("section_number") or item.get("title") or "WHO"
                page = f"Page {item.get('physical_page_start')}" if item.get("physical_page_start") is not None else ""
                prompt_parts.append(f"- Source {item.get('source_id')}: [WHO — Section {sec} — {page}] (Chunk: {item.get('chunk_id')})")
            prompt_parts.append("=== END CITATIONS METADATA ===\n")

        # 4. Partial-support explicit constraints
        if contract_state == "PARTIALLY_SUPPORTED" and unsupported_claims:
            prompt_parts.append("=== UNSUPPORTED CLAIM CONSTRAINTS ===")
            prompt_parts.append(
                "The following claim(s) from the patient's question are NOT supported by the retrieved evidence. "
                "You MUST explicitly state that the evidence does not establish these items. "
                "Do NOT infer, guess, or derive their answers from context or pretrained knowledge:"
            )
            for uc in unsupported_claims:
                prompt_parts.append(f"  - {uc.get('claim_text', str(uc))}")
            prompt_parts.append("=== END UNSUPPORTED CLAIM CONSTRAINTS ===\n")

        # 5. User Query
        prompt_parts.append(f"PATIENT MESSAGE: {query}")

        # 6. Task instructions — strengthen for contract compliance
        if contract_state in {"SUPPORTED", "PARTIALLY_SUPPORTED"}:
            prompt_parts.append(
                "\nTASK: Provide a warm, natural, empathetic clinical response strictly grounded in the retrieved evidence above.\n"
                "RULES (strictly enforced):\n"
                "- Apply the Answer-First principle: answer the patient's actual question directly in your opening sentence.\n"
                "- Select and apply ONLY the retrieved evidence directly relevant to the patient's current situation, question, and cessation stage. Do NOT attempt to use all retrieved chunks, and do NOT mention an evidence chunk merely because it appears above.\n"
                "- Do NOT force medication or cessation initiation details on a patient seeking behavioral craving support or maintenance.\n"
                "- Every substantive medical claim must be supported by the retrieved evidence and cited using [WHO — Section X.X] or [WHO — Section X.X — Page Y] ONLY if that section/page exists in AVAILABLE CITATIONS METADATA.\n"
                "- Do NOT fabricate section numbers or page numbers.\n"
                "- Do NOT transform contextual or background text into a WHO recommendation.\n"
                "- Do NOT infer a recommendation from the mere mention of an intervention in the evidence.\n"
                "- If the patient describes acute red-flag symptoms (chest pain, severe dyspnea, suicide risk), safety overrides all normal RAG behavior: direct immediately to emergency services.\n"
                "- If a specific clinical detail (e.g. dosage, NNT) is genuinely requested by the patient but absent from the evidence, state briefly: 'المعلومة دي مش متوفرة عندي بشكل موثوق دلوقتي.' without long epistemic disclaimers.\n"
            )
        else:
            prompt_parts.append(
                "\nTASK: Provide a warm, natural, empathetic response to the patient following the Answer-First principle.\n"
                "- For medical facts or advice, use ONLY relevant supporting evidence above and cite using [WHO — Section X.X — Page Y].\n"
                "- If off-topic or personal, acknowledge and support empathetically without forcing tobacco discussions.\n"
                "- Do NOT invent ungrounded medical facts.\n"
            )

        return "\n".join(prompt_parts)

    def generate(
        self,
        query: str,
        context: str,
        citations_metadata: Optional[List[Dict[str, Any]]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        safety_flag: Optional[str] = None,
        is_grounded: bool = True,
        temperature: float = 0.0,
        contract_state: Optional[str] = None,
        unsupported_claims: Optional[List[Dict[str, Any]]] = None,
    ) -> LLMGenerationResponse:
        """Generates a complete, structured clinical response with Phase 5 contract-state awareness."""
        user_prompt = self.build_user_prompt(
            query=query,
            context=context,
            citations_metadata=citations_metadata,
            safety_flag=safety_flag,
            is_grounded=is_grounded,
            contract_state=contract_state,
            unsupported_claims=unsupported_claims,
        )

        messages: List[Dict[str, str]] = []
        if conversation_history:
            for turn in conversation_history:
                if turn.get("role") in {"user", "assistant"} and turn.get("content"):
                    messages.append({"role": turn["role"], "content": turn["content"]})

        messages.append({"role": "user", "content": user_prompt})

        try:
            raw_text = self.provider.complete(
                system_prompt=self.system_prompt,
                messages=messages,
                temperature=temperature,
                max_tokens=2048,
            )

            citations = citations_metadata or []

            return LLMGenerationResponse(
                answer=raw_text,
                citations=citations,
                grounded=is_grounded and (safety_flag != "NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE"),
                safety_status=safety_flag or ("DIRECT_EVIDENCE" if is_grounded else "INSUFFICIENT_EVIDENCE"),
                provider=self.provider.provider_name,
                model=self.provider.model_name,
                raw_response=raw_text,
                error=None,
            )
        except Exception as e:
            logging.error(f"LLM Generation with {self.provider.provider_name} failed: {e}. Trying Gemini fallback...")
            # Automatic fallback to Gemini if primary provider (e.g. Groq/Nvidia) failed or hit 429
            if self.provider.provider_name != "google_gemini" and os.environ.get("GEMINI_API_KEY"):
                try:
                    fallback_provider = GeminiProvider()
                    raw_text = fallback_provider.complete(
                        system_prompt=self.system_prompt,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=2048,
                    )
                    return LLMGenerationResponse(
                        answer=raw_text,
                        citations=citations_metadata or [],
                        grounded=is_grounded and (safety_flag != "NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE"),
                        safety_status=safety_flag or ("DIRECT_EVIDENCE" if is_grounded else "INSUFFICIENT_EVIDENCE"),
                        provider="google_gemini_fallback",
                        model=fallback_provider.model_name,
                        raw_response=raw_text,
                        error=None,
                    )
                except Exception as fb_err:
                    logging.error(f"Fallback Gemini Provider also failed: {fb_err}")

            fallback_ans = (
                "أهلاً بحضرتك. وفقاً للأدلة الإكلينيكية لمنظمة الصحة العالمية (2024)، "
                "يتوفر دعم سلوكي وعلاجات معتمدة لمساعدتك في رحلة الإقلاع. "
                "نعتذر عن حدوث تعذر فني مؤقت في معالجة الرد الكامل."
            )
            return LLMGenerationResponse(
                answer=fallback_ans,
                citations=citations_metadata or [],
                grounded=is_grounded,
                safety_status=safety_flag or "TECHNICAL_ERROR",
                provider=self.provider.provider_name,
                model=self.provider.model_name,
                raw_response=None,
                error=str(e),
            )
