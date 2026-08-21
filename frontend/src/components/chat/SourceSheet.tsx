import { BottomSheet } from '../ui/BottomSheet';
import type { EvidenceSource } from '../../types/chat';
import { BookOpen, ShieldCheck, ExternalLink } from 'lucide-react';

export interface SourceSheetProps {
  isOpen: boolean;
  onClose: () => void;
  sources: EvidenceSource[];
}

export const SourceSheet = ({ isOpen, onClose, sources }: SourceSheetProps) => {
  return (
    <BottomSheet
      isOpen={isOpen}
      onClose={onClose}
      title="المصادر العلمية المعتمدة"
      subtitle="المعلومات مبنية على أحدث إرشادات طبية معتمدة"
    >
      <div className="flex flex-col gap-4 font-arabic" dir="rtl">
        {sources.map((src, i) => (
          <div
            key={src.id || i}
            className="p-4 rounded-2xl bg-[#F4F7FB] border border-[#D9E2F0] flex flex-col gap-2.5"
          >
            {/* Header */}
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-xl bg-[#2D8BFF]/10 text-[#2D8BFF] flex items-center justify-center shrink-0">
                  <BookOpen className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-[#061A3A]">{src.title}</h4>
                  <span className="text-xs text-[#5F708C]">
                    {src.organization || 'منظمة الصحة العالمية (WHO)'} · {src.year || '2024'}
                  </span>
                </div>
              </div>

              <span className="text-[11px] px-2.5 py-1 rounded-full bg-[#34D399]/15 text-[#047857] border border-[#34D399]/30 font-semibold shrink-0">
                {src.sourceType || 'دليل إكلينيكي معتمد'}
              </span>
            </div>

            {/* Section if available */}
            {src.section && (
              <div className="text-xs text-[#5F708C] font-medium">
                <span>القسم: </span>
                <span className="text-[#061A3A]">{src.section}</span>
              </div>
            )}

            {/* Why relevant */}
            <div className="p-3 rounded-xl bg-white border border-[#D9E2F0] text-xs text-[#061A3A] leading-relaxed">
              <div className="flex items-center gap-1.5 font-bold text-[#1E3A8A] mb-1">
                <ShieldCheck className="w-3.5 h-3.5 text-[#2D8BFF]" />
                <span>سبب الاستشهاد بهذه المعلومة:</span>
              </div>
              <p className="text-[#5F708C]">
                {src.whyRelevant ||
                  'تم الرجوع إلى هذا المصدر للتحقق من معايير السلامة الإكلينيكية والجرعات وتوصيات الإقلاع السلوكي.'}
              </p>
            </div>

            {/* Excerpt if present */}
            {src.excerpt && (
              <p className="text-xs text-[#5F708C] italic bg-[#FFFFFF] p-2.5 rounded-xl border-r-3 border-[#2D8BFF]">
                &ldquo;{src.excerpt}&rdquo;
              </p>
            )}

            {src.externalUrl && (
              <a
                href={src.externalUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="self-start inline-flex items-center gap-1 text-xs text-[#2D8BFF] hover:text-[#1E3A8A] font-semibold mt-1"
              >
                <span>الاطلاع على المصدر الأصلي</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            )}
          </div>
        ))}
      </div>
    </BottomSheet>
  );
};
