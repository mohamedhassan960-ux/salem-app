import { Button } from '../ui/Button';
import { Surface } from '../ui/Surface';
import { LogOut, AlertTriangle } from 'lucide-react';

export interface LogoutDialogProps {
  isOpen: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export const LogoutDialog = ({
  isOpen,
  onConfirm,
  onCancel,
}: LogoutDialogProps) => {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs animate-in fade-in duration-200"
      dir="rtl"
      role="dialog"
      aria-modal="true"
      aria-labelledby="logout-title"
    >
      <Surface
        variant="elevated"
        padding="lg"
        rounded="2xl"
        className="w-full max-w-xs text-center border border-slate-700 bg-slate-900 shadow-2xl flex flex-col items-center gap-4"
      >
        <div className="w-12 h-12 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-center justify-center">
          <AlertTriangle className="w-6 h-6" />
        </div>

        <div className="flex flex-col gap-1.5">
          <h3 id="logout-title" className="text-base font-bold text-white font-arabic">
            هل تريد تسجيل الخروج؟
          </h3>
          <p className="text-xs text-slate-300 font-arabic leading-relaxed">
            سيتم إنهاء جلسة تسجيل الدخول الحالية والعودة لشاشة البدء.
          </p>
        </div>

        <div className="w-full flex items-center gap-2 mt-2">
          <Button
            variant="danger"
            size="md"
            fullWidth
            onClick={onConfirm}
            leftIcon={<LogOut className="w-4 h-4" />}
          >
            تسجيل الخروج
          </Button>
          <Button
            variant="secondary"
            size="md"
            fullWidth
            onClick={onCancel}
          >
            إلغاء
          </Button>
        </div>
      </Surface>
    </div>
  );
};
