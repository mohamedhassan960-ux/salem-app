import { DoctorAvatar } from '../ui/DoctorAvatar';
import { Flame, Menu, HeartPulse } from 'lucide-react';
import { useUserState } from '../../state/UserStateContext';

export interface TopHeaderProps {
  currentTab: 'chat' | 'plan' | 'history' | 'profile' | 'settings';
  onMenuToggle: () => void;
  onOpenCravingModal: () => void;
  className?: string;
}

const TAB_TITLES: Record<string, string> = {
  chat: 'المحادثة مع سالم',
  plan: 'خطتك الشخصية',
  history: 'سجل المحادثات',
  profile: 'الملف الصحي والتقدم',
  settings: 'الإعدادات والخصوصية',
};

export const TopHeader = ({
  currentTab,
  onMenuToggle,
  onOpenCravingModal,
  className = '',
}: TopHeaderProps) => {
  const { stats, smokingProfile } = useUserState();

  return (
    <header
      className={`w-full shrink-0 bg-[#FFFFFF] border-b border-[#D9E2F0] px-4 py-3 flex items-center justify-between z-30 font-arabic ${className}`}
      style={{ paddingTop: 'calc(0.75rem + var(--sat))' }}
      dir="rtl"
    >
      {/* Right side: Mobile Menu Button & Brand/Title */}
      <div className="flex items-center gap-3 min-w-0">
        <button
          type="button"
          onClick={onMenuToggle}
          aria-label="فتح القائمة الرئيسية"
          className="lg:hidden w-10 h-10 flex items-center justify-center rounded-xl text-[#061A3A] hover:bg-[#F4F7FB] border border-[#D9E2F0] transition-colors cursor-pointer"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2.5">
          <DoctorAvatar size="sm" showStatus={false} />
          <div className="flex flex-col">
            <h1 className="text-sm sm:text-base font-bold text-[#061A3A] truncate">
              {TAB_TITLES[currentTab] || 'سالم'}
            </h1>
            <span className="text-[11px] text-[#5F708C] hidden sm:inline">
              دعم مبني على إرشادات WHO 2024
            </span>
          </div>
        </div>
      </div>

      {/* Left side: Streak Badge & Emergency Craving Button */}
      <div className="flex items-center gap-2">
        {smokingProfile && (
          <div
            className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#F4F7FB] border border-[#D9E2F0] text-xs font-semibold text-[#061A3A]"
            title="مدة التوقف عن التدخين"
          >
            <Flame className="w-4 h-4 text-[#2D8BFF]" />
            <span>{stats.smokeFreeFormatted}</span>
          </div>
        )}

        <button
          type="button"
          onClick={onOpenCravingModal}
          className="h-9 px-3 rounded-xl bg-[#2D8BFF]/10 hover:bg-[#2D8BFF]/20 text-[#1E3A8A] border border-[#2D8BFF]/30 text-xs font-bold flex items-center gap-1.5 transition-all duration-150 active:scale-95 cursor-pointer"
        >
          <HeartPulse className="w-4 h-4 text-[#2D8BFF]" />
          <span>عندي رغبة الآن</span>
        </button>
      </div>
    </header>
  );
};
