import { useEffect } from 'react';
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react';

export interface ToastProps {
  message: string;
  type?: 'success' | 'error' | 'info';
  isOpen: boolean;
  onClose: () => void;
  durationMs?: number;
}

export const Toast = ({
  message,
  type = 'success',
  isOpen,
  onClose,
  durationMs = 3000,
}: ToastProps) => {
  useEffect(() => {
    if (!isOpen) return;
    const timer = setTimeout(() => {
      onClose();
    }, durationMs);
    return () => clearTimeout(timer);
  }, [isOpen, durationMs, onClose]);

  if (!isOpen) return null;

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle2 className="w-4 h-4 text-[#34D399] shrink-0" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-[#F87171] shrink-0" />;
      default:
        return <Info className="w-4 h-4 text-[#2D8BFF] shrink-0" />;
    }
  };

  const getBg = () => {
    switch (type) {
      case 'success':
        return 'bg-[#FFFFFF] border-[#34D399]/30 text-[#061A3A] shadow-md';
      case 'error':
        return 'bg-[#FFFFFF] border-[#F87171]/30 text-[#061A3A] shadow-md';
      default:
        return 'bg-[#FFFFFF] border-[#2D8BFF]/30 text-[#061A3A] shadow-md';
    }
  };

  return (
    <div
      className="fixed bottom-6 left-1/2 transform -translate-x-1/2 z-50 animate-in fade-in slide-in-from-bottom-2 duration-200"
      dir="rtl"
      role="status"
      aria-live="polite"
    >
      <div
        className={`flex items-center gap-2.5 px-4 py-3 rounded-2xl border font-arabic text-xs font-semibold select-none ${getBg()}`}
      >
        {getIcon()}
        <span>{message}</span>
        <button
          type="button"
          onClick={onClose}
          aria-label="إغلاق الإشعار"
          className="mr-2 text-[#8291A8] hover:text-[#061A3A] transition-colors cursor-pointer"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
