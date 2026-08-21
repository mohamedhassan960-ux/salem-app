/**
 * ChatScreen — Primary product screen.
 *
 * Integration contract:
 *   handleSend() → ragService.sendQuery() → /api/v1/chat → existing Oxygen RAG pipeline
 *
 * The mock setTimeout has been REMOVED from the real send path.
 * All assistant responses come from the actual RAG. No fake medical content.
 *
 * RAG safety rules:
 *  - SUPPORTED / PARTIALLY_SUPPORTED → display grounded answer + citations
 *  - UNSUPPORTED / OUT_OF_SCOPE / ABSTAIN → display the RAG's deterministic response verbatim
 *  - Network / server errors → safe Arabic error message, no stack trace
 */

import { useState, useRef, useEffect, useCallback } from 'react';
import type { ChatMessage, ConversationSession, EvidenceSource } from '../../types/chat';
import { sendQuery, RAGNetworkError } from '../../services/ragService';
import type { RAGCitation } from '../../services/ragService';
import { UserMessage } from './UserMessage';
import { AssistantMessage } from './AssistantMessage';
import { TypingIndicator } from './TypingIndicator';
import { EmptyChatState } from './EmptyChatState';
import { MobileComposer } from './MobileComposer';
import { AlertCircle, RefreshCw } from 'lucide-react';

export interface ChatScreenProps {
  activeConversation?: ConversationSession | null;
}

/** Map RAG citations → UI EvidenceSource. Zero medical content rewriting. */
function mapCitations(citations: RAGCitation[]): EvidenceSource[] {
  return citations.map((c) => ({
    id: String(c.source_id),
    title: c.title,
    sourceDoc: 'دليل WHO الإكلينيكي 2024',
    section: c.section_number ?? undefined,
    chunkId: c.chunk_id,
    pageStart: c.physical_page_start ?? undefined,
  }));
}

export const ChatScreen = ({ activeConversation }: ChatScreenProps) => {
  const [messages, setMessages] = useState<ChatMessage[]>(() =>
    activeConversation ? activeConversation.messages : []
  );
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [composerValue, setComposerValue] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // When active conversation changes, reset state
  useEffect(() => {
    setMessages(activeConversation ? activeConversation.messages : []);
    setErrorMessage(null);
    setComposerValue('');
  }, [activeConversation]);

  // Scroll to bottom whenever messages or loading state changes
  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, [messages, isLoading]);

  // Cleanup any in-flight request on unmount
  useEffect(() => {
    return () => {
      abortControllerRef.current?.abort();
    };
  }, []);

  const handleSelectSuggestion = (text: string) => setComposerValue(text);

  const handleSend = useCallback(async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || isLoading) return;

    // Clear any previous error and pending composer value
    setErrorMessage(null);
    setComposerValue('');

    // 1. Display user message immediately
    const userMsg: ChatMessage = {
      id: `u_${Date.now()}`,
      role: 'user',
      content: trimmed,
      timestamp: Date.now(),
    };

    setMessages((prev) => {
      const updated = [...prev, userMsg];
      return updated;
    });
    setIsLoading(true);

    // 2. Call the real RAG — abort any previous in-flight request first
    abortControllerRef.current?.abort();
    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      // Build conversation history from messages currently in state
      // We use a functional read-style via closure — history up to the user message
      // Note: setMessages above hasn't flushed yet in this tick, so we close over
      // the snapshot before the user message was added.
      const historySnapshot = messages.map((m) => ({
        role: m.role as 'user' | 'assistant',
        content: m.content,
      }));

      const result = await sendQuery(trimmed, historySnapshot, controller.signal);

      if (controller.signal.aborted) return;

      // 3. Map RAG citations → UI evidence sources (verbatim, no invention)
      const evidence = result.citations.length > 0 ? mapCitations(result.citations) : undefined;

      // 4. Build assistant message from real RAG result
      const assistantMsg: ChatMessage = {
        id: `a_${Date.now()}`,
        role: 'assistant',
        content: result.answer,          // verbatim from RAG — never rewritten
        evidence,                         // real citations or undefined (no fakes)
        contractState: result.contractState,
        grounded: result.grounded,
        safetyStatus: result.safetyStatus,
        latencyMs: result.latencyMs,
        timestamp: Date.now(),
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      if (controller.signal.aborted) return;

      // Safe structured console logging for observability in both DEV and PROD
      if (err instanceof RAGNetworkError) {
        console.error('[ChatScreen] RAG Network Failure:', {
          endpoint: err.endpoint,
          statusCode: err.statusCode,
          message: err.message,
        });
      } else if (err instanceof Error && err.name !== 'AbortError') {
        console.error('[ChatScreen] Query Processing Error:', {
          name: err.name,
          message: err.message,
        });
      }

      const isTimeout =
        err instanceof Error && err.name === 'AbortError';
      const isNetwork =
        err instanceof RAGNetworkError;

      if (isTimeout) {
        setErrorMessage('انتهت مهلة الاستجابة. يرجى المحاولة مرة أخرى.');
      } else if (isNetwork && err.statusCode === 503) {
        setErrorMessage('المساعد الطبي لا يزال يتهيأ، يرجى الانتظار قليلاً ثم المحاولة مجدداً.');
      } else if (isNetwork && err.statusCode === 404) {
        setErrorMessage('تعذر الاتصال بخادم المعالجة الطبية (404 Not Found). يرجى التحقق من إعدادات الرابط VITE_API_URL.');
      } else {
        setErrorMessage('حدث خطأ أثناء معالجة السؤال.');
      }
    } finally {
      if (!controller.signal.aborted) {
        setIsLoading(false);
      }
    }
  }, [isLoading, messages]);

  const handleRetry = () => {
    // Retry the last user message
    const lastUser = [...messages].reverse().find((m) => m.role === 'user');
    if (lastUser && !isLoading) {
      setErrorMessage(null);
      // Remove the last user message from display to re-send cleanly
      setMessages((prev) => prev.slice(0, -1));
      handleSend(lastUser.content);
    }
  };

  return (
    <div className="w-full h-full flex flex-col bg-slate-950 text-slate-100 overflow-hidden">
      {/* Messages scroll area */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto overflow-x-hidden px-4 py-4 min-h-0"
      >
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <EmptyChatState onSelectSuggestion={handleSelectSuggestion} />
          </div>
        ) : (
          <div className="flex flex-col gap-1 max-w-2xl mx-auto pb-2">
            {messages.map((msg, idx) => {
              if (msg.role === 'user') {
                return <UserMessage key={msg.id} message={msg} />;
              }
              const prev = messages[idx - 1];
              return (
                <AssistantMessage
                  key={msg.id}
                  message={msg}
                  showAvatar={!prev || prev.role !== 'assistant'}
                />
              );
            })}

            {isLoading && <TypingIndicator className="mt-2" />}

            {errorMessage && (
              <div
                className="flex items-center justify-between gap-3 my-3 p-3 rounded-xl bg-rose-950/30 border border-rose-800/40 text-rose-300 text-xs"
                dir="rtl"
                role="alert"
              >
                <div className="flex items-center gap-2 min-w-0">
                  <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
                  <span className="truncate">{errorMessage}</span>
                </div>
                <button
                  type="button"
                  onClick={handleRetry}
                  className="shrink-0 flex items-center gap-1 text-sky-400 hover:text-sky-300 px-2 py-1.5 rounded-lg bg-slate-900 border border-slate-700 cursor-pointer transition-colors"
                >
                  <RefreshCw className="w-3 h-3" />
                  <span>حاول مرة أخرى</span>
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Composer — always at bottom, disabled while loading */}
      <MobileComposer
        onSendMessage={handleSend}
        initialValue={composerValue}
        disabled={isLoading}
        placeholder="اسأل سالم عن الإقلاع، الأدوية، أو الأعراض..."
      />
    </div>
  );
};
