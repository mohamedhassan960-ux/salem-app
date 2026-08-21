import { useState } from 'react';
import type { ChatMessage } from '../../types/chat';
import { DoctorAvatar } from '../ui/DoctorAvatar';
import { SourceSheet } from './SourceSheet';
import { BookOpen, ShieldCheck, AlertTriangle } from 'lucide-react';

export interface AssistantMessageProps {
  message: ChatMessage;
  showAvatar?: boolean;
}

export const AssistantMessage = ({
  message,
  showAvatar = true,
}: AssistantMessageProps) => {
  const [isSourceSheetOpen, setIsSourceSheetOpen] = useState(false);
  const s = message.structured;
  const hasEvidence = message.evidence && message.evidence.length > 0;

  return (
    <div className="w-full flex items-start gap-2.5 my-2 font-arabic" dir="rtl">
      {showAvatar ? (
        <DoctorAvatar size="sm" showStatus={false} className="mt-1 shrink-0" />
      ) : (
        <div className="w-8 shrink-0" />
      )}

      <div className="flex-1 max-w-[85%] sm:max-w-[80%] rounded-2xl rounded-tr-xs bg-[#FFFFFF] border border-[#D9E2F0] p-4 sm:p-5 shadow-xs flex flex-col gap-3">
        {/* Header author */}
        <div className="flex items-center justify-between pb-2 border-b border-[#D9E2F0]">
          <div className="flex items-center gap-1.5">
            <span className="text-xs font-bold text-[#061A3A]">سالم</span>
            <span className="text-[11px] text-[#5F708C]">· مساعدك للإقلاع</span>
          </div>

          {hasEvidence && (
            <button
              type="button"
              onClick={() => setIsSourceSheetOpen(true)}
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-[#2D8BFF]/10 text-[#1E3A8A] hover:bg-[#2D8BFF]/20 text-[11px] font-semibold transition-colors cursor-pointer"
            >
              <BookOpen className="w-3 h-3 text-[#2D8BFF]" />
              <span>المصادر ({message.evidence?.length})</span>
            </button>
          )}
        </div>

        {/* Content */}
        {s ? (
          <div className="flex flex-col gap-2.5 text-sm text-[#061A3A] leading-relaxed">
            {s.paragraphs.map((p, i) => (
              <p key={i} className="whitespace-pre-wrap">{p}</p>
            ))}

            {s.bulletPoints && s.bulletPoints.length > 0 && (
              <ul className="flex flex-col gap-2 pr-1 my-1">
                {s.bulletPoints.map((pt, i) => (
                  <li key={i} className="flex items-start gap-2 text-xs sm:text-sm text-[#061A3A]">
                    <span className="mt-2 w-1.5 h-1.5 rounded-full bg-[#2D8BFF] shrink-0" />
                    <span>{pt}</span>
                  </li>
                ))}
              </ul>
            )}

            {s.keyTakeaway && (
              <div className="flex items-start gap-2 p-3 rounded-xl bg-[#2D8BFF]/5 border border-[#2D8BFF]/20 text-xs text-[#061A3A]">
                <ShieldCheck className="w-4 h-4 shrink-0 text-[#2D8BFF] mt-0.5" />
                <span>
                  <strong>الخلاصة: </strong>
                  {s.keyTakeaway}
                </span>
              </div>
            )}

            {s.safetyNote && (
              <div className="flex items-start gap-2 p-3 rounded-xl bg-[#FBBF24]/10 border border-[#FBBF24]/30 text-xs text-[#061A3A]">
                <AlertTriangle className="w-4 h-4 shrink-0 text-[#B45309] mt-0.5" />
                <span>{s.safetyNote}</span>
              </div>
            )}
          </div>
        ) : (
          <div className="text-sm text-[#061A3A] leading-relaxed whitespace-pre-wrap">
            {message.content}
          </div>
        )}

        {/* Grounded Evidence Trigger Button if present */}
        {hasEvidence && (
          <div className="pt-2 border-t border-[#D9E2F0] flex items-center justify-between">
            <button
              type="button"
              onClick={() => setIsSourceSheetOpen(true)}
              className="text-[11px] text-[#2D8BFF] hover:text-[#1E3A8A] font-semibold flex items-center gap-1 transition-colors cursor-pointer"
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>مدعوم بأدلة منظمة الصحة العالمية (WHO 2024)</span>
            </button>
          </div>
        )}
      </div>

      {/* Sources BottomSheet */}
      {hasEvidence && message.evidence && (
        <SourceSheet
          isOpen={isSourceSheetOpen}
          onClose={() => setIsSourceSheetOpen(false)}
          sources={message.evidence}
        />
      )}
    </div>
  );
};
