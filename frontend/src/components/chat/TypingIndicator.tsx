import { DoctorAvatar } from '../ui/DoctorAvatar';

export interface TypingIndicatorProps {
  className?: string;
}

export const TypingIndicator = ({ className = '' }: TypingIndicatorProps) => {
  return (
    <div className={`flex items-center gap-2.5 my-2 font-arabic ${className}`} dir="rtl">
      <DoctorAvatar size="sm" showStatus={false} className="shrink-0" />
      <div className="bg-[#FFFFFF] border border-[#D9E2F0] px-4 py-3 rounded-2xl rounded-tr-xs shadow-xs flex items-center gap-1.5">
        <span className="w-2 h-2 rounded-full bg-[#2D8BFF] animate-bounce [animation-delay:-0.3s]" />
        <span className="w-2 h-2 rounded-full bg-[#2D8BFF] animate-bounce [animation-delay:-0.15s]" />
        <span className="w-2 h-2 rounded-full bg-[#2D8BFF] animate-bounce" />
        <span className="text-xs text-[#5F708C] mr-2">سالم يبحث في المصادر الطبية...</span>
      </div>
    </div>
  );
};
