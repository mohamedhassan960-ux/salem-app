import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { LogOut } from 'lucide-react';

export interface LogoutDialogProps {
  isOpen: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export const LogoutDialog = ({ isOpen, onConfirm, onCancel }: LogoutDialogProps) => {
  return (
    <Modal
      isOpen={isOpen}
      onClose={onCancel}
      title="تسجيل الخروج"
      subtitle="هل أنت متأكد من رغبتك في تسجيل الخروج من سالم؟"
      maxWidth="sm"
    >
      <div className="flex flex-col gap-4 font-arabic" dir="rtl">
        <p className="text-xs sm:text-sm text-[#5F708C] leading-relaxed">
          ستظل بيانات رحلتك ومحادثاتك محفوظة بأمان، ويمكنك العودة في أي وقت بمجرد تسجيل الدخول.
        </p>

        <div className="flex gap-2.5 pt-2">
          <Button
            variant="danger"
            fullWidth
            onClick={onConfirm}
            leftIcon={<LogOut className="w-4 h-4" />}
          >
            تأكيد الخروج
          </Button>
          <Button variant="secondary" fullWidth onClick={onCancel}>
            إلغاء
          </Button>
        </div>
      </div>
    </Modal>
  );
};
