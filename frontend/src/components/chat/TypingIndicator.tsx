import { DoctorAvatar } from '../ui/DoctorAvatar';

export interface TypingIndicatorProps {
  className?: string;
}

export const TypingIndicator = ({ className = '' }: TypingIndicatorProps) => {
  return (
    <div className={`flex items-start gap-3 w-full animate-in fade-in duration-200 ${className}`} dir="rtl">
      <DoctorAvatar size="sm" showStatus={false} className="mt-1" />
      <div className="bg-slate-900 border border-slate-800 text-slate-200 rounded-2xl rounded-tr-sm px-4 py-3.5 flex items-center gap-1.5 shadow-sm shadow-slate-950/40">
        <span className="w-2 h-2 rounded-full bg-sky-400 animate-bounce [animation-delay:-0.3s]" />
        <span className="w-2 h-2 rounded-full bg-sky-400 animate-bounce [animation-delay:-0.15s]" />
        <span className="w-2 h-2 rounded-full bg-sky-400 animate-bounce" />
      </div>
    </div>
  );
};
