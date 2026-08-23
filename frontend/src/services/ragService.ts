/**
 * RAG Service — Thin integration adapter between Chat UI and Oxygen Medical RAG API.
 *
 * Architecture contract:
 *   ChatScreen → ragService.sendQuery() → POST /api/v1/chat → existing RAG pipeline
 *
 * This file contains ZERO RAG logic.
 * It only translates UI types ↔ API wire format and handles network errors safely.
 *
 * RAG pipeline is completely frozen. This adapter never modifies:
 *   - retrieval thresholds
 *   - reranking
 *   - evidence quality gate
 *   - grounded answer contract
 *   - circuit breaker decisions
 *   - LLM prompts
 */

// ─── Wire-format types (matching api/schemas.py exactly) ─────────────────────

export interface RAGConversationTurn {
  role: 'user' | 'assistant';
  content: string;
}

export interface RAGCitationSource {
  title?: string;
  section_title?: string;
  organization?: string;
  year?: string;
  section?: string | null;
  page?: string | null;
  url?: string | null;
}

export interface RAGCitationEvidence {
  original_text?: string;
  highlight_text?: string | null;
}

export interface RAGCitation {
  citation_id?: string;
  source_id: number;
  section_number?: string | null;
  physical_page_start?: number | null;
  physical_page_end?: number | null;
  title: string;
  chunk_id: string;
  source?: RAGCitationSource;
  evidence?: RAGCitationEvidence;
}

export interface RAGResponse {
  request_id: string;
  answer: string;
  contract_state: string; // SUPPORTED | PARTIALLY_SUPPORTED | UNSUPPORTED | OUT_OF_SCOPE | ABSTAIN
  grounded: boolean;
  safety_status: string;
  provider: string;
  model: string;
  citations: RAGCitation[];
  latency_ms: number;
  metadata: Record<string, unknown>;
}

// ─── UI-facing result (what ChatScreen consumes) ─────────────────────────────

export interface RAGResult {
  answer: string;
  contractState: string;
  grounded: boolean;
  safetyStatus: string;
  provider: string;
  model: string;
  citations: RAGCitation[];
  latencyMs: number;
  requestId: string;
}

export class RAGNetworkError extends Error {
  public readonly statusCode?: number;
  public readonly responseBody?: string;
  public readonly endpoint?: string;

  constructor(statusCode?: number, message?: string, responseBody?: string, endpoint?: string) {
    super(message ?? 'RAG network error');
    this.statusCode = statusCode;
    this.responseBody = responseBody;
    this.endpoint = endpoint;
    this.name = 'RAGNetworkError';
  }
}

// ─── Base URL Configuration & Validation ──────────────────────────────────────

export function getBaseApi(): string {
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl && typeof envUrl === 'string' && envUrl.trim().length > 0) {
    return envUrl.trim().replace(/\/+$/, '');
  }
  if (typeof window !== 'undefined') {
    const host = window.location.hostname;
    if (host === 'localhost' || host === '127.0.0.1') {
      return 'http://127.0.0.1:8000';
    }
  }
  return 'https://salem-backend.vercel.app';
}

export const BASE_API = getBaseApi();
const REQUEST_TIMEOUT_MS = 120_000; // 2 minutes — LLM generation and retrieval timeout

/**
 * Sends a query to the existing Oxygen Medical RAG pipeline via HTTP.
 *
 * @param query          The user's question text (trimmed, non-empty).
 * @param history        Ordered prior turns to pass as conversation_history.
 *                       Passed verbatim to the RAG — no modification.
 * @param signal         Optional AbortSignal for cancellation.
 * @returns              RAGResult with the pipeline's verbatim response.
 * @throws RAGNetworkError on HTTP or network failures.
 */
export async function sendQuery(
  query: string,
  history: RAGConversationTurn[] = [],
  signal?: AbortSignal,
): Promise<RAGResult> {
  const correlationId = `req_cli_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
  const body = JSON.stringify({
    query: query.trim(),
    conversation_history: history.length > 0 ? history : undefined,
  });

  // Timeout via AbortController if no external signal is provided
  let timeoutId: ReturnType<typeof setTimeout> | undefined;
  let timeoutController: AbortController | undefined;
  let effectiveSignal = signal;

  if (!signal) {
    timeoutController = new AbortController();
    timeoutId = setTimeout(() => timeoutController!.abort(), REQUEST_TIMEOUT_MS);
    effectiveSignal = timeoutController.signal;
  }

  const endpoint = `${getBaseApi()}/api/v1/chat`;
  const startTime = performance.now();
  console.info(`[Oxygen RAG] [${correlationId}] REQUEST_START -> ${endpoint}`);

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Request-ID': correlationId,
      },
      body,
      signal: effectiveSignal,
    });

    const elapsed = Math.round(performance.now() - startTime);

    if (!response.ok) {
      let errBody = '';
      try {
        errBody = await response.text();
      } catch {
        // Ignore read failure
      }

      console.error(`[Oxygen RAG] [${correlationId}] HTTP_ERROR:`, {
        endpoint,
        status: response.status,
        statusText: response.statusText,
        elapsedMs: elapsed,
        responseBody: errBody.slice(0, 500),
      });

      throw new RAGNetworkError(
        response.status,
        `HTTP ${response.status}: ${response.statusText || 'Request Failed'}`,
        errBody,
        endpoint
      );
    }

    const data: RAGResponse = await response.json();
    console.info(`[Oxygen RAG] [${correlationId}] RESPONSE_SUCCESS:`, {
      requestId: data.request_id || correlationId,
      contractState: data.contract_state,
      provider: data.provider,
      citationsCount: data.citations?.length ?? 0,
      elapsedMs: elapsed,
    });

    return {
      answer: data.answer,
      contractState: data.contract_state,
      grounded: data.grounded,
      safetyStatus: data.safety_status,
      provider: data.provider,
      model: data.model,
      citations: data.citations ?? [],
      latencyMs: data.latency_ms ?? elapsed,
      requestId: data.request_id || correlationId,
    };
  } catch (err: unknown) {
    const elapsed = Math.round(performance.now() - startTime);
    if (err instanceof RAGNetworkError) {
      throw err;
    }
    const isAbort = err instanceof Error && err.name === 'AbortError';
    if (isAbort) {
      console.warn(`[Oxygen RAG] [${correlationId}] REQUEST_ABORTED (timeout or user cancel) after ${elapsed}ms`);
    } else {
      console.error(`[Oxygen RAG] [${correlationId}] NETWORK_EXCEPTION:`, {
        endpoint,
        errorType: err instanceof Error ? err.name : typeof err,
        message: err instanceof Error ? err.message : String(err),
        elapsedMs: elapsed,
      });
    }
    throw err;
  } finally {
    if (timeoutId !== undefined) clearTimeout(timeoutId);
  }
}

/**
 * Checks if the backend is reachable (liveness probe).
 * Does NOT initialize the pipeline — that happens on first /chat call.
 */
export async function checkHealth(): Promise<boolean> {
  try {
    const r = await fetch(`${getBaseApi()}/api/v1/health`, { method: 'GET' });
    return r.ok;
  } catch {
    return false;
  }
}

