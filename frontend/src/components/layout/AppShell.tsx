import type { ReactNode } from 'react';
import { TopHeader } from './TopHeader';
import { Sidebar } from './Sidebar';

export interface AppShellProps {
  children: ReactNode;
  currentTab: 'chat' | 'plan' | 'history' | 'profile' | 'settings' | 'marketing';
  onSelectTab: (tab: 'chat' | 'plan' | 'history' | 'profile' | 'settings' | 'marketing') => void;
  isSidebarOpen: boolean;
  onSidebarToggle: () => void;
  onSidebarClose: () => void;
  onNewConversation: () => void;
  onOpenLogout: () => void;
  onOpenCravingModal: () => void;
}

export const AppShell = ({
  children,
  currentTab,
  onSelectTab,
  isSidebarOpen,
  onSidebarToggle,
  onSidebarClose,
  onNewConversation,
  onOpenLogout,
  onOpenCravingModal,
}: AppShellProps) => {
  return (
    <div className="w-full h-[100dvh] flex bg-[#F7F9FC] text-[#061A3A] overflow-hidden font-arabic" dir="rtl">
      {/* Sidebar (Desktop persistent + Mobile slide-over) */}
      <Sidebar
        isOpen={isSidebarOpen}
        onClose={onSidebarClose}
        currentTab={currentTab}
        onSelectTab={onSelectTab}
        onNewConversation={onNewConversation}
        onOpenLogout={onOpenLogout}
      />

      {/* Main Content Viewport */}
      <div className="flex-1 h-full flex flex-col min-w-0 bg-[#F7F9FC] relative overflow-hidden">
        <TopHeader
          currentTab={currentTab === 'marketing' ? 'chat' : currentTab}
          onMenuToggle={onSidebarToggle}
          onOpenCravingModal={onOpenCravingModal}
        />
        <main className="flex-1 w-full overflow-hidden flex flex-col min-h-0 bg-[#F7F9FC]">
          {children}
        </main>
      </div>
    </div>
  );
};
