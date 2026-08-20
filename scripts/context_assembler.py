"""
Context Assembler — Medical RAG Project: Oxygen (أوكسجين)

Converts ranked Retrieval results into a structured, token-budgeted Context
ready to be injected into an LLM prompt.

Design principles:
- Verbatim medical text: zero modification, zero summarisation, zero paraphrasing.
- Token-safe: context never exceeds max_context_tokens (tiktoken cl100k_base).
- Chunk-safe: a chunk is either included in full or excluded entirely; never split mid-text.
- Provenance-preserved: every source carries full citation metadata.
- Document-Agnostic: no hardcoded WHO section names or document structure.
- LLM-ready: includes a grounding instruction block to constrain the downstream LLM.
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import tiktoken


# ─────────────────────────────────────────────────────────────────────────────
# Data types
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SourceReference:
    """Provenance metadata attached to each included chunk."""
    source_id: int                  # 1-based position in context
    chunk_id: str
    node_id: str
    parent_id: str
    title: str
    section_number: str
    physical_page_start: Optional[int]
    physical_page_end: Optional[int]
    content_type: str
    chunk_index: int
    distance: float


@dataclass
class AssembledContext:
    """Full output of the Context Assembler."""
    query: str
    context: str                          # The verbatim text block for the LLM
    sources: List[SourceReference]        # Provenance for included chunks
    included_chunks: List[str]            # chunk_ids included
    excluded_chunks: List[str]            # chunk_ids excluded (budget overflow)
    context_token_count: int              # Verified token count


# ─────────────────────────────────────────────────────────────────────────────
# Grounding instruction (prepended to every context)
# ─────────────────────────────────────────────────────────────────────────────

GROUNDING_INSTRUCTION = (
    "INSTRUCTIONS FOR THE AI ASSISTANT:\n"
    "Answer using ONLY the information provided in the retrieved sources below.\n"
    "Do NOT use any external knowledge, assumptions, or information not present "
    "in the sources.\n"
    "Do NOT modify, rephrase, or reinterpret dosages, statistics, risk ratios, "
    "confidence intervals, or clinical recommendations.\n"
    "If the sources do not contain enough information to answer the question, "
    "state clearly: 'The available sources do not provide enough information "
    "to answer this question.'\n"
    "Always cite the source number (e.g. [SOURCE 1]) when referring to evidence.\n"
)


# ─────────────────────────────────────────────────────────────────────────────
# Context Assembler
# ─────────────────────────────────────────────────────────────────────────────

class ContextAssembler:
    """
    Assembles ranked retrieval results into a token-budgeted LLM context.

    Parameters
    ----------
    max_context_tokens : int
        Hard token ceiling for the assembled context (default 3000).
    tokenizer_name : str
        tiktoken encoding name (default 'cl100k_base').
    """

    DEFAULT_MAX_CONTEXT_TOKENS = 3_000
    DEFAULT_TOKENIZER = "cl100k_base"

    def __init__(
        self,
        max_context_tokens: int = DEFAULT_MAX_CONTEXT_TOKENS,
        tokenizer_name: str = DEFAULT_TOKENIZER,
    ):
        if not isinstance(max_context_tokens, int) or max_context_tokens < 100:
            raise ValueError(
                f"max_context_tokens must be an integer >= 100 (got {max_context_tokens!r})."
            )
        self.max_context_tokens = max_context_tokens
        self._enc = tiktoken.get_encoding(tokenizer_name)

        # Pre-compute token cost of the grounding instruction (constant per instance)
        self._grounding_token_count = len(self._enc.encode(GROUNDING_INSTRUCTION))

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def assemble(
        self,
        query: str,
        retrieval_results: List[Dict[str, Any]],
        max_context_tokens: Optional[int] = None,
    ) -> AssembledContext:
        """
        Build a structured, token-safe context from retrieval results.

        Parameters
        ----------
        query : str
            The original user query (English or Arabic).
        retrieval_results : list
            Output of RetrievalPipeline.retrieve() — list of result dicts,
            assumed pre-sorted by distance ascending (most relevant first).
        max_context_tokens : int, optional
            Override the instance-level budget for this call.

        Returns
        -------
        AssembledContext
        """
        # --- Validate inputs ---
        if not query or not query.strip():
            raise ValueError("query must be a non-empty string.")

        if retrieval_results is None:
            raise ValueError("retrieval_results must be a list, not None.")

        budget = max_context_tokens if max_context_tokens is not None else self.max_context_tokens
        if not isinstance(budget, int) or budget < 100:
            raise ValueError(
                f"max_context_tokens must be an integer >= 100 (got {budget!r})."
            )

        if not retrieval_results:
            # Return an empty-but-valid context rather than crashing
            return AssembledContext(
                query=query,
                context=GROUNDING_INSTRUCTION + "\n[No relevant sources were retrieved.]\n",
                sources=[],
                included_chunks=[],
                excluded_chunks=[],
                context_token_count=self._grounding_token_count + 5,
            )

        # --- Sort by distance ascending (most relevant first) ---
        sorted_results = sorted(retrieval_results, key=lambda r: r.get("distance", 1.0))

        # --- Build source blocks within token budget ---
        source_blocks: List[str] = []
        sources: List[SourceReference] = []
        included_ids: List[str] = []
        excluded_ids: List[str] = []

        # Budget accounting: start with grounding instruction tokens
        tokens_used = self._grounding_token_count

        for result in sorted_results:
            chunk_id = result.get("chunk_id", "")
            text = result.get("text", "")

            # Skip chunks with empty text
            if not text or not text.strip():
                excluded_ids.append(chunk_id)
                continue

            source_num = len(included_ids) + 1
            block = self._format_source_block(source_num, result)
            block_tokens = len(self._enc.encode(block))

            # Chunk-safe: include the chunk in full or exclude entirely
            if tokens_used + block_tokens > budget:
                excluded_ids.append(chunk_id)
                continue

            source_blocks.append(block)
            tokens_used += block_tokens
            included_ids.append(chunk_id)

            sources.append(SourceReference(
                source_id=source_num,
                chunk_id=chunk_id,
                node_id=result.get("node_id", ""),
                parent_id=result.get("parent_id", ""),
                title=result.get("section_title", ""),
                section_number=result.get("section_number", "") or "",
                physical_page_start=result.get("physical_page_start"),
                physical_page_end=result.get("physical_page_end"),
                content_type=result.get("content_type", ""),
                chunk_index=result.get("chunk_index", 0),
                distance=result.get("distance", 1.0),
            ))

        # --- Assemble final context string ---
        query_header = f"QUESTION:\n{query.strip()}\n\n"
        sources_section = "\n".join(source_blocks)
        full_context = (
            GROUNDING_INSTRUCTION
            + "\n"
            + query_header
            + "RETRIEVED SOURCES:\n\n"
            + (sources_section if source_blocks else "[No sources fit within the token budget.]\n")
        )

        # Verify final token count
        final_token_count = len(self._enc.encode(full_context))

        return AssembledContext(
            query=query,
            context=full_context,
            sources=sources,
            included_chunks=included_ids,
            excluded_chunks=excluded_ids,
            context_token_count=final_token_count,
        )

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _format_source_block(self, source_num: int, result: Dict[str, Any]) -> str:
        """Renders one retrieval result as a verbatim context block."""
        title = result.get("section_title") or "—"
        section = result.get("section_number") or "—"
        page_start = result.get("physical_page_start")
        page_end = result.get("physical_page_end")
        pages = f"P{page_start}–P{page_end}" if page_start is not None else "—"
        content_type = result.get("content_type") or "—"
        distance = result.get("distance", 1.0)
        text = result.get("text", "").strip()

        return (
            f"[SOURCE {source_num}]\n"
            f"Title: {title}\n"
            f"Section: {section}\n"
            f"Pages: {pages}\n"
            f"Content Type: {content_type}\n"
            f"Relevance Distance: {distance:.4f}\n\n"
            f"Text:\n{text}\n\n"
            f"{'─' * 60}\n\n"
        )

    def count_tokens(self, text: str) -> int:
        """Returns the token count for any text string using the configured tokenizer."""
        return len(self._enc.encode(text))
