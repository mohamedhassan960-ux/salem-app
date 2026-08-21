import { useAuth } from '../../context/AuthContext';
import { useUserState } from '../../state/UserStateContext';
import { User, Flame, Cigarette, Target, Calendar, ShieldCheck, Settings } from 'lucide-react';

export interface ProfileScreenProps {
  onOpenSettings: () => void;
}

export const ProfileScreen = ({ onOpenSettings }: ProfileScreenProps) => {
  const { user } = useAuth();
  const { smokingProfile, stats } = useUserState();

  const getTobaccoName = (type?: string) => {
    switch (type) {
      case 'cigarettes':
        return 'سجائر عادية';
      case 'shisha':
        return 'شيشة / معسل';
      case 'vape':
        return 'سجائر إلكترونية (فيب)';
      case 'heated_tobacco':
        return 'تبغ مسخن';
      default:
        return 'تبغ تقليدي';
    }
  };

  const joinDateFormatted = user?.createdAt
    ? new Date(user.createdAt).toLocaleDateString('ar-EG', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    : 'اليوم';

  return (
    <div className="w-full h-full overflow-y-auto p-4 sm:p-6 font-arabic select-none bg-[#F7F9FC]" dir="rtl">
      <div className="max-w-3xl mx-auto flex flex-col gap-6 pb-8">
        {/* Header Profile Card */}
        <div className="bg-[#FFFFFF] border border-[#D9E2F0] rounded-3xl p-6 shadow-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-3xl bg-gradient-to-br from-[#1E3A8A] to-[#2D8BFF] text-white font-black text-xl flex items-center justify-center border border-[#D9E2F0] shadow-xs shrink-0">
              {user?.name ? user.name.slice(0, 1) : <User className="w-8 h-8" />}
            </div>

            <div className="flex flex-col">
              <h2 className="text-lg sm:text-xl font-black text-[#061A3A]">{user?.name || 'مستخدم سالم'}</h2>
              <span className="text-xs text-[#5F708C] mt-0.5">{user?.email || 'user@salem.app'}</span>
              <div className="flex items-center gap-1.5 text-[11px] text-[#8291A8] mt-1.5">
                <Calendar className="w-3.5 h-3.5" />
                <span>بداية الرحلة: {joinDateFormatted}</span>
              </div>
            </div>
          </div>

          <button
            type="button"
            onClick={onOpenSettings}
            className="px-3.5 py-2 rounded-xl bg-[#F4F7FB] hover:bg-[#E8EFF8] text-[#1E3A8A] text-xs font-bold border border-[#D9E2F0] flex items-center gap-1.5 transition-colors cursor-pointer self-stretch sm:self-auto justify-center"
          >
            <Settings className="w-4 h-4" />
            <span>تعديل الملف والإعدادات</span>
          </button>
        </div>

        {/* Live Journey Progress Summary */}
        <div className="bg-[#FFFFFF] border border-[#D9E2F0] rounded-3xl p-6 shadow-xs flex flex-col gap-4">
          <div className="flex items-center gap-2 pb-3 border-b border-[#D9E2F0]">
            <Flame className="w-5 h-5 text-[#2D8BFF]" />
            <h3 className="text-base font-bold text-[#061A3A]">إنجازات رحلة التعافي</h3>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3.5 rounded-2xl bg-[#F4F7FB] border border-[#D9E2F0] flex flex-col gap-1">
              <span className="text-xs text-[#5F708C]">أيام بدون تدخين</span>
              <span className="text-xl font-black text-[#061A3A]">{stats.smokeFreeDays}</span>
              <span className="text-[10px] text-[#8291A8]">{stats.smokeFreeHours} ساعة إجمالية</span>
            </div>

            <div className="p-3.5 rounded-2xl bg-[#F4F7FB] border border-[#D9E2F0] flex flex-col gap-1">
              <span className="text-xs text-[#5F708C]">سجائر تم تجنبها</span>
              <span className="text-xl font-black text-[#061A3A]">{stats.cigarettesAvoided}</span>
              <span className="text-[10px] text-[#8291A8]">سيجارة أقل في الرئتين</span>
            </div>

            <div className="p-3.5 rounded-2xl bg-[#F4F7FB] border border-[#D9E2F0] flex flex-col gap-1">
              <span className="text-xs text-[#5F708C]">توفير مالي تقريبي</span>
              <span className="text-xl font-black text-[#061A3A]">{stats.moneySavedEGP}</span>
              <span className="text-[10px] text-[#8291A8]">جنيه مصري</span>
            </div>

            <div className="p-3.5 rounded-2xl bg-[#F4F7FB] border border-[#D9E2F0] flex flex-col gap-1">
              <span className="text-xs text-[#5F708C]">نوبات تم تجاوزها</span>
              <span className="text-xl font-black text-[#061A3A]">{stats.cravingsManagedCount}</span>
              <span className="text-[10px] text-[#8291A8]">تغلب ناجح</span>
            </div>
          </div>
        </div>

        {/* Smoking Profile Summary */}
        {smokingProfile && (
          <div className="bg-[#FFFFFF] border border-[#D9E2F0] rounded-3xl p-6 shadow-xs flex flex-col gap-4">
            <div className="flex items-center gap-2 pb-3 border-b border-[#D9E2F0]">
              <Cigarette className="w-5 h-5 text-[#2D8BFF]" />
              <h3 className="text-base font-bold text-[#061A3A]">بيانات نمط التدخين المسجلة</h3>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex items-start gap-3 p-3.5 rounded-2xl bg-[#F4F7FB] border border-[#D9E2F0]">
                <Cigarette className="w-4 h-4 text-[#1E3A8A] mt-0.5" />
                <div className="flex flex-col">
                  <span className="text-xs text-[#5F708C]">نوع التبغ والمعدل</span>
                  <span className="text-xs font-bold text-[#061A3A] mt-0.5">
                    {getTobaccoName(smokingProfile.tobaccoType)} · حوالي {smokingProfile.dailyCigarettes} يوميًا
                  </span>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3.5 rounded-2xl bg-[#F4F7FB] border border-[#D9E2F0]">
                <Target className="w-4 h-4 text-[#1E3A8A] mt-0.5" />
                <div className="flex flex-col">
                  <span className="text-xs text-[#5F708C]">الهدف الأساسي</span>
                  <span className="text-xs font-bold text-[#061A3A] mt-0.5">
                    {smokingProfile.quitGoal}
                  </span>
                </div>
              </div>
            </div>

            {smokingProfile.primaryTriggers.length > 0 && (
              <div className="flex flex-col gap-2 pt-2 border-t border-[#D9E2F0]">
                <span className="text-xs font-bold text-[#061A3A]">المحفزات المسجلة:</span>
                <div className="flex flex-wrap gap-2">
                  {smokingProfile.primaryTriggers.map((trig, i) => (
                    <span
                      key={i}
                      className="px-3 py-1 rounded-full bg-[#2D8BFF]/10 text-[#1E3A8A] border border-[#2D8BFF]/20 text-xs font-semibold"
                    >
                      {trig}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Clinical Footnote */}
        <div className="p-4 rounded-2xl bg-[#FFFFFF] border border-[#D9E2F0] flex items-center gap-3 text-xs text-[#5F708C]">
          <ShieldCheck className="w-5 h-5 text-[#34D399] shrink-0" />
          <span>
            جميع حسابات التعافي والتوصيات مبنية على معايير منظمة الصحة العالمية (WHO 2024).
          </span>
        </div>
      </div>
    </div>
  );
};
