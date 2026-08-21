# DEPLOYMENT BLOCKER AUDIT & ROOT CAUSE ANALYSIS
**Audit Date**: 2026-08-22
**Role**: Senior AI/RAG Architect + MLOps Engineer + Cloud Deployment Engineer

---

## 1. Root Cause Analysis of Previous Deployment Failures

| Previous Blocker | Technical Cause | Consequence in Production |
| :--- | :--- | :--- |
| **1. 448 MB ONNX Model Weight** | `outputs/onnx_model/model.onnx` was bundled directly into the container image. | Container image size exceeded 1.5–2.0 GB, causing slug size exhaustion, slow image transfer, and deployment build timeouts. |
| **2. Heavy Runtimes (`onnxruntime`, `transformers`, `tokenizers`)** | Required by local ONNX tokenizer and C++ execution engine. | Memory footprint exceeded 700–850 MB RAM at runtime, triggering immediate Out-Of-Memory (OOM kill code 137) on standard 512 MB free-tier container instances (Render Free, Koyeb, Hugging Face Spaces). |
| **3. Slow Startup & Healthcheck Timeouts** | Loading ONNX graph and tokenizer on cold starts took 15–25 seconds. | Liveness probes failed before the server could respond, causing orchestrator crash loops. |
| **4. Localhost / Tunnel Workaround** | Because the container could not boot within 512 MB limits, the system relied on running locally on port 8080 with `cloudflared.exe` tunnel. | Fragile, non-production, required user PC to stay awake 24/7. |

---

## 2. Codebase Import & Runtime Inspection

We inspected all production modules (`api/main.py`, `api/rag_service.py`, `scripts/dense_retriever.py`, `scripts/hybrid_retriever.py`, `scripts/llm_generation_pipeline.py`, etc.):
- **Findings**:
  - `torch`, `onnxruntime`, `transformers`, and `sentence_transformers` are **NEVER** imported at module top-level.
  - They are only lazily imported inside the rollback classes (`ONNXEmbeddingProvider._init_runtime()` and `LocalE5EmbeddingProvider._load_model()`).
  - Production code path (`GeminiEmbeddingProvider` + `dense_index_cloud_v3.npz`) uses pure Python standard libraries + `requests` + `numpy` + `fastapi`.
  - **Conclusion**: Local embedding runtimes (`onnxruntime`, `transformers`, `tokenizers`) can be safely removed from production `requirements.txt` with zero impact on production code.

---

## 3. Production Architecture Verification Plan

```
Client (Web / Mobile)
        │
        ▼
FastAPI Cloud Service (Lightweight Container: ~150 MB, <80 MB RAM)
        │
        ├───────────────────────────────┐
        ▼                               ▼
Cloud Embedding API (Gemini 2)     BM25 Keyword Search
        │                               │
        ▼                               ▼
Cloud Dense Index (171 vectors)   BM25 Top Candidates
        │                               │
        └───────────────┬───────────────┘
                        ▼
            Reciprocal Rank Fusion (RRF k=60)
                        ▼
            Clinical Reranker
                        ▼
            Evidence Quality Gate
                        ▼
            Claim Coverage Validator
                        ▼
            Salem Contract (Circuit Breaker)
                        │
            ┌───────────┴───────────┐
            │ [NO EVIDENCE]         │ [GROUNDED]
            ▼                       ▼
   Deterministic Abstention    Gemini LLM Generation
     (0 LLM API credits)            │
                                    ▼
                          Simplification Verifier
                                    │
                                    ▼
                         Grounded Answer + Citations
```

---

## 4. Rollback Preservation Confirmation
- `outputs/dense_index_v2.npz` (384d, 242 KB) is strictly preserved.
- `outputs/dense_metadata_v2.json` is strictly preserved.
- `ONNXEmbeddingProvider` and `LocalE5EmbeddingProvider` code remain intact in `scripts/dense_retriever.py` for offline/local rollback via `EMBEDDING_PROVIDER=onnx`.
