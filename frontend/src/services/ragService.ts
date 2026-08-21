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

export interface RAGCitation {
  source_id: number;
  section_number?: string | null;
  physical_page_start?: number | null;
  title: string;
  chunk_id: string;
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

const RAW_API_URL = import.meta.env.VITE_API_URL;
// Ensure no trailing slash
export const BASE_API = (RAW_API_URL ? String(RAW_API_URL).trim().replace(/\/+$/, '') : '');

if (!BASE_API) {
  console.warn(
    '[Oxygen RAG] Missing VITE_API_URL environment variable. ' +
    'API calls will fall back to the current origin. ' +
    'In Production (Vercel), make sure to configure VITE_API_URL pointing to your backend service.'
  );
}

const RAG_ENDPOINT = `${BASE_API}/api/v1/chat`;
const HEALTH_ENDPOINT = `${BASE_API}/api/v1/health`;
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

  try {
    const response = await fetch(RAG_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body,
      signal: effectiveSignal,
    });

    if (!response.ok) {
      let errBody = '';
      try {
        errBody = await response.text();
      } catch {
        // Ignore read failure
      }

      console.error('[Oxygen RAG API Error]', {
        endpoint: RAG_ENDPOINT,
        status: response.status,
        statusText: response.statusText,
        responseBody: errBody.slice(0, 500),
      });

      throw new RAGNetworkError(
        response.status,
        `HTTP ${response.status}: ${response.statusText || 'Request Failed'}`,
        errBody,
        RAG_ENDPOINT
      );
    }

    const data: RAGResponse = await response.json();

    return {
      answer: data.answer,
      contractState: data.contract_state,
      grounded: data.grounded,
      safetyStatus: data.safety_status,
      provider: data.provider,
      model: data.model,
      citations: data.citations ?? [],
      latencyMs: data.latency_ms,
      requestId: data.request_id,
    };
  } catch (err: unknown) {
    if (err instanceof RAGNetworkError) {
      throw err;
    }
    const isAbort = err instanceof Error && err.name === 'AbortError';
    if (!isAbort) {
      console.error('[Oxygen RAG Network Exception]', {
        endpoint: RAG_ENDPOINT,
        errorType: err instanceof Error ? err.name : typeof err,
        message: err instanceof Error ? err.message : String(err),
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
    const r = await fetch(HEALTH_ENDPOINT, { method: 'GET' });
    return r.ok;
  } catch {
    return false;
  }
}

