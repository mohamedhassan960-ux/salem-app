import { AlertTriangle, PhoneCall } from 'lucide-react';

export interface SafetyBannerProps {
  message?: string;
  emergencyNumber?: string;
  className?: string;
}

export const SafetyBanner = ({
  message = 'إذا كنت تعاني من آلام حادة في الصدر، ضيق تنفس شديد، أو حالة طوارئ طبية، يرجى طلب الرعاية الطبية الفورية.',
  emergencyNumber = '123',
  className = '',
}: SafetyBannerProps) => {
  return (
    <div
      className={`p-4 rounded-2xl bg-[#FBBF24]/10 border border-[#FBBF24]/30 text-[#061A3A] font-arabic flex flex-col gap-2.5 ${className}`}
      dir="rtl"
      role="alert"
    >
      <div className="flex items-start gap-2.5">
        <div className="w-8 h-8 rounded-xl bg-[#FBBF24]/20 text-[#B45309] flex items-center justify-center shrink-0 mt-0.5">
          <AlertTriangle className="w-4 h-4" />
        </div>
        <div className="flex-1">
          <h4 className="text-xs font-bold text-[#B45309]">تنبيه السلامة الطبية</h4>
          <p className="text-xs text-[#061A3A] leading-relaxed mt-0.5">{message}</p>
        </div>
      </div>

      <div className="flex items-center justify-between pt-2 border-t border-[#FBBF24]/20">
        <span className="text-[11px] text-[#5F708C]">طوارئ الإسعاف المباشرة:</span>
        <a
          href={`tel:${emergencyNumber}`}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#061A3A] text-white text-xs font-bold hover:bg-[#0B2454] transition-colors"
        >
          <PhoneCall className="w-3.5 h-3.5" />
          <span>الاتصال بالإسعاف ({emergencyNumber})</span>
        </a>
      </div>
    </div>
  );
};
