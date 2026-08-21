import { useUserState } from '../../state/UserStateContext';
import { Flame, DollarSign, ShieldCheck, Heart } from 'lucide-react';

export const ProgressCard = () => {
  const { stats, smokingProfile } = useUserState();

  if (!smokingProfile) {
    return (
      <div className="bg-[#FFFFFF] border border-[#D9E2F0] rounded-3xl p-6 shadow-xs font-arabic" dir="rtl">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-[#2D8BFF]/10 text-[#2D8BFF] flex items-center justify-center">
            <Flame className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-base font-bold text-[#061A3A]">رحلتك تبدأ اليوم</h3>
            <p className="text-xs text-[#5F708C] mt-0.5">أول هدف: إتمام أول 24 ساعة بدون تدخين</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-[#FFFFFF] border border-[#D9E2F0] rounded-3xl p-6 shadow-xs font-arabic flex flex-col gap-5" dir="rtl">
      {/* Top Banner */}
      <div className="flex items-center justify-between pb-4 border-b border-[#D9E2F0]">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-[#2D8BFF]/10 text-[#2D8BFF] flex items-center justify-center shrink-0">
            <Flame className="w-6 h-6" />
          </div>
          <div>
            <span className="text-xs text-[#5F708C] font-medium">التقدم الحالي</span>
            <h2 className="text-xl sm:text-2xl font-extrabold text-[#061A3A] tracking-tight">
              {stats.smokeFreeFormatted}
            </h2>
          </div>
        </div>

        <span className="px-3 py-1 rounded-full bg-[#34D399]/15 text-[#047857] border border-[#34D399]/30 text-xs font-bold">
          مستمر بنجاح
        </span>
      </div>

      {/* 3 Metric Cards */}
      <div className="grid grid-cols-3 gap-2.5 sm:gap-4">
        {/* Cigarettes Avoided */}
        <div className="p-3 sm:p-4 rounded-2xl bg-[#F4F7FB] border border-[#D9E2F0] flex flex-col gap-1">
          <div className="flex items-center gap-1.5 text-xs text-[#5F708C]">
            <Heart className="w-3.5 h-3.5 text-[#F87171]" />
            <span className="truncate">سجائر تم تجنبها</span>
          </div>
          <span className="text-lg sm:text-xl font-black text-[#061A3A]">
            {stats.cigarettesAvoided}
          </span>
          <span className="text-[10px] text-[#8291A8]">سيجارة أقل</span>
        </div>

        {/* Money Saved */}
        <div className="p-3 sm:p-4 rounded-2xl bg-[#F4F7FB] border border-[#D9E2F0] flex flex-col gap-1">
          <div className="flex items-center gap-1.5 text-xs text-[#5F708C]">
            <DollarSign className="w-3.5 h-3.5 text-[#34D399]" />
            <span className="truncate">توفير مالي تقريبي</span>
          </div>
          <span className="text-lg sm:text-xl font-black text-[#061A3A]">
            {stats.moneySavedEGP}
          </span>
          <span className="text-[10px] text-[#8291A8]">جنيه مصري</span>
        </div>

        {/* Cravings Managed */}
        <div className="p-3 sm:p-4 rounded-2xl bg-[#F4F7FB] border border-[#D9E2F0] flex flex-col gap-1">
          <div className="flex items-center gap-1.5 text-xs text-[#5F708C]">
            <ShieldCheck className="w-3.5 h-3.5 text-[#2D8BFF]" />
            <span className="truncate">رغبات تم تجاوزها</span>
          </div>
          <span className="text-lg sm:text-xl font-black text-[#061A3A]">
            {stats.cravingsManagedCount}
          </span>
          <span className="text-[10px] text-[#8291A8]">نوبة مسجلة</span>
        </div>
      </div>
    </div>
  );
};
