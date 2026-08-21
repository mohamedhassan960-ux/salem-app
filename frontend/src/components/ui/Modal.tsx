import { useEffect, type ReactNode } from 'react';
import { X } from 'lucide-react';

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  subtitle?: string;
  children: ReactNode;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl';
  showCloseButton?: boolean;
}

export const Modal = ({
  isOpen,
  onClose,
  title,
  subtitle,
  children,
  maxWidth = 'md',
  showCloseButton = true,
}: ModalProps) => {
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    document.body.style.overflow = 'hidden';

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const maxWidthClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#061A3A]/60 backdrop-blur-xs font-arabic animate-in fade-in duration-200"
      dir="rtl"
      role="dialog"
      aria-modal="true"
    >
      {/* Backdrop */}
      <div className="absolute inset-0" onClick={onClose} aria-hidden="true" />

      {/* Content card */}
      <div
        className={`
          relative w-full ${maxWidthClasses[maxWidth]} bg-[#FFFFFF] border border-[#D9E2F0] rounded-2xl shadow-xl
          flex flex-col max-h-[88vh] overflow-hidden z-10 animate-in zoom-in-95 duration-200
        `}
      >
        {(title || showCloseButton) && (
          <div className="flex items-center justify-between px-5 py-4 border-b border-[#D9E2F0]">
            <div className="flex flex-col">
              {title && <h3 className="text-base font-bold text-[#061A3A]">{title}</h3>}
              {subtitle && <p className="text-xs text-[#5F708C] mt-0.5">{subtitle}</p>}
            </div>
            {showCloseButton && (
              <button
                type="button"
                onClick={onClose}
                aria-label="إغلاق النافذة"
                className="w-9 h-9 flex items-center justify-center rounded-xl text-[#8291A8] hover:text-[#061A3A] hover:bg-[#F4F7FB] transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>
        )}

        <div className="flex-1 overflow-y-auto p-5">{children}</div>
      </div>
    </div>
  );
};
