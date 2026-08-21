import { useEffect } from 'react';
import { BrandMark } from '../ui/BrandMark';
import { DoctorAvatar } from '../ui/DoctorAvatar';
import {
  MessageSquare,
  CalendarCheck,
  History,
  User,
  Settings,
  Plus,
  X,
  LogOut,
  Flame,
  Sparkles,
} from 'lucide-react';
import { useUserState } from '../../state/UserStateContext';

export interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  currentTab: 'chat' | 'plan' | 'history' | 'profile' | 'settings' | 'marketing';
  onSelectTab: (tab: 'chat' | 'plan' | 'history' | 'profile' | 'settings' | 'marketing') => void;
  onNewConversation: () => void;
  onOpenLogout: () => void;
}

export const Sidebar = ({
  isOpen,
  onClose,
  currentTab,
  onSelectTab,
  onNewConversation,
  onOpenLogout,
}: SidebarProps) => {
  const { stats, smokingProfile } = useUserState();

  // Escape key for mobile drawer
  useEffect(() => {
    if (!isOpen) return;
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  const navItems = [
    { id: 'chat', label: 'المحادثة مع سالم', icon: MessageSquare },
    { id: 'plan', label: 'خطتي الشخصية', icon: CalendarCheck },
    { id: 'history', label: 'سجل المحادثات', icon: History },
    { id: 'profile', label: 'الملف الصحي والتقدم', icon: User },
    { id: 'settings', label: 'الإعدادات والخصوصية', icon: Settings },
  ] as const;

  const sidebarContent = (
    <div className="h-full flex flex-col justify-between bg-[#FFFFFF] border-l border-[#D9E2F0] p-4 font-arabic select-none" dir="rtl">
      {/* Top Header & Brand */}
      <div className="flex flex-col gap-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <DoctorAvatar size="md" showStatus={true} />
            <BrandMark showSubtitle={false} theme="light" />
          </div>

          {/* Close button on mobile */}
          <button
            type="button"
            onClick={onClose}
            aria-label="إغلاق القائمة"
            className="lg:hidden w-8 h-8 flex items-center justify-center rounded-xl text-[#8291A8] hover:text-[#061A3A] hover:bg-[#F4F7FB] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* New Conversation Button */}
        <button
          type="button"
          onClick={() => {
            onNewConversation();
            onSelectTab('chat');
            onClose();
          }}
          className="w-full h-11 px-4 rounded-xl bg-[#2D8BFF] hover:bg-[#1E7AE6] active:bg-[#1569CC] text-white font-semibold text-xs sm:text-sm flex items-center justify-center gap-2 shadow-sm transition-all duration-150 active:scale-[0.98] cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>محادثة جديدة</span>
        </button>

        {/* Streak Mini Card */}
        {smokingProfile && (
          <div className="p-3.5 rounded-2xl bg-[#F4F7FB] border border-[#D9E2F0] flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-[#2D8BFF]/10 flex items-center justify-center text-[#2D8BFF]">
                <Flame className="w-4 h-4" />
              </div>
              <div className="flex flex-col">
                <span className="text-[11px] text-[#5F708C]">بدون تدخين</span>
                <span className="text-xs font-bold text-[#061A3A]">{stats.smokeFreeFormatted}</span>
              </div>
            </div>
          </div>
        )}

        {/* Navigation items */}
        <nav className="flex flex-col gap-1 mt-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => {
                  onSelectTab(item.id);
                  onClose();
                }}
                className={`
                  w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition-all duration-150 cursor-pointer
                  ${
                    isActive
                      ? 'bg-[#2D8BFF]/10 text-[#1E3A8A] border border-[#2D8BFF]/25 shadow-xs'
                      : 'text-[#5F708C] hover:text-[#061A3A] hover:bg-[#F4F7FB] border border-transparent'
                  }
                `}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-[#2D8BFF]' : 'text-[#8291A8]'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer Items */}
      <div className="flex flex-col gap-2 pt-3 border-t border-[#D9E2F0]">
        {/* Toggle Marketing Page Preview */}
        <button
          type="button"
          onClick={() => {
            onSelectTab('marketing');
            onClose();
          }}
          className="w-full flex items-center gap-2.5 px-3.5 py-2 rounded-xl text-xs text-[#5F708C] hover:text-[#061A3A] hover:bg-[#F4F7FB] transition-colors cursor-pointer"
        >
          <Sparkles className="w-4 h-4 text-[#2D8BFF]" />
          <span>الموقع التعريفي لسالم</span>
        </button>

        {/* Logout */}
        <button
          type="button"
          onClick={onOpenLogout}
          className="w-full flex items-center gap-2.5 px-3.5 py-2 rounded-xl text-xs text-[#F87171] hover:bg-[#F87171]/10 font-semibold transition-colors cursor-pointer"
        >
          <LogOut className="w-4 h-4" />
          <span>تسجيل الخروج</span>
        </button>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Persistent Sidebar (>=1024px) */}
      <aside className="hidden lg:block w-72 shrink-0 h-full">
        {sidebarContent}
      </aside>

      {/* Mobile Drawer (<1024px) */}
      {isOpen && (
        <div className="lg:hidden fixed inset-0 z-40 bg-[#061A3A]/50 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="absolute inset-0" onClick={onClose} aria-hidden="true" />
          <div
            className="absolute top-0 right-0 h-full w-[82%] max-w-[320px] bg-[#FFFFFF] shadow-2xl z-50 animate-in slide-in-from-right duration-250"
            style={{ paddingTop: 'var(--sat)', paddingBottom: 'var(--sab)' }}
          >
            {sidebarContent}
          </div>
        </div>
      )}
    </>
  );
};
