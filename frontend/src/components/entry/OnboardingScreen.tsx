import { useState } from 'react';
import { Button } from '../ui/Button';
import { ShieldCheck, MessageSquareHeart, Lock } from 'lucide-react';

export interface OnboardingScreenProps {
  onComplete: () => void;
}

const slides = [
  {
    id: 'intro',
    badge: 'رفيقك الصحي',
    title: 'أهلاً بيك! أنا سالم',
    body: 'طبيبك واستشارك للإقلاع عن التدخين. هكون معاك في كل خطوة علشان تبدأ حياة صحية جديدة بدون أي ضغط أو قلق.',
    Icon: MessageSquareHeart,
    iconColor: 'text-sky-400',
  },
  {
    id: 'evidence',
    badge: 'دليل WHO 2024',
    title: 'نصائح طبية مبنية على الأدلة',
    body: 'كل خطة وجرعة بدائل نيكوتين بنحددها مستندة لأحدث بروتوكولات منظمة الصحة العالمية المعتمدة.',
    Icon: ShieldCheck,
    iconColor: 'text-emerald-400',
  },
  {
    id: 'privacy',
    badge: 'أمان وسرية تامة',
    title: 'مساحتك الآمنة والخاصة',
    body: 'استفساراتك وتفاصيل رحلتك في سرية تامة. اسأل في أي وقت عن أي أعراض أو محفزات بتواجهها.',
    Icon: Lock,
    iconColor: 'text-indigo-400',
  },
];

export const OnboardingScreen = ({ onComplete }: OnboardingScreenProps) => {
  const [index, setIndex] = useState(0);
  const slide = slides[index];
  const isLast = index === slides.length - 1;

  return (
    <div
      className="w-full h-[100dvh] flex flex-col justify-between bg-slate-950 text-white select-none"
      style={{ paddingTop: 'var(--sat)', paddingBottom: 'var(--sab)' }}
      dir="rtl"
    >
      {/* Top bar */}
      <div className="flex items-center justify-between px-6 pt-4 pb-2 shrink-0">
        <div className="flex items-center gap-1.5">
          {slides.map((_, i) => (
            <div
              key={i}
              className={`h-1.5 rounded-full transition-all duration-300 ${
                i === index
                  ? 'w-7 bg-sky-400 shadow-sm shadow-sky-500/50'
                  : i < index
                  ? 'w-2.5 bg-sky-800'
                  : 'w-2 bg-slate-800'
              }`}
            />
          ))}
        </div>
        {!isLast && (
          <button
            type="button"
            onClick={onComplete}
            className="text-xs font-semibold text-slate-400 hover:text-white px-3 py-1.5 rounded-lg hover:bg-slate-900 transition-colors cursor-pointer"
          >
            تخطي
          </button>
        )}
      </div>

      {/* Hero Illustration (Salem Logo) */}
      <div className="flex-1 flex flex-col items-center justify-center text-center px-6 gap-5">
        <div className="relative">
          <div className="absolute -inset-4 rounded-3xl bg-sky-500/20 blur-2xl animate-pulse-subtle" />
          <div className="relative w-36 h-36 rounded-3xl p-1.5 bg-gradient-to-b from-sky-400/80 via-blue-600/60 to-slate-900 border border-sky-400/40 shadow-2xl shadow-sky-950/80 overflow-hidden flex items-center justify-center">
            <img
              src="/logo.png"
              alt="سالم"
              className="w-full h-full object-cover rounded-2xl"
            />
          </div>
        </div>

        <div className="flex flex-col items-center gap-2 max-w-[320px]">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-sky-500/15 text-sky-300 border border-sky-500/25">
            <slide.Icon className={`w-3.5 h-3.5 ${slide.iconColor}`} />
            {slide.badge}
          </span>
          <h2 className="text-2xl font-extrabold text-white tracking-tight">{slide.title}</h2>
          <p className="text-sm text-slate-300 leading-relaxed">{slide.body}</p>
        </div>
      </div>

      {/* Actions */}
      <div className="px-6 pb-6 flex flex-col gap-2 shrink-0">
        <Button
          variant="primary"
          size="lg"
          fullWidth
          onClick={() => (isLast ? onComplete() : setIndex((i) => i + 1))}
        >
          {isLast ? 'ابدأ محادثتك مع سالم' : 'التالي'}
        </Button>
        {index > 0 && (
          <Button variant="ghost" size="sm" fullWidth onClick={() => setIndex((i) => i - 1)}>
            السابق
          </Button>
        )}
      </div>
    </div>
  );
};
