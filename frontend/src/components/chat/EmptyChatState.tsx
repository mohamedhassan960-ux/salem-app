import { DoctorAvatar } from '../ui/DoctorAvatar';
import { SuggestionChip } from './SuggestionChip';

export interface EmptyChatStateProps {
  onSelectSuggestion: (prompt: string) => void;
}

const SUGGESTIONS = [
  'إزاي أتعامل مع الصداع والعصبية في أول 3 أيام بدون تدخين؟',
  'إيه جرعة اللصقات (NRT) المناسبة لو بشرب علبة في اليوم؟',
  'عايز خطة تساعدني أوقف تدخين تدريجياً خلال أسبوعين.',
  'هل السجائر الإلكترونية وسيلة معتمدة طبياً للإقلاع؟',
];

export const EmptyChatState = ({ onSelectSuggestion }: EmptyChatStateProps) => {
  return (
    <div className="flex flex-col items-center text-center px-4 py-6 w-full max-w-sm mx-auto gap-6 select-none" dir="rtl">
      <div className="relative">
        <DoctorAvatar size="xl" showStatus />
      </div>

      <div className="flex flex-col gap-1.5">
        <h2 className="text-xl font-bold text-white tracking-tight">أهلاً بيك، أنا سالم</h2>
        <p className="text-xs text-slate-300 leading-relaxed max-w-[280px] mx-auto">
          استشارك الطبي للإقلاع عن التدخين. اسألني عن الأدوية، بدائل النيكوتين، أو الأعراض — وفق أدلة WHO 2024.
        </p>
      </div>

      <div className="w-full flex flex-col gap-2 text-right">
        {SUGGESTIONS.map((text, i) => (
          <SuggestionChip key={i} text={text} onClick={onSelectSuggestion} />
        ))}
      </div>
    </div>
  );
};
