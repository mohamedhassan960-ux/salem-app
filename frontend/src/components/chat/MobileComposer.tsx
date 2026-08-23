import { useState, useRef, useEffect, type FormEvent, type KeyboardEvent, type PointerEvent } from 'react';
import { ArrowUp } from 'lucide-react';

export interface MobileComposerProps {
  onSendMessage: (text: string) => void;
  disabled?: boolean;
  placeholder?: string;
  initialValue?: string;
}

export const MobileComposer = ({
  onSendMessage,
  disabled = false,
  placeholder = 'اسأل سالم عن الإقلاع، الأدوية، أو الأعراض...',
  initialValue = '',
}: MobileComposerProps) => {
  const [text, setText] = useState(initialValue);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const isSubmittingRef = useRef(false);

  useEffect(() => {
    if (initialValue) {
      setText(initialValue);
      if (textareaRef.current) {
        textareaRef.current.focus();
      }
    }
  }, [initialValue]);

  const executeSend = () => {
    const trimmed = text.trim();
    if (!trimmed || disabled || isSubmittingRef.current) return;

    isSubmittingRef.current = true;
    onSendMessage(trimmed);
    setText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
    // Release debounce lock after brief tick
    setTimeout(() => {
      isSubmittingRef.current = false;
    }, 300);
  };

  const handleSubmit = (e?: FormEvent) => {
    if (e) e.preventDefault();
    executeSend();
  };

  const handlePointerDownSend = (e: PointerEvent<HTMLButtonElement>) => {
    // Crucial for mobile touch: prevent blur layout shift before execution
    if (!text.trim() || disabled) return;
    e.preventDefault();
    executeSend();
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      executeSend();
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
    const el = e.target;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 140)}px`;
  };

  const canSend = Boolean(text.trim()) && !disabled;

  return (
    <div
      className="w-full bg-[#FFFFFF] border-t border-[#D9E2F0] px-4 py-3 shrink-0 font-arabic"
      style={{ paddingBottom: 'calc(0.75rem + var(--sab))' }}
      dir="rtl"
    >
      <form onSubmit={handleSubmit} className="max-w-3xl mx-auto flex items-end gap-2">
        <div className="flex-1 relative bg-[#F1F5FA] rounded-2xl border border-[#D9E2F0] focus-within:border-[#2D8BFF] focus-within:bg-[#FFFFFF] focus-within:ring-2 focus-within:ring-[#2D8BFF]/20 transition-all duration-150">
          <textarea
            ref={textareaRef}
            rows={1}
            value={text}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            placeholder={placeholder}
            className="w-full bg-transparent px-4 py-3 text-sm text-[#061A3A] placeholder:text-[#8291A8] resize-none outline-none max-h-36 min-h-[44px] leading-relaxed block select-text"
          />
        </div>

        <button
          type="submit"
          onPointerDown={handlePointerDownSend}
          onClick={handleSubmit}
          disabled={!canSend}
          aria-label="إرسال الرسالة"
          className="
            w-11 h-11 min-w-[44px] min-h-[44px] rounded-2xl bg-[#2D8BFF] hover:bg-[#1E7AE6] active:bg-[#1569CC] text-white
            flex items-center justify-center shadow-xs transition-all duration-150 active:scale-95 cursor-pointer
            disabled:opacity-40 disabled:cursor-not-allowed disabled:active:scale-100 shrink-0
          "
        >
          <ArrowUp className="w-5 h-5" />
        </button>
      </form>
    </div>
  );
};
