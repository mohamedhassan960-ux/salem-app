# PHASE 0 AUDIT REPORT — Salem Medical RAG System
**Audit Date**: 2026-08-22
**Project**: أوكسجين (Oxygen) — WHO Tobacco Cessation Guideline (2024) Clinical RAG
**Role**: Senior AI/RAG Architect + MLOps Engineer

---

## 1. Current Architecture Overview
The system implements a multi-stage, evidence-grounded, safety-first clinical RAG architecture:
```
User Query (Arabic / Egyptian / English)
       │
       ▼
1. Clinical Query Understanding (query_understanding.py)
       │
       ├─────────────────────────┬─────────────────────────┐
       ▼                         ▼                         ▼
   BM25 Sparse             Dense Vector (ONNX)       Clinical Dimensions
 (bm25_retriever.py)      (dense_retriever.py)
       │                         │                         │
       └─────────────────────────┼─────────────────────────┘
                                 ▼
2. Reciprocal Rank Fusion (RRF k=60) (hybrid_retriever.py)
                                 ▼
3. Multi-Aspect Clinical Reranker (reranker.py)
                                 ▼
4. Evidence Quality Gate (evidence_quality_gate.py)
                                 ▼
5. Claim-Level Coverage Validator (claim_validator.py)
                                 ▼
6. Grounded Answer Contract (Circuit Breaker) (grounded_answer_contract.py)
         │
         ├─── [NO EVIDENCE / OUT OF SCOPE / ABSTAIN] ──► Deterministic Response (0 LLM Calls)
         │
         └─── [SUPPORTED / PARTIALLY SUPPORTED]
                     │
                     ▼
7. Context Assembler & Provenance (context_assembler.py)
                     │
                     ▼
8. LLM Generator (Gemini / Provider Agnostic) (llm_generator.py)
                     │
                     ▼
9. Simplification & Dosage Verifier (simplification_verifier.py)
                     │
                     ▼
             Final Clinical Answer + Citations
```

---

## 2. Current Embedding Flow
- **Model**: `intfloat/multilingual-e5-small`
- **Inference Runtime**: Local ONNX Runtime via `onnxruntime` + HuggingFace `transformers` AutoTokenizer.
- **Model Weights Storage**: Local file `outputs/onnx_model/model.onnx` (~448 MB) + tokenizer in `data/models/multilingual-e5-small/`.
- **Dimension**: 384 float32 values.
- **Prefixes**: Asymmetric query/passage prefixes (`query: ` / `passage: `).
- **Normalization**: L2 unit normalization.
- **Vector Search**: Dot-product cosine similarity over L2-normalized numpy matrix.

---

## 3. Current Generation Flow
- **Provider**: Google Gemini REST API via `GenerativeLanguage API` (`v1beta`).
- **Configured Models**: `gemini-2.5-flash`, `gemini-2.5-flash-lite`, fallback `gemini-3.5-flash-lite`.
- **Security & Provenance**: Strict delimiter fencing, explicit citation metadata injection (`[WHO — Section X.X — Page Y]`), system prompt enforcing 14 medical communication & simplification rules.
- **Circuit Breaker Integration**: If Grounded Answer Contract determines `is_generation_allowed == False`, LLM generation is completely bypassed (0 API calls).

---

## 4. Current Index Format
- **Dense Vectors**: `outputs/dense_index_v2.npz`
  - Array `vectors`: `(171, 384)` dtype `float32`
  - Array `chunk_ids`: 171 chunk identifiers
- **Dense Metadata**: `outputs/dense_metadata_v2.json`
  - Records: `model_name: "intfloat/multilingual-e5-small"`, `embedding_dimension: 384`, `corpus_size: 171`, `use_e5_prefixes: true`.
- **Knowledge Source**: `outputs/retrieval_records_v2.json` containing 171 verbatim chunks extracted from WHO 2024 guideline.

---

## 5. Current Deployment Blockers (Free-Tier Hosting)
1. **Local Model Weight Size**: `outputs/onnx_model/model.onnx` is 448 MB. Including tokenizer and base dependencies balloons Docker image to ~2 GB.
2. **Heavy Python Dependencies**: `onnxruntime`, `transformers`, `torch` require extensive compilation layers and ~800+ MB RAM at runtime. Free-tier web services (e.g., Render Free 512MB RAM, Koyeb, Hugging Face Spaces) trigger Out-Of-Memory (OOM) kills or fail build size constraints.
3. **Localhost Dependency**: Without a lightweight, cloud-embedding architecture, backend cannot boot reliably under 512 MB RAM limits.

---

## 6. Files That Must NOT Be Modified (Protected RAG Core)
- `scripts/bm25_retriever.py` (BM25 sparse search logic)
- `scripts/reranker.py` (Clinical reranking logic)
- `scripts/evidence_quality_gate.py` (Quality gate thresholds and safety flags)
- `scripts/claim_validator.py` (Claim-level grounding rules)
- `scripts/grounded_answer_contract.py` (Salem Contract circuit breaker logic)
- `scripts/simplification_verifier.py` (Dosage, numbers, and uncertainty verification)
- `scripts/context_assembler.py` (Token budget and context formatting)
- `prompts/clinical_assistant_system.txt` (WHO medical rules & Egyptian Arabic policy)
- `outputs/dense_index_v2.npz` (Old index — frozen rollback baseline)
- `outputs/dense_metadata_v2.json` (Old metadata — frozen rollback baseline)

---

## 7. Files That May Need Modification
- `scripts/dense_retriever.py` (Add CloudEmbeddingProvider abstraction while preserving local ONNX/PyTorch for rollback)
- `scripts/hybrid_retriever.py` (Enable loading cloud dense index v3 by default with automatic fallback)
- `scripts/llm_generation_pipeline.py` (Default to cloud index v3 while respecting environment variables)
- `requirements.txt` (Make production dependencies lightweight: remove mandatory onnxruntime/transformers)
- `Dockerfile` (Optimize container image for fast boot and <150 MB size)
- `.env.example` (Document embedding provider variables)

---

## 8. Rollback Strategy
If cloud embeddings fail validation or show degraded retrieval metrics:
1. The rollback index `outputs/dense_index_v2.npz` is preserved 100% untouched.
2. Switching `EMBEDDING_PROVIDER=onnx` or `EMBEDDING_PROVIDER=local` immediately restores the original 384d ONNX/PyTorch pipeline without code rewrites.
