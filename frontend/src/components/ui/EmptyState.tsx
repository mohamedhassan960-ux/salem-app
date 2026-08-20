import { DoctorAvatar } from './DoctorAvatar';
import { Surface } from './Surface';
import { Sparkles, MessageCircle, ShieldCheck, HeartPulse } from 'lucide-react';

export interface EmptyStateProps {
  onQuickPromptClick?: (prompt: string) => void;
  className?: string;
}

export const EmptyState = ({
  onQuickPromptClick,
  className = '',
}: EmptyStateProps) => {
  const quickPrompts = [
    {
      title: 'أعراض الانسحاب',
      text: 'إزاي أتعامل مع الصداع والعصبية في أول 3 أيام بدون تدخين؟',
      icon: HeartPulse,
    },
    {
      title: 'بدائل النيكوتين (NRT)',
      text: 'إيه جرعة اللصقات أو العلكة المناسبة لو بشرب علبة في اليوم؟',
      icon: ShieldCheck,
    },
    {
      title: 'خطة إقلاع متدرجة',
      text: 'عايز خطة عملية تساعدني أوقف تدخين تدريجياً خلال أسبوعين.',
      icon: MessageCircle,
    },
  ];

  return (
    <div
      className={`flex flex-col items-center justify-center text-center px-4 py-8 max-w-md mx-auto w-full select-none ${className}`}
      dir="rtl"
    >
      <div className="relative mb-5">
        <DoctorAvatar size="lg" showStatus={true} />
        <div className="absolute -top-1 -right-1 bg-sky-500/20 text-sky-400 p-1.5 rounded-full border border-sky-400/30">
          <Sparkles className="w-3.5 h-3.5" />
        </div>
      </div>

      <h2 className="text-xl font-bold text-white mb-2 font-arabic tracking-tight">
        أهلاً بيك! أنا دكتور سالم 👋
      </h2>
      <p className="text-sm text-slate-300 mb-6 leading-relaxed font-arabic px-2">
        مرشدك الطبي المتخصص للإقلاع عن التدخين، مستنداً إلى أحدث إرشادات منظمة الصحة العالمية (WHO Guideline 2024).
      </p>

      <div className="w-full flex flex-col gap-2.5 text-right">
        <span className="text-[11px] font-semibold text-sky-400 uppercase tracking-wider px-1">
          أسئلة شائعة يمكنك البدء بها:
        </span>
        {quickPrompts.map((item, idx) => {
          const Icon = item.icon;
          return (
            <button
              key={idx}
              type="button"
              onClick={() => onQuickPromptClick?.(item.text)}
              className="text-right transition-all duration-200 active:scale-[0.98] cursor-pointer group"
            >
              <Surface
                variant="card"
                padding="sm"
                rounded="lg"
                className="group-hover:border-sky-500/40 group-hover:bg-slate-800/80 transition-all flex items-start gap-3 border border-slate-800"
              >
                <div className="p-2 rounded-lg bg-sky-500/10 text-sky-400 shrink-0 mt-0.5 border border-sky-500/20">
                  <Icon className="w-4 h-4" />
                </div>
                <div className="flex-1">
                  <h3 className="text-xs font-bold text-slate-200 mb-0.5 font-arabic group-hover:text-sky-300 transition-colors">
                    {item.title}
                  </h3>
                  <p className="text-[12px] text-slate-400 leading-snug font-arabic line-clamp-2">
                    {item.text}
                  </p>
                </div>
              </Surface>
            </button>
          );
        })}
      </div>
    </div>
  );
};