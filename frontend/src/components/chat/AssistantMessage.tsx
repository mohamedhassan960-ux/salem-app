import type { ChatMessage } from '../../types/chat';
import { DoctorAvatar } from '../ui/DoctorAvatar';
import { EvidenceSection } from './EvidenceSection';
import { ShieldCheck, AlertTriangle } from 'lucide-react';

export interface AssistantMessageProps {
  message: ChatMessage;
  showAvatar?: boolean;
}

export const AssistantMessage = ({ message, showAvatar = true }: AssistantMessageProps) => {
  const s = message.structured;

  return (
    <div className="w-full flex items-start gap-2.5 my-1.5" dir="rtl">
      {showAvatar ? (
        <DoctorAvatar size="sm" showStatus={false} className="mt-1 shrink-0" />
      ) : (
        <div className="w-9 shrink-0" />
      )}

      <div className="flex-1 min-w-0 rounded-2xl rounded-tr-sm bg-slate-900 border border-slate-800/80 p-4 shadow-sm">
        {/* Author */}
        <div className="flex items-center gap-1.5 mb-2.5 pb-2 border-b border-slate-800/60">
          <span className="text-xs font-bold text-sky-400">سالم</span>
          <span className="text-[10px] text-slate-400">· استشاري إقلاع عن التدخين</span>
        </div>

        {s ? (
          <div className="flex flex-col gap-2.5 text-sm text-slate-200 leading-relaxed">
            {s.paragraphs.map((p, i) => (
              <p key={i} className="whitespace-pre-wrap">{p}</p>
            ))}

            {s.bulletPoints && s.bulletPoints.length > 0 && (
              <ul className="flex flex-col gap-1.5 pr-1">
                {s.bulletPoints.map((pt, i) => (
                  <li key={i} className="flex items-start gap-2 text-slate-300">
                    <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-sky-500 shrink-0" />
                    <span>{pt}</span>
                  </li>
                ))}
              </ul>
            )}

            {s.keyTakeaway && (
              <div className="flex items-start gap-2 p-2.5 rounded-xl bg-sky-950/40 border border-sky-800/30 text-sky-200 text-xs">
                <ShieldCheck className="w-3.5 h-3.5 shrink-0 text-sky-400 mt-0.5" />
                <span><strong>الخلاصة:</strong> {s.keyTakeaway}</span>
              </div>
            )}

            {s.safetyNote && (
              <div className="flex items-start gap-2 p-2.5 rounded-xl bg-amber-950/25 border border-amber-800/30 text-amber-200 text-xs">
                <AlertTriangle className="w-3.5 h-3.5 shrink-0 text-amber-400 mt-0.5" />
                <span>{s.safetyNote}</span>
              </div>
            )}
          </div>
        ) : (
          <p className="text-sm text-slate-200 leading-relaxed whitespace-pre-wrap">{message.content}</p>
        )}

        {message.evidence && message.evidence.length > 0 && (
          <EvidenceSection evidence={message.evidence} />
        )}
      </div>
    </div>
  );
};
