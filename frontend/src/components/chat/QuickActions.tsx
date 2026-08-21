import { useUserState } from '../../state/UserStateContext';
import { Sparkles, HeartPulse } from 'lucide-react';

export interface QuickActionsProps {
  onSelectAction: (text: string) => void;
  onOpenCravingModal?: () => void;
  onOpenRelapseModal?: () => void;
  className?: string;
}

export const QuickActions = ({
  onSelectAction,
  onOpenCravingModal,
  onOpenRelapseModal,
  className = '',
}: QuickActionsProps) => {
  const { userState } = useUserState();

  // State-adaptive action sets
  const getActions = () => {
    switch (userState) {
      case 'craving_period':
        return [
          { label: 'ساعدني أتجاوز الرغبة الآن', isSpecial: true, onClick: onOpenCravingModal },
          { label: 'ابدأ تمرين التنفس السريع', text: 'عايز أبدأ تمرين تنفس يساعدني أهدى.' },
          { label: 'إيه اللي حفزني للتدخين دلوقتي؟', text: 'عايز أفهم إيه السبب اللي خلاني أحس بالرغبة دلوقتي.' },
        ];
      case 'relapse':
        return [
          { label: 'ساعدني أفهم اللي حصل', text: 'دخنت سيجارة وعايز أفهم إيه اللي حصل وأتعامل إزاي بدون إحباط.' },
          { label: 'تسجيل الموقف وإعادة الخطة', isSpecial: true, onClick: onOpenRelapseModal },
          { label: 'أكمل الخطة من جديد', text: 'أنا مستعد أكمل الخطة من النقطة دي.' },
        ];
      default:
        return [
          { label: 'خطة اليوم', text: 'إيه أهم خطوات وتوصيات خطتي لليوم؟' },
          { label: 'عندي رغبة في التدخين', isSpecial: true, onClick: onOpenCravingModal },
          { label: 'عايز أفهم اللي بيحصل لجسمي', text: 'إيه التغيرات الإيجابية اللي بتحصل لجسمي بعد التوقف؟' },
          { label: 'حاسس إني هضعف', text: 'حاسس بتوتر وخايف أضعف وأرجع للتدخين.' },
        ];
    }
  };

  const actions = getActions();

  return (
    <div className={`w-full flex items-center gap-2 overflow-x-auto py-2 px-1 scrollbar-none font-arabic ${className}`} dir="rtl">
      {actions.map((act, i) => {
        if (act.isSpecial && act.onClick) {
          return (
            <button
              key={i}
              type="button"
              onClick={act.onClick}
              className="shrink-0 flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-[#2D8BFF]/10 hover:bg-[#2D8BFF]/20 text-[#1E3A8A] border border-[#2D8BFF]/30 text-xs font-bold transition-all duration-150 active:scale-95 cursor-pointer"
            >
              <HeartPulse className="w-3.5 h-3.5 text-[#2D8BFF]" />
              <span>{act.label}</span>
            </button>
          );
        }

        return (
          <button
            key={i}
            type="button"
            onClick={() => act.text && onSelectAction(act.text)}
            className="shrink-0 flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-[#FFFFFF] hover:bg-[#F4F7FB] text-[#061A3A] border border-[#D9E2F0] hover:border-[#C4D1E3] text-xs font-semibold transition-all duration-150 active:scale-95 shadow-xs cursor-pointer"
          >
            <Sparkles className="w-3.5 h-3.5 text-[#2D8BFF]" />
            <span>{act.label}</span>
          </button>
        );
      })}
    </div>
  );
};
