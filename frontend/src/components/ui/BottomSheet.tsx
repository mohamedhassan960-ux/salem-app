import { useEffect, type ReactNode } from 'react';
import { X } from 'lucide-react';

export interface BottomSheetProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  subtitle?: string;
  children: ReactNode;
}

export const BottomSheet = ({
  isOpen,
  onClose,
  title,
  subtitle,
  children,
}: BottomSheetProps) => {
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

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-[#061A3A]/50 backdrop-blur-xs font-arabic animate-in fade-in duration-200"
      dir="rtl"
      role="dialog"
      aria-modal="true"
    >
      {/* Backdrop */}
      <div className="absolute inset-0" onClick={onClose} aria-hidden="true" />

      {/* Sheet Container */}
      <div
        className="
          relative w-full max-w-lg bg-[#FFFFFF] border-t border-[#D9E2F0] rounded-t-3xl shadow-2xl
          flex flex-col max-h-[85vh] z-10 animate-in slide-in-from-bottom duration-250
        "
        style={{ paddingBottom: 'calc(1rem + var(--sab))' }}
      >
        {/* Handle bar */}
        <div className="w-full flex justify-center pt-3 pb-1">
          <div className="w-12 h-1.5 rounded-full bg-[#D9E2F0]" />
        </div>

        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3 border-b border-[#D9E2F0]">
          <div className="flex flex-col">
            {title && <h3 className="text-base font-bold text-[#061A3A]">{title}</h3>}
            {subtitle && <p className="text-xs text-[#5F708C] mt-0.5">{subtitle}</p>}
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="إغلاق اللوحة"
            className="w-9 h-9 flex items-center justify-center rounded-xl text-[#8291A8] hover:text-[#061A3A] hover:bg-[#F4F7FB] transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body content */}
        <div className="flex-1 overflow-y-auto p-5">{children}</div>
      </div>
    </div>
  );
};
