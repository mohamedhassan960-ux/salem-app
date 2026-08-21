import { Sparkles, ArrowLeft } from 'lucide-react';
import { Button } from '../ui/Button';

export interface RecommendationCardProps {
  title?: string;
  rationale?: string;
  actionLabel?: string;
  onActionClick?: () => void;
}

export const RecommendationCard = ({
  title = 'التعامل مع محفزات القهوة والروتين الصباحي',
  rationale = 'إذا كانت القهوة الصباحية مرتبطة ارتباطًا شرطيًا بالتدخين، فإن تغيير مكان الجلوس أو استبدالها بمشروب بديل لبضعة أيام يكسر هذا الرابط العصبي.',
  actionLabel = 'استشر سالم عن كسر الروابط الشرطية',
  onActionClick,
}: RecommendationCardProps) => {
  return (
    <div className="bg-[#FFFFFF] border border-[#D9E2F0] rounded-3xl p-5 sm:p-6 shadow-xs flex flex-col gap-4 font-arabic select-none" dir="rtl">
      <div className="flex items-center gap-2">
        <Sparkles className="w-5 h-5 text-[#2D8BFF]" />
        <h3 className="text-base font-bold text-[#061A3A]">سالم يقترح عليك</h3>
      </div>

      <div className="p-4 rounded-2xl bg-[#2D8BFF]/5 border border-[#2D8BFF]/20 flex flex-col gap-2">
        <h4 className="text-xs sm:text-sm font-bold text-[#1E3A8A]">{title}</h4>
        <p className="text-xs text-[#061A3A] leading-relaxed">{rationale}</p>
      </div>

      {onActionClick && (
        <div className="pt-1">
          <Button
            variant="secondary"
            size="md"
            fullWidth
            onClick={onActionClick}
            leftIcon={<ArrowLeft className="w-4 h-4" />}
          >
            {actionLabel}
          </Button>
        </div>
      )}
    </div>
  );
};
