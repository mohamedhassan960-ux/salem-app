import { useState, useEffect, useRef } from 'react';
import type { FormEvent, KeyboardEvent } from 'react';
import { Send, Mic } from 'lucide-react';

export interface MobileComposerProps {
  onSendMessage?: (text: string) => void;
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

  useEffect(() => {
    if (initialValue && initialValue !== text) {
      setText(initialValue);
    }
  }, [initialValue]);

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 120) + 'px';
  }, [text]);

  const canSend = text.trim().length > 0 && !disabled;

  const doSend = () => {
    if (!canSend) return;
    onSendMessage?.(text.trim());
    setText('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    doSend();
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      doSend();
    }
  };

  return (
    <div
      className="w-full shrink-0 bg-slate-900 border-t border-slate-800/80"
      style={{ paddingBottom: 'calc(0.625rem + var(--sab))', paddingTop: '0.625rem', paddingLeft: '0.875rem', paddingRight: '0.875rem' }}
      dir="rtl"
    >
      <form
        onSubmit={handleSubmit}
        className="flex items-end gap-2 bg-slate-800/80 rounded-2xl px-3 py-1.5 border border-slate-700/50 focus-within:border-sky-500/60 focus-within:ring-1 focus-within:ring-sky-500/30 transition-all"
      >
        <textarea
          ref={textareaRef}
          rows={1}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder={placeholder}
          aria-label="اكتب سؤالك الطبي"
          className="flex-1 bg-transparent text-slate-100 placeholder-slate-500 text-sm py-2 focus:outline-none resize-none min-h-[40px] max-h-[120px] leading-relaxed disabled:opacity-50"
          style={{ height: 'auto' }}
        />
        <button
          type="submit"
          disabled={!canSend}
          aria-label="إرسال السؤال"
          className={`shrink-0 w-9 h-9 mb-0.5 rounded-xl flex items-center justify-center transition-all duration-200 ${
            canSend
              ? 'bg-sky-500 hover:bg-sky-400 text-white active:scale-95'
              : 'bg-slate-700/60 text-slate-500 cursor-not-allowed'
          }`}
        >
          {canSend ? (
            <Send className="w-4 h-4 -scale-x-100" />
          ) : (
            <Mic className="w-4 h-4" />
          )}
        </button>
      </form>

      <p className="text-center text-[10px] text-slate-600 mt-1.5">
        مستند إلى دليل WHO 2024 الإكلينيكي
      </p>
    </div>
  );
};
