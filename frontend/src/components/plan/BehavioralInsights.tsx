import { useUserState } from '../../state/UserStateContext';
import { Lightbulb, TrendingUp, AlertCircle } from 'lucide-react';

export const BehavioralInsights = () => {
  const { insights, cravings } = useUserState();

  // If there isn't enough real craving data (minimum 2 logged cravings), do not show fake charts
  if (insights.length === 0) {
    return (
      <div className="bg-[#FFFFFF] border border-[#D9E2F0] rounded-3xl p-6 shadow-xs font-arabic flex flex-col gap-3" dir="rtl">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-[#2D8BFF]/10 text-[#2D8BFF] flex items-center justify-center">
            <Lightbulb className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-base font-bold text-[#061A3A]">التحليلات السلوكية والمحفزات</h3>
            <p className="text-xs text-[#5F708C]">تبدأ التحليلات بالظهور تلقائيًا بعد تسجيل نوبات الرغبة</p>
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-[#F4F7FB] border border-[#D9E2F0] text-xs text-[#5F708C] leading-relaxed flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-[#8291A8] shrink-0" />
          <span>
            {cravings.length === 0
              ? 'لم تسجل أي نوبات رغبة بعد. اضغط "عندي رغبة الآن" في أي وقت تواجه فيه رغبة بالتدخين لنساعدك ونحلل محفزاتك.'
              : 'تم تسجيل نوبة واحدة. سجل نوبة أخرى للبدء في اكتشاف نمط المحفزات الشخصي.'}
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-[#FFFFFF] border border-[#D9E2F0] rounded-3xl p-6 shadow-xs font-arabic flex flex-col gap-4" dir="rtl">
      <div className="flex items-center gap-2.5 pb-3 border-b border-[#D9E2F0]">
        <div className="w-9 h-9 rounded-xl bg-[#2D8BFF]/10 text-[#2D8BFF] flex items-center justify-center">
          <TrendingUp className="w-4 h-4" />
        </div>
        <div>
          <h3 className="text-base font-bold text-[#061A3A]">تحليلات سلوكك ومحفزاتك</h3>
          <p className="text-xs text-[#5F708C]">مستخلصة من مواقف الرغبة المسجلة فعليًا</p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {insights.map((insight) => (
          <div
            key={insight.id}
            className="p-4 rounded-2xl bg-[#F4F7FB] border border-[#D9E2F0] flex flex-col gap-2"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-[#061A3A]">{insight.title}</span>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-[#2D8BFF]/10 text-[#1E3A8A] font-extrabold border border-[#2D8BFF]/25">
                {insight.highlight}
              </span>
            </div>
            <p className="text-xs text-[#5F708C] leading-relaxed">{insight.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
