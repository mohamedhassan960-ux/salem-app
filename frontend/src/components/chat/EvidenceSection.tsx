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
    <div className={`mt-3 pt-2.5 border-t border-[#D9E2F0] w-full font-arabic ${className}`} dir="rtl">
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        className="flex items-center justify-between w-full text-xs font-semibold text-[#1E3A8A] hover:text-[#2D8BFF] py-1 cursor-pointer transition-colors"
      >
        <span className="flex items-center gap-1.5">
          <BookOpen className="w-3.5 h-3.5 text-[#2D8BFF]" />
          <span>المصادر الإكلينيكية المعتمدة ({evidence.length})</span>
        </span>
        <ChevronDown className={`w-3.5 h-3.5 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="mt-2 flex flex-col gap-2 animate-in fade-in duration-150">
          {evidence.map((item) => (
            <div
              key={item.id}
              className="p-3 rounded-2xl bg-[#F4F7FB] border border-[#D9E2F0] text-xs text-[#061A3A] flex flex-col gap-1"
            >
              <div className="flex items-center justify-between font-bold text-[#061A3A]">
                <span>{item.title}</span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#2D8BFF]/10 text-[#1E3A8A] border border-[#2D8BFF]/20">
                  {item.organization || 'WHO 2024'}
                </span>
              </div>
              {item.section && (
                <div className="text-[11px] text-[#5F708C]">
                  <span>القسم: {item.section}</span>
                </div>
              )}
              {item.excerpt && (
                <p className="text-[11px] text-[#5F708C] italic bg-[#FFFFFF] p-2 rounded-xl border-r-2 border-[#2D8BFF] mt-0.5">
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
