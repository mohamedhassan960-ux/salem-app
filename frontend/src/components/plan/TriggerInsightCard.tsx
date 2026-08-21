import { Zap } from 'lucide-react';

export interface TriggerInsightCardProps {
  primaryTriggers: string[];
  cravingsManagedCount: number;
  onOpenRelapseModal?: () => void;
}

export const TriggerInsightCard = ({
  primaryTriggers,
  cravingsManagedCount,
  onOpenRelapseModal,
}: TriggerInsightCardProps) => {
  return (
    <div className="bg-[#FFFFFF] border border-[#D9E2F0] rounded-3xl p-5 sm:p-6 shadow-xs flex flex-col gap-4 font-arabic select-none" dir="rtl">
      <div className="flex items-center justify-between pb-3 border-b border-[#D9E2F0]">
        <div className="flex items-center gap-2">
          <Zap className="w-5 h-5 text-[#2D8BFF]" />
          <h3 className="text-base font-bold text-[#061A3A]">المحفزات السلوكية والتغلب على الرغبة</h3>
        </div>

        <span className="text-xs font-bold text-[#047857] bg-[#34D399]/15 px-3 py-1 rounded-full border border-[#34D399]/30">
          {cravingsManagedCount} نوبة تم تجاوزها
        </span>
      </div>

      <div className="flex flex-col gap-3">
        <div className="flex flex-col gap-2">
          <span className="text-xs font-semibold text-[#5F708C]">المواقف الأكثر تحفيزاً لرغبتك:</span>
          <div className="flex flex-wrap gap-2">
            {primaryTriggers.length > 0 ? (
              primaryTriggers.map((trig, i) => (
                <span
                  key={i}
                  className="px-3 py-1.5 rounded-2xl bg-[#F4F7FB] text-[#061A3A] border border-[#D9E2F0] text-xs font-medium"
                >
                  {trig}
                </span>
              ))
            ) : (
              <span className="text-xs text-[#8291A8]">لم يتم تسجيل محفزات محددة بعد</span>
            )}
          </div>
        </div>

        {onOpenRelapseModal && (
          <div className="mt-2 pt-3 border-t border-[#D9E2F0] flex items-center justify-between">
            <span className="text-xs text-[#5F708C]">حصلت كبوة أو دخنت سيجارة؟</span>
            <button
              type="button"
              onClick={onOpenRelapseModal}
              className="text-xs font-bold text-[#1E3A8A] hover:text-[#2D8BFF] cursor-pointer transition-colors"
            >
              تسجيل ومتابعة بدون لوم
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
