import type { ReactNode } from 'react';
import { MobileHeader } from './MobileHeader';

export interface AppShellProps {
  children: ReactNode;
  onMenuClick?: () => void;
  isMenuOpen?: boolean;
  showHeader?: boolean;
}

export const AppShell = ({
  children,
  onMenuClick,
  isMenuOpen = false,
  showHeader = true,
}: AppShellProps) => {
  return (
    <div className="w-full h-[100dvh] flex justify-center bg-slate-950 overflow-hidden">
      <div className="w-full max-w-[440px] h-full flex flex-col bg-slate-900 shadow-2xl relative border-x border-slate-800/60 overflow-hidden">
        {showHeader && (
          <MobileHeader onMenuClick={onMenuClick} isMenuOpen={isMenuOpen} />
        )}
        <main className="flex-1 w-full overflow-y-auto overflow-x-hidden flex flex-col min-h-0">
          {children}
        </main>
      </div>
    </div>
  );
};
