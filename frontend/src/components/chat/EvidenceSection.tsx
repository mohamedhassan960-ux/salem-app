import { useState } from 'react';
import type { EvidenceSource } from '../../types/chat';
import { BookOpen, ChevronDown } from 'lucide-react';

export interface EvidenceSectionProps {
  evidence: EvidenceSource[];
  className?: string;
}

export const EvidenceSection = ({ evidence, className = '' }: EvidenceSectionProps) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!evidence || evidence.length === 0) return null;

  return (
    <div className={`mt-3 pt-2.5 border-t border-slate-800/80 w-full ${className}`} dir="rtl">
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        className="flex items-center justify-between w-full text-xs font-semibold text-sky-400 hover:text-sky-300 py-1 cursor-pointer transition-colors active:scale-[0.99]"
      >
        <span className="flex items-center gap-1.5">
          <BookOpen className="w-3.5 h-3.5 text-sky-400" />
          <span>المصادر الإكلينيكية المعتمدة ({evidence.length})</span>
        </span>
        <ChevronDown className={`w-3.5 h-3.5 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="mt-2 flex flex-col gap-2 animate-in fade-in slide-in-from-top-1 duration-200">
          {evidence.map((item) => (
            <div
              key={item.id}
              className="p-2.5 rounded-xl bg-slate-950/80 border border-slate-800 text-[12px] font-arabic text-slate-300 flex flex-col gap-1"
            >
              <div className="flex items-center justify-between font-semibold text-slate-200">
                <span>{item.title}</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-sky-500/10 text-sky-400 border border-sky-500/20">
                  {item.sourceDoc}
                </span>
              </div>
              {item.section && (
                <div className="text-[11px] text-slate-400">
                  <span>القسم: {item.section}</span>
                </div>
              )}
              {item.excerpt && (
                <p className="text-[11px] text-slate-400 italic bg-slate-900/60 p-2 rounded-lg border-r-2 border-sky-500 mt-0.5">
                  &ldquo;{item.excerpt}&rdquo;
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
