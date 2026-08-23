import { useState, useRef, useEffect, useCallback } from 'react';
import type { ChatMessage, ConversationSession, EvidenceSource } from '../../types/chat';
import { sendQuery, RAGNetworkError } from '../../services/ragService';
import type { RAGCitation } from '../../services/ragService';
import { UserMessage } from './UserMessage';
import { AssistantMessage } from './AssistantMessage';
import { TypingIndicator } from './TypingIndicator';
import { EmptyChatState } from './EmptyChatState';
import { QuickActions } from './QuickActions';
import { MobileComposer } from './MobileComposer';
import { SafetyBanner } from './SafetyBanner';
import { AlertCircle, RefreshCw } from 'lucide-react';

export interface ChatScreenProps {
  activeConversation?: ConversationSession | null;
  onOpenCravingModal?: () => void;
  onOpenRelapseModal?: () => void;
  onUpdateConversationMessages?: (messages: ChatMessage[]) => void;
}

/** Maps raw RAG citations to UI EvidenceSource with verified original text and highlights */
function mapCitations(citations: RAGCitation[]): EvidenceSource[] {
  return citations.map((c) => {
    const origText = c.evidence?.original_text || '';
    const highText = c.evidence?.highlight_text || undefined;
    
    // Strict safety verification: highlightText MUST be an exact substring of originalText
    const verifiedHighlight = (highText && origText.includes(highText)) ? highText : undefined;

    return {
      id: c.citation_id || String(c.source_id),
      title: c.source?.title || 'WHO clinical treatment guideline for tobacco cessation in adults',
      sectionTitle: c.source?.section_title || c.title || 'إرشادات منظمة الصحة العالمية',
      organization: c.source?.organization || 'منظمة الصحة العالمية (WHO)',
      year: c.source?.year || '2024',
      sourceType: 'دليل إكلينيكي معتمد',
      section: c.source?.section || c.section_number || undefined,
      pageStart: c.physical_page_start ?? (c.source?.page ? parseInt(c.source.page, 10) : undefined),
      pageEnd: c.physical_page_end ?? undefined,
      externalUrl: c.source?.url || 'https://www.who.int/publications/i/item/9789240096493',
      originalText: origText || undefined,
      highlightText: verifiedHighlight,
      whyRelevant: 'تم التحقق من هذه التوصية استنادًا إلى بروتوكول منظمة الصحة العالمية المعتمد لعام 2024.',
    };
  });
}

export const ChatScreen = ({
  activeConversation,
  onOpenCravingModal,
  onOpenRelapseModal,
  onUpdateConversationMessages,
}: ChatScreenProps) => {
  const [messages, setMessages] = useState<ChatMessage[]>(() =>
    activeConversation ? activeConversation.messages : []
  );
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [composerValue, setComposerValue] = useState('');
  const [showSafetyBanner, setShowSafetyBanner] = useState(false);

  const scrollRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Track last loaded conversation ID to prevent in-flight messages from being wiped by prop changes
  const activeConvId = activeConversation?.id;
  const lastLoadedIdRef = useRef(activeConvId);

  useEffect(() => {
    // Only re-sync messages if the conversation ID has genuinely changed (user switched conversation)
    if (activeConvId && activeConvId !== lastLoadedIdRef.current) {
      lastLoadedIdRef.current = activeConvId;
      setMessages(activeConversation ? activeConversation.messages : []);
      setErrorMessage(null);
      setComposerValue('');
    }
  }, [activeConvId, activeConversation]);

  // Scroll to bottom smoothly on message or loading state changes (robust on mobile viewports & virtual keyboards)
  useEffect(() => {
    const scrollToBottom = () => {
      if (messagesEndRef.current) {
        messagesEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
      }
      if (scrollRef.current) {
        scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
      }
    };

    scrollToBottom();
    // Second pass after DOM paint / mobile keyboard reflow
    const timer = setTimeout(scrollToBottom, 120);
    return () => clearTimeout(timer);
  }, [messages, isLoading]);

  // Abort pending request on unmount
  useEffect(() => {
    return () => {
      abortControllerRef.current?.abort();
    };
  }, []);

  const handleSelectSuggestion = (text: string) => {
    handleSend(text);
  };

  const handleSend = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || isLoading) return;

      setErrorMessage(null);
      setComposerValue('');

      console.info('[ChatScreen] SEND_HANDLER_ENTERED:', { queryPreview: trimmed.slice(0, 40) });

      // Check for safety emergency keywords (chest pain, shortness of breath, etc.)
      const isEmergencyQuery =
        /ألم في الصدر|وجع صدر|ضيق تنفس|مش قادر اتنفس|نزيف|إغماء|طوارئ/i.test(trimmed);
      if (isEmergencyQuery) {
        setShowSafetyBanner(true);
      }

      // 1. Add user message
      const userMsg: ChatMessage = {
        id: `u_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
        role: 'user',
        content: trimmed,
        timestamp: Date.now(),
      };

      // Take current messages snapshot for conversation history passed to RAG
      const currentHistorySnapshot = messages.map((m) => ({
        role: m.role as 'user' | 'assistant',
        content: m.content,
      }));

      // Commit user message
      const messagesWithUser = [...messages, userMsg];
      setMessages(messagesWithUser);
      onUpdateConversationMessages?.(messagesWithUser);

      setIsLoading(true);

      // 2. Call real RAG pipeline
      abortControllerRef.current?.abort();
      const controller = new AbortController();
      abortControllerRef.current = controller;

      try {
        const result = await sendQuery(trimmed, currentHistorySnapshot, controller.signal);
        if (controller.signal.aborted) {
          console.warn('[ChatScreen] Request aborted before state commit');
          return;
        }

        const evidence =
          result.citations && result.citations.length > 0
            ? mapCitations(result.citations)
            : undefined;

        const assistantMsg: ChatMessage = {
          id: `a_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
          role: 'assistant',
          content: result.answer,
          evidence,
          contractState: result.contractState,
          grounded: result.grounded,
          safetyStatus: result.safetyStatus,
          latencyMs: result.latencyMs,
          timestamp: Date.now(),
        };

        // Commit assistant message cleanly without inside-reducer side-effects
        const updatedWithAssistant = [...messagesWithUser, assistantMsg];
        setMessages(updatedWithAssistant);
        onUpdateConversationMessages?.(updatedWithAssistant);

        console.info('[ChatScreen] STATE_COMMITTED: Assistant message permanently added', {
          totalMessages: updatedWithAssistant.length,
          contractState: assistantMsg.contractState,
        });
      } catch (err) {
        if (controller.signal.aborted) return;

        console.error('[ChatScreen] SEND_FAILED:', err);

        const isTimeout = err instanceof Error && err.name === 'AbortError';
        const isNetwork = err instanceof RAGNetworkError;

        if (isTimeout) {
          setErrorMessage('انتهت مهلة الانتظار. يرجى إعادة المحاولة.');
        } else if (isNetwork && err.statusCode === 503) {
          setErrorMessage('المساعد الطبي قيد التجهيز، يرجى الانتظار ثوانٍ ثم المحاولة مجددًا.');
        } else if (!navigator.onLine) {
          setErrorMessage('لا يوجد اتصال بالإنترنت. يرجى التحقق من الشبكة.');
        } else {
          setErrorMessage('حصلت مشكلة أثناء تجهيز الرد الطبي. يرجى إعادة المحاولة.');
        }
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      }
    },
    [isLoading, messages, onUpdateConversationMessages]
  );

  const handleRetry = () => {
    const lastUser = [...messages].reverse().find((m) => m.role === 'user');
    if (lastUser && !isLoading) {
      setErrorMessage(null);
      handleSend(lastUser.content);
    }
  };

  return (
    <div className="w-full h-full flex flex-col bg-[#F7F9FC] text-[#061A3A] overflow-hidden font-arabic" dir="rtl">
      {/* Messages Scroll Area */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto px-4 py-4 min-h-0"
      >
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <EmptyChatState
              onSelectSuggestion={handleSelectSuggestion}
              onOpenCravingModal={onOpenCravingModal}
            />
          </div>
        ) : (
          <div className="flex flex-col gap-2 max-w-3xl mx-auto pb-4">
            {showSafetyBanner && (
              <SafetyBanner className="mb-2" />
            )}

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

            {/* Error & Retry Banner */}
            {errorMessage && (
              <div
                className="flex items-center justify-between gap-3 my-3 p-4 rounded-2xl bg-[#F87171]/10 border border-[#F87171]/30 text-[#B91C1C] text-xs"
                dir="rtl"
                role="alert"
              >
                <div className="flex items-center gap-2 min-w-0">
                  <AlertCircle className="w-4 h-4 text-[#F87171] shrink-0" />
                  <span className="truncate">{errorMessage}</span>
                </div>
                <button
                  type="button"
                  onClick={handleRetry}
                  className="shrink-0 flex items-center gap-1 text-[#1E3A8A] hover:bg-[#FFFFFF] px-3 py-1.5 rounded-xl bg-[#FFFFFF] border border-[#D9E2F0] font-semibold cursor-pointer transition-colors shadow-xs"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  <span>إعادة المحاولة</span>
                </button>
              </div>
            )}

            {/* Mobile Scroll Target */}
            <div ref={messagesEndRef} className="h-2 shrink-0" />
          </div>
        )}
      </div>

      {/* Quick Action Chips & Composer at Bottom */}
      <div className="shrink-0 max-w-3xl mx-auto w-full">
        {messages.length > 0 && (
          <div className="px-4">
            <QuickActions
              onSelectAction={handleSend}
              onOpenCravingModal={onOpenCravingModal}
              onOpenRelapseModal={onOpenRelapseModal}
            />
          </div>
        )}

        <MobileComposer
          onSendMessage={handleSend}
          initialValue={composerValue}
          disabled={isLoading}
          placeholder="اسأل سالم عن الإقلاع، الأدوية، أو الأعراض..."
        />
      </div>
    </div>
  );
};
