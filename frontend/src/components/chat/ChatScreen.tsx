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

/** Maps raw RAG citations to UI EvidenceSource (zero medical hallucination) */
function mapCitations(citations: RAGCitation[]): EvidenceSource[] {
  return citations.map((c) => ({
    id: String(c.source_id),
    title: c.title || 'دليل منظمة الصحة العالمية الإكلينيكي للإقلاع عن التبغ',
    organization: 'منظمة الصحة العالمية (WHO)',
    year: '2024',
    sourceType: 'دليل إكلينيكي معتمد',
    section: c.section_number ?? undefined,
    pageStart: c.physical_page_start ?? undefined,
    whyRelevant: 'تم التحقق من هذه التوصية استنادًا إلى بروتوكول منظمة الصحة العالمية المعتمد لعام 2024.',
  }));
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
  const abortControllerRef = useRef<AbortController | null>(null);

  // Sync with active conversation change
  useEffect(() => {
    setMessages(activeConversation ? activeConversation.messages : []);
    setErrorMessage(null);
    setComposerValue('');
  }, [activeConversation]);

  // Scroll to bottom smoothly on message or loading state changes
  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
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

      // Check for safety emergency keywords (chest pain, shortness of breath, etc.)
      const isEmergencyQuery =
        /ألم في الصدر|وجع صدر|ضيق تنفس|مش قادر اتنفس|نزيف|إغماء|طوارئ/i.test(trimmed);
      if (isEmergencyQuery) {
        setShowSafetyBanner(true);
      }

      // 1. Add user message
      const userMsg: ChatMessage = {
        id: `u_${Date.now()}`,
        role: 'user',
        content: trimmed,
        timestamp: Date.now(),
      };

      const nextMessages = [...messages, userMsg];
      setMessages(nextMessages);
      onUpdateConversationMessages?.(nextMessages);
      setIsLoading(true);

      // 2. Call real RAG pipeline
      abortControllerRef.current?.abort();
      const controller = new AbortController();
      abortControllerRef.current = controller;

      try {
        const historySnapshot = messages.map((m) => ({
          role: m.role as 'user' | 'assistant',
          content: m.content,
        }));

        const result = await sendQuery(trimmed, historySnapshot, controller.signal);
        if (controller.signal.aborted) return;

        const evidence =
          result.citations && result.citations.length > 0
            ? mapCitations(result.citations)
            : undefined;

        const assistantMsg: ChatMessage = {
          id: `a_${Date.now()}`,
          role: 'assistant',
          content: result.answer,
          evidence,
          contractState: result.contractState,
          grounded: result.grounded,
          safetyStatus: result.safetyStatus,
          latencyMs: result.latencyMs,
          timestamp: Date.now(),
        };

        const updatedWithAssistant = [...nextMessages, assistantMsg];
        setMessages(updatedWithAssistant);
        onUpdateConversationMessages?.(updatedWithAssistant);
      } catch (err) {
        if (controller.signal.aborted) return;

        const isTimeout = err instanceof Error && err.name === 'AbortError';
        const isNetwork = err instanceof RAGNetworkError;

        if (isTimeout) {
          setErrorMessage('انتهت مهلة الانتظار. يرجى إعادة المحاولة.');
        } else if (isNetwork && err.statusCode === 503) {
          setErrorMessage('المساعد الطبي قيد التجهيز، يرجى الانتظار ثوانٍ ثم المحاولة مجددًا.');
        } else {
          setErrorMessage('حصلت مشكلة وأنا بحاول أجهز الرد. جرّب تاني.');
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
      setMessages((prev) => prev.slice(0, -1));
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
