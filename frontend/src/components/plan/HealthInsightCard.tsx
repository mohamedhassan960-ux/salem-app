import type { HealthRecoveryInsight } from '../../types/plan';
import { HeartPulse, ShieldCheck } from 'lucide-react';

export interface HealthInsightCardProps {
  insights: HealthRecoveryInsight[];
}

export const HealthInsightCard = ({ insights }: HealthInsightCardProps) => {
  return (
    <div className="bg-[#FFFFFF] border border-[#D9E2F0] rounded-3xl p-5 sm:p-6 shadow-xs flex flex-col gap-4 font-arabic select-none" dir="rtl">
      <div className="flex items-center justify-between pb-3 border-b border-[#D9E2F0]">
        <div className="flex items-center gap-2">
          <HeartPulse className="w-5 h-5 text-[#2D8BFF]" />
          <h3 className="text-base font-bold text-[#061A3A]">التغيرات الصحية والتعافي الفسيولوجي</h3>
        </div>

        <span className="text-[11px] text-[#5F708C]">إرشادات WHO 2024</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {insights.map((item) => (
          <div
            key={item.id}
            className={`
              p-4 rounded-2xl border flex flex-col justify-between gap-2.5 transition-all
              ${
                item.isUnlocked
                  ? 'bg-[#F4F7FB] border-[#D9E2F0]'
                  : 'bg-[#FFFFFF] border-dashed border-[#D9E2F0] opacity-75'
              }
            `}
          >
            <div className="flex flex-col gap-1">
              <span className="text-[11px] font-bold text-[#2D8BFF]">{item.timeframeLabel}</span>
              <h4 className="text-xs sm:text-sm font-bold text-[#061A3A]">{item.title}</h4>
              <p className="text-xs text-[#5F708C] leading-relaxed mt-0.5">{item.explanation}</p>
            </div>

            <div className="flex items-center gap-1 text-[10px] text-[#8291A8] pt-1">
              <ShieldCheck className="w-3 h-3 text-[#34D399]" />
              <span>{item.isUnlocked ? 'مكتمل / نشط' : 'قيد التعافي المستمر'}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
