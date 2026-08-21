import { Calendar, Flame, ShieldCheck, Banknote } from 'lucide-react';

export interface PlanHeroProps {
  smokeFreeDays: number;
  smokeFreeHours: number;
  cigarettesAvoided: number;
  moneySavedEGP: number;
  quitStartDate: number;
  status?: string;
  onOpenCravingModal?: () => void;
}

export const PlanHero = ({
  smokeFreeDays,
  smokeFreeHours,
  cigarettesAvoided,
  moneySavedEGP,
  quitStartDate,
  status = 'active',
  onOpenCravingModal,
}: PlanHeroProps) => {
  const formattedStartDate = new Date(quitStartDate).toLocaleDateString('ar-EG', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <div className="bg-[#FFFFFF] border border-[#D9E2F0] rounded-3xl p-6 sm:p-7 shadow-xs flex flex-col gap-6 font-arabic select-none" dir="rtl">
      {/* Top Header Badge & Start Date */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-[#34D399] animate-pulse" />
          <span className="text-xs font-bold text-[#061A3A]">
            {status === 'active' ? 'أنت في رحلتك ومستمر' : 'الرحلة قيد المتابعة'}
          </span>
        </div>

        <div className="flex items-center gap-1.5 text-xs text-[#5F708C]">
          <Calendar className="w-3.5 h-3.5" />
          <span>بدأت في {formattedStartDate}</span>
        </div>
      </div>

      {/* Large Hero Metric (Where am I?) */}
      <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-2 pb-2">
        <div className="flex items-baseline gap-3">
          <span className="text-4xl sm:text-5xl font-black text-[#061A3A] tracking-tight">
            {smokeFreeDays}
          </span>
          <div className="flex flex-col">
            <span className="text-base sm:text-lg font-bold text-[#061A3A]">
              يوم بدون تدخين
            </span>
            <span className="text-xs text-[#5F708C]">
              {smokeFreeHours} ساعة متواصلة من التعافي
            </span>
          </div>
        </div>

        {onOpenCravingModal && (
          <button
            type="button"
            onClick={onOpenCravingModal}
            className="px-4 py-2.5 rounded-2xl bg-[#F4F7FB] hover:bg-[#E8EFF8] border border-[#D9E2F0] text-[#1E3A8A] text-xs font-bold flex items-center gap-2 transition-colors cursor-pointer self-start sm:self-auto"
          >
            <Flame className="w-4 h-4 text-[#2D8BFF]" />
            <span>عندي رغبة الآن</span>
          </button>
        )}
      </div>

      {/* Primary Key Achievements */}
      <div className="grid grid-cols-2 gap-3 pt-3 border-t border-[#D9E2F0]">
        <div className="p-3.5 rounded-2xl bg-[#F4F7FB] border border-[#D9E2F0] flex flex-col gap-1">
          <div className="flex items-center gap-1.5 text-[#5F708C] text-xs">
            <ShieldCheck className="w-4 h-4 text-[#2D8BFF]" />
            <span>سجائر تم تجنبها</span>
          </div>
          <span className="text-xl font-black text-[#061A3A]">{cigarettesAvoided}</span>
          <span className="text-[10px] text-[#8291A8]">سيجارة لم تدخل رئتيك</span>
        </div>

        <div className="p-3.5 rounded-2xl bg-[#F4F7FB] border border-[#D9E2F0] flex flex-col gap-1">
          <div className="flex items-center gap-1.5 text-[#5F708C] text-xs">
            <Banknote className="w-4 h-4 text-[#34D399]" />
            <span>توفير مالي تقريبي</span>
          </div>
          <span className="text-xl font-black text-[#061A3A]">{moneySavedEGP} ج.م</span>
          <span className="text-[10px] text-[#8291A8]">تم استثمارها في صحتك</span>
        </div>
      </div>
    </div>
  );
};
