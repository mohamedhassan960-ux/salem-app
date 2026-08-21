import { Button } from '../ui/Button';
import { CheckCircle2, ArrowRight } from 'lucide-react';

export interface InterventionCompletionProps {
  intensityBefore: number;
  intensityAfter: number;
  onFinish: () => void;
}

export const InterventionCompletion = ({
  intensityBefore,
  intensityAfter,
  onFinish,
}: InterventionCompletionProps) => {
  return (
    <div className="flex flex-col items-center text-center gap-6 py-4 font-arabic select-none" dir="rtl">
      {/* Calm Success Icon */}
      <div className="w-16 h-16 rounded-full bg-[#34D399]/15 text-[#047857] flex items-center justify-center">
        <CheckCircle2 className="w-8 h-8" />
      </div>

      <div className="flex flex-col gap-1.5 max-w-sm">
        <h3 className="text-xl font-extrabold text-[#061A3A] tracking-tight">
          عدّينا اللحظة دي مع بعض.
        </h3>
        <p className="text-xs text-[#5F708C] leading-relaxed">
          كل مرة بتأجل فيها السيجارة وتتغلب على الرغبة، عقلك وجسمك بيتعلموا مسارات عصبية جديدة للتحرر.
        </p>
      </div>

      {/* Before / After subtle indicator */}
      <div className="w-full max-w-xs p-4 rounded-2xl bg-[#F4F7FB] border border-[#D9E2F0] flex items-center justify-between">
        <div className="flex flex-col items-center">
          <span className="text-[11px] text-[#5F708C]">قبل التدخل</span>
          <span className="text-base font-black text-[#061A3A]">{intensityBefore} / 10</span>
        </div>

        <ArrowRight className="w-4 h-4 text-[#8291A8] transform rotate-180" />

        <div className="flex flex-col items-center">
          <span className="text-[11px] text-[#047857] font-semibold">بعد التدخل</span>
          <span className="text-base font-black text-[#047857]">{intensityAfter} / 10</span>
        </div>
      </div>

      <div className="w-full max-w-xs flex flex-col gap-2">
        <Button variant="primary" size="lg" fullWidth onClick={onFinish}>
          العودة للمحادثة مع سالم
        </Button>
      </div>
    </div>
  );
};
