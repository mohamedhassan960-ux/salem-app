import { MenuButton } from '../ui/MenuButton';
import { DoctorAvatar } from '../ui/DoctorAvatar';
import { BrandMark } from '../ui/BrandMark';

export interface MobileHeaderProps {
  onMenuClick?: () => void;
  isMenuOpen?: boolean;
  className?: string;
}

export const MobileHeader = ({
  onMenuClick,
  isMenuOpen = false,
  className = '',
}: MobileHeaderProps) => {
  return (
    <header
      className={`w-full shrink-0 bg-slate-900/95 backdrop-blur-md border-b border-slate-800/80 px-4 flex items-center justify-between z-30 ${className}`}
      style={{ paddingTop: 'calc(0.875rem + var(--sat))', paddingBottom: '0.875rem' }}
      dir="rtl"
    >
      <div className="flex items-center gap-3 min-w-0">
        <DoctorAvatar size="md" showStatus={true} />
        <BrandMark showSubtitle={true} />
      </div>
      <div className="shrink-0 ml-2">
        <MenuButton onClick={onMenuClick} isOpen={isMenuOpen} />
      </div>
    </header>
  );
};
