import { useEffect } from 'react';
import type { ConversationSession } from '../../types/chat';
import { DoctorAvatar } from '../ui/DoctorAvatar';
import { BrandMark } from '../ui/BrandMark';
import { ConversationItem } from './ConversationItem';
import { Plus, X, Settings, LogOut, MessageSquareDashed } from 'lucide-react';

export interface SidebarDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  conversations: ConversationSession[];
  activeConversationId: string | null;
  onSelectConversation: (c: ConversationSession) => void;
  onNewConversation: () => void;
  onOpenSettings: () => void;
  onOpenLogoutDialog: () => void;
}

export const SidebarDrawer = ({
  isOpen,
  onClose,
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onOpenSettings,
  onOpenLogoutDialog,
}: SidebarDrawerProps) => {
  // Escape key to close
  useEffect(() => {
    if (!isOpen) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [isOpen, onClose]);

  const groups = [
    { label: 'اليوم', items: conversations.filter((c) => c.group === 'اليوم') },
    { label: 'أمس', items: conversations.filter((c) => c.group === 'أمس') },
    { label: 'هذا الأسبوع', items: conversations.filter((c) => c.group === 'هذا الأسبوع') },
  ].filter((g) => g.items.length > 0);

  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-[2px]"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Drawer panel — slides from RIGHT (RTL) */}
      <div
        className={`fixed top-0 right-0 h-full z-50 w-[82%] max-w-[340px] bg-slate-900 border-l border-slate-800/80 shadow-2xl flex flex-col transition-transform duration-250 ease-out ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
        role="dialog"
        aria-modal="true"
        aria-label="القائمة الجانبية"
        style={{ paddingTop: 'var(--sat)', paddingBottom: 'var(--sab)' }}
        dir="rtl"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800/80">
          <div className="flex items-center gap-2.5">
            <DoctorAvatar size="sm" showStatus={false} />
            <BrandMark showSubtitle={false} />
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="إغلاق القائمة"
            className="w-9 h-9 flex items-center justify-center rounded-xl text-slate-400 hover:text-white hover:bg-slate-800/60 transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* New conversation */}
        <div className="px-3 py-2.5 border-b border-slate-800/60">
          <button
            type="button"
            onClick={onNewConversation}
            className="w-full h-10 px-3 rounded-xl bg-sky-500/10 hover:bg-sky-500/20 text-sky-400 font-bold text-xs border border-sky-500/25 flex items-center justify-center gap-2 transition-colors cursor-pointer active:scale-[0.98]"
          >
            <Plus className="w-4 h-4" />
            <span>محادثة جديدة</span>
          </button>
        </div>

        {/* Conversation list */}
        <div className="flex-1 overflow-y-auto px-2 py-3 flex flex-col gap-4 min-h-0">
          {groups.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center text-center text-slate-500 gap-2 py-8">
              <MessageSquareDashed className="w-8 h-8 text-slate-700" />
              <p className="text-xs">لا توجد محادثات بعد</p>
            </div>
          ) : (
            groups.map((g) => (
              <div key={g.label} className="flex flex-col gap-0.5">
                <span className="text-[10px] font-bold text-slate-500 px-2 mb-1 tracking-wider uppercase">
                  {g.label}
                </span>
                {g.items.map((conv) => (
                  <ConversationItem
                    key={conv.id}
                    conversation={conv}
                    isActive={conv.id === activeConversationId}
                    onClick={onSelectConversation}
                  />
                ))}
              </div>
            ))
          )}
        </div>

        {/* Footer actions */}
        <div className="border-t border-slate-800/80 px-2 py-2 flex flex-col gap-0.5">
          <button
            type="button"
            onClick={onOpenSettings}
            className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-slate-300 hover:text-white hover:bg-slate-800/60 text-xs font-medium transition-colors cursor-pointer"
          >
            <Settings className="w-4 h-4 text-slate-500" />
            <span>الإعدادات</span>
          </button>
          <button
            type="button"
            onClick={onOpenLogoutDialog}
            className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 text-xs font-medium transition-colors cursor-pointer"
          >
            <LogOut className="w-4 h-4" />
            <span>تسجيل الخروج</span>
          </button>
        </div>
      </div>
    </>
  );
};
