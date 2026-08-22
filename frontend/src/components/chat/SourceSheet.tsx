import { useState, useMemo } from 'react';
import { BottomSheet } from '../ui/BottomSheet';
import type { EvidenceSource } from '../../types/chat';
import { BookOpen, ShieldCheck, ExternalLink, FileText, CheckCircle2 } from 'lucide-react';

export interface SourceSheetProps {
  isOpen: boolean;
  onClose: () => void;
  sources: EvidenceSource[];
}

/** Helper to render original text with safe, verified highlight */
function renderHighlightedText(originalText: string, highlightText?: string) {
  if (!originalText) return null;

  // Strict verification: highlightText MUST exist and be an exact substring of originalText
  if (!highlightText || !originalText.includes(highlightText)) {
    return (
      <p className="text-xs sm:text-sm text-[#334155] leading-relaxed whitespace-pre-wrap font-sans">
        {originalText}
      </p>
    );
  }

  const parts = originalText.split(highlightText);
  // Reconstruct safely
  return (
    <p className="text-xs sm:text-sm text-[#334155] leading-relaxed whitespace-pre-wrap font-sans">
      {parts.map((part, i) => (
        <span key={i}>
          {part}
          {i < parts.length - 1 && (
            <mark
              style={{
                backgroundColor: 'rgba(59, 130, 246, 0.20)',
                color: 'inherit',
                borderRadius: '4px',
                padding: '2px 4px',
                fontWeight: 600,
              }}
              title="الجزء الداعم الموثق من الدليل"
            >
              {highlightText}
            </mark>
          )}
        </span>
      ))}
    </p>
  );
}

export const SourceSheet = ({ isOpen, onClose, sources }: SourceSheetProps) => {
  const [activeTab, setActiveTab] = useState(0);

  // Safe active source fallback
  const currentSource = useMemo(() => {
    if (!sources || sources.length === 0) return null;
    return sources[Math.min(activeTab, sources.length - 1)];
  }, [sources, activeTab]);

  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <BottomSheet
      isOpen={isOpen}
      onClose={onClose}
      title="الدليل المستخدم"
      subtitle="إرشادات منظمة الصحة العالمية المعتمدة لعلاج إدمان التبغ (WHO 2024)"
    >
      <div className="flex flex-col gap-4 font-arabic" dir="rtl">
        {/* Source Switcher Tabs if multiple sources */}
        {sources.length > 1 && (
          <div className="flex items-center gap-2 overflow-x-auto pb-1 border-b border-[#E2E8F0] scrollbar-none">
            {sources.map((src, i) => (
              <button
                key={src.id || i}
                type="button"
                onClick={() => setActiveTab(i)}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all cursor-pointer flex items-center gap-1.5 ${
                  activeTab === i
                    ? 'bg-[#2D8BFF] text-white shadow-xs'
                    : 'bg-[#F1F5F9] text-[#64748B] hover:bg-[#E2E8F0] hover:text-[#1E293B]'
                }`}
              >
                <FileText className="w-3.5 h-3.5" />
                <span>
                  {src.section ? `القسم ${src.section}` : `المصدر ${i + 1}`}
                </span>
              </button>
            ))}
          </div>
        )}

        {/* Active Source Card */}
        {currentSource && (
          <div className="flex flex-col gap-4">
            {/* Header Metadata */}
            <div className="p-4 rounded-2xl bg-[#F8FAFC] border border-[#E2E8F0] flex flex-col gap-3">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2.5">
                  <div className="w-9 h-9 rounded-xl bg-[#2D8BFF]/10 text-[#2D8BFF] flex items-center justify-center shrink-0">
                    <BookOpen className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-[#0F172A]">
                      {currentSource.sectionTitle || currentSource.title}
                    </h4>
                    <span className="text-xs text-[#64748B]">
                      {currentSource.organization} · {currentSource.year}
                    </span>
                  </div>
                </div>

                <span className="text-[11px] px-2.5 py-1 rounded-full bg-[#10B981]/10 text-[#059669] border border-[#10B981]/20 font-semibold shrink-0">
                  {currentSource.sourceType || 'دليل إكلينيكي معتمد'}
                </span>
              </div>

              {/* Badges: Section & Page */}
              <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-[#E2E8F0] text-xs">
                {currentSource.section && (
                  <span className="px-2.5 py-1 rounded-lg bg-[#FFFFFF] border border-[#E2E8F0] text-[#334155] font-medium">
                    القسم: <strong className="text-[#0F172A]">{currentSource.section}</strong>
                  </span>
                )}
                {currentSource.pageStart && (
                  <span className="px-2.5 py-1 rounded-lg bg-[#FFFFFF] border border-[#E2E8F0] text-[#334155] font-medium">
                    الصفحة: <strong className="text-[#0F172A]">{currentSource.pageStart}</strong>
                    {currentSource.pageEnd && currentSource.pageEnd !== currentSource.pageStart
                      ? ` – ${currentSource.pageEnd}`
                      : ''}
                  </span>
                )}
                <span className="px-2.5 py-1 rounded-lg bg-[#2D8BFF]/10 text-[#1E40AF] font-medium flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>دليل معتمد WHO 2024</span>
                </span>
              </div>
            </div>

            {/* Original Verbatim Evidence */}
            {currentSource.originalText ? (
              <div className="p-4 rounded-2xl bg-[#FFFFFF] border border-[#CBD5E1] shadow-xs flex flex-col gap-2.5">
                <div className="flex items-center justify-between pb-2 border-b border-[#F1F5F9]">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-[#0F172A]">
                    <ShieldCheck className="w-4 h-4 text-[#2D8BFF]" />
                    <span>النص الأصلي من الدليل (Original Evidence):</span>
                  </div>
                  {currentSource.highlightText && (
                    <span className="text-[10px] px-2 py-0.5 rounded-md bg-[#2D8BFF]/15 text-[#1D4ED8] font-medium">
                      مظلل بالجزء الداعم
                    </span>
                  )}
                </div>

                {/* Text container */}
                <div className="max-h-[300px] overflow-y-auto p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] font-arabic">
                  {renderHighlightedText(currentSource.originalText, currentSource.highlightText)}
                </div>
              </div>
            ) : null}

            {/* Source URL Action */}
            {currentSource.externalUrl ? (
              <div className="flex items-center justify-between p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                <span className="text-xs text-[#64748B]">
                  وثيقة منظمة الصحة العالمية الرسمية
                </span>
                <a
                  href={currentSource.externalUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#2D8BFF] text-white hover:bg-[#1D4ED8] text-xs font-semibold transition-colors shadow-xs cursor-pointer"
                >
                  <span>فتح المصدر الأصلي</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>
            ) : (
              <div className="text-xs text-[#94A3B8] text-center p-2">
                رابط المصدر غير متوفر
              </div>
            )}
          </div>
        )}
      </div>
    </BottomSheet>
  );
};
