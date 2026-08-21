import { Button } from '../ui/Button';
import { Target, ArrowLeft, Wind } from 'lucide-react';

export interface NextActionCardProps {
  title?: string;
  description?: string;
  actionLabel?: string;
  actionType?: 'craving' | 'chat' | 'breathing';
  onActionClick: () => void;
}

export const NextActionCard = ({
  title = 'تمرين التنفس وتجديد التركيز',
  description = 'تمرين بسيط لمدة دقيقة واحدة يساعد على خفض التوتر واستقرار الجهاز العصبي.',
  actionLabel = 'ابدأ التمرين الآن',
  actionType = 'breathing',
  onActionClick,
}: NextActionCardProps) => {
  return (
    <div className="bg-[#FFFFFF] border border-[#D9E2F0] rounded-3xl p-5 sm:p-6 shadow-xs flex flex-col gap-4 font-arabic select-none" dir="rtl">
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold text-[#1E3A8A] bg-[#2D8BFF]/10 px-3 py-1 rounded-full border border-[#2D8BFF]/20">
          الخطوة التالية الموصى بها
        </span>

        <div className="w-8 h-8 rounded-xl bg-[#2D8BFF]/10 text-[#2D8BFF] flex items-center justify-center">
          {actionType === 'breathing' ? (
            <Wind className="w-4 h-4" />
          ) : (
            <Target className="w-4 h-4" />
          )}
        </div>
      </div>

      <div className="flex flex-col gap-1">
        <h3 className="text-base sm:text-lg font-extrabold text-[#061A3A]">{title}</h3>
        <p className="text-xs sm:text-sm text-[#5F708C] leading-relaxed">{description}</p>
      </div>

      <div className="pt-1">
        <Button
          variant="primary"
          size="lg"
          fullWidth
          onClick={onActionClick}
          leftIcon={<ArrowLeft className="w-4 h-4" />}
        >
          {actionLabel}
        </Button>
      </div>
    </div>
  );
};
