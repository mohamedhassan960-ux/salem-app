import { HeartPulse, Sparkles, Compass, ShieldAlert } from 'lucide-react';

export interface EmptyChatStateProps {
  onSelectSuggestion: (prompt: string) => void;
  onOpenCravingModal?: () => void;
}

export const EmptyChatState = ({
  onSelectSuggestion,
  onOpenCravingModal,
}: EmptyChatStateProps) => {
  const suggestions = [
    {
      title: 'عندي رغبة في التدخين دلوقتي',
      desc: 'تدخل سريع وتمرين يساعدك تتجاوز اللحظة',
      icon: HeartPulse,
      isSpecial: true,
      onClick: onOpenCravingModal,
    },
    {
      title: 'خطة اليوم للإقلاع',
      desc: 'إيه الخطوات والتوصيات المعتمدة لليوم؟',
      icon: Compass,
      prompt: 'إيه أهم الخطوات والتوصيات لخطتي اليومية للإقلاع؟',
    },
    {
      title: 'عايز أفهم اللي بيحصل لجسمي',
      desc: 'أعراض الانسحاب وكيف يتعافى الجسم وفق WHO',
      icon: Sparkles,
      prompt: 'عايز أفهم التغيرات الإيجابية وأعراض الانسحاب اللي همر بيها وإزاي أتعامل معاها.',
    },
    {
      title: 'حاسس إني ممكن أضعف',
      desc: 'دعم سلوكي ومراجعة الدوافع بدون أي لوم',
      icon: ShieldAlert,
      prompt: 'حاسس بضغط وتوتر وخايف أضعف، محتاج دعم يساعدني أثبت على قراري.',
    },
  ];

  return (
    <div
      className="w-full max-w-lg mx-auto flex flex-col items-center text-center px-4 py-8 gap-6 font-arabic select-none"
      dir="rtl"
    >
      <div className="relative">
        <div className="w-20 h-20 rounded-3xl p-1 bg-gradient-to-b from-[#2D8BFF] via-[#1E3A8A] to-[#0B2454] border border-[#D9E2F0] shadow-md flex items-center justify-center">
          <img
            src="/salem-logo.png"
            alt="سالم"
            className="w-full h-full object-cover rounded-2xl"
            onError={(e) => {
              const t = e.currentTarget;
              t.onerror = null;
              t.src = '/logo.png';
            }}
          />
        </div>
      </div>

      <div className="flex flex-col gap-1.5 max-w-sm">
        <h2 className="text-xl sm:text-2xl font-bold text-[#061A3A] tracking-tight">
          أهلًا بيك، أنا سالم.
        </h2>
        <p className="text-sm text-[#5F708C] leading-relaxed">
          خلينا نبدأ من مكانك أنت، ونمشي خطوة بخطوة.
        </p>
      </div>

      {/* Suggestion cards */}
      <div className="w-full flex flex-col gap-2.5 text-right mt-2">
        {suggestions.map((item, i) => {
          const Icon = item.icon;
          return (
            <button
              key={i}
              type="button"
              onClick={() => {
                if (item.isSpecial && item.onClick) {
                  item.onClick();
                } else if (item.prompt) {
                  onSelectSuggestion(item.prompt);
                }
              }}
              className={`
                p-4 rounded-2xl border text-right transition-all duration-150 cursor-pointer flex items-center justify-between gap-3 shadow-xs
                ${
                  item.isSpecial
                    ? 'bg-[#2D8BFF]/5 border-[#2D8BFF]/30 hover:bg-[#2D8BFF]/10 text-[#1E3A8A]'
                    : 'bg-[#FFFFFF] border-[#D9E2F0] hover:border-[#C4D1E3] hover:bg-[#F4F7FB] text-[#061A3A]'
                }
              `}
            >
              <div className="flex items-center gap-3">
                <div
                  className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 ${
                    item.isSpecial
                      ? 'bg-[#2D8BFF]/15 text-[#2D8BFF]'
                      : 'bg-[#F1F5FA] text-[#1E3A8A]'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                </div>
                <div className="flex flex-col">
                  <span className="text-xs sm:text-sm font-bold text-[#061A3A]">
                    {item.title}
                  </span>
                  <span className="text-[11px] text-[#5F708C] mt-0.5">{item.desc}</span>
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
