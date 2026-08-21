import { Menu } from 'lucide-react';
import { IconButton } from './IconButton';

export interface MenuButtonProps {
  onClick?: () => void;
  isOpen?: boolean;
  className?: string;
}

export const MenuButton = ({
  onClick,
  isOpen = false,
  className = '',
}: MenuButtonProps) => {
  return (
    <IconButton
      aria-label={isOpen ? 'إغلاق القائمة' : 'فتح القائمة الرئيسية ومحادثات سابقة'}
      onClick={onClick}
      variant="default"
      size="md"
      className={`relative group ${className}`}
    >
      <Menu className={`w-5 h-5 transition-transform duration-200 ${isOpen ? 'rotate-90' : ''}`} />
    </IconButton>
  );
};
