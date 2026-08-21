import { useState } from 'react';
import { Button } from '../ui/Button';
import { IntensitySelector } from './IntensitySelector';
import { TrendingDown, Minus, TrendingUp } from 'lucide-react';

export interface InterventionCheckInProps {
  intensityBefore: number;
  onSubmit: (intensityAfter: number, outcome: 'lower' | 'same' | 'higher') => void;
}

export const InterventionCheckIn = ({
  intensityBefore,
  onSubmit,
}: InterventionCheckInProps) => {
  const [outcome, setOutcome] = useState<'lower' | 'same' | 'higher'>('lower');
  const [intensityAfter, setIntensityAfter] = useState<number>(Math.max(1, intensityBefore - 3));

  const handleOutcomeSelect = (selectedOutcome: 'lower' | 'same' | 'higher') => {
    setOutcome(selectedOutcome);
    if (selectedOutcome === 'lower') {
      setIntensityAfter(Math.max(1, intensityBefore - 3));
    } else if (selectedOutcome === 'same') {
      setIntensityAfter(intensityBefore);
    } else {
      setIntensityAfter(Math.min(10, intensityBefore + 1));
    }
  };

  const handleFinish = () => {
    onSubmit(intensityAfter, outcome);
  };

  return (
    <div className="flex flex-col gap-6 py-2 font-arabic select-none" dir="rtl">
      <div className="flex flex-col gap-1 text-center">
        <h3 className="text-base font-bold text-[#061A3A]">
          الرغبة عاملة إيه دلوقتي؟
        </h3>
        <p className="text-xs text-[#5F708C]">
          سالم بيسجل استجابتك لتطوير خطتك ومساعدتك في المرات القادمة
        </p>
      </div>

      {/* 3 Outcome Pill Options */}
      <div className="grid grid-cols-3 gap-2.5">
        {[
          {
            id: 'lower',
            title: 'خفّت كتير',
            desc: 'أقل من الأول',
            icon: TrendingDown,
            activeColor: 'border-[#34D399] bg-[#34D399]/10 text-[#047857]',
          },
          {
            id: 'same',
            title: 'زي ما هي',
            desc: 'ثابتة ومتحكم',
            icon: Minus,
            activeColor: 'border-[#2D8BFF] bg-[#2D8BFF]/10 text-[#1E3A8A]',
          },
          {
            id: 'higher',
            title: 'ما زالت قوية',
            desc: 'محتاج دعم إضافي',
            icon: TrendingUp,
            activeColor: 'border-[#FBBF24] bg-[#FBBF24]/15 text-[#B45309]',
          },
        ].map((item) => {
          const Icon = item.icon;
          const isSelected = outcome === item.id;
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => handleOutcomeSelect(item.id as any)}
              className={`
                min-h-[52px] p-3 rounded-2xl border text-center flex flex-col items-center justify-center gap-1.5 transition-all duration-150 cursor-pointer
                ${
                  isSelected
                    ? `${item.activeColor} ring-2 ring-current font-bold`
                    : 'bg-[#F4F7FB] border-[#D9E2F0] text-[#061A3A] hover:border-[#C4D1E3]'
                }
              `}
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span className="text-xs font-bold">{item.title}</span>
            </button>
          );
        })}
      </div>

      {/* Numerical Intensity After */}
      <IntensitySelector
        label="تقدير شدة الرغبة الآن بعد التدخل:"
        value={intensityAfter}
        onChange={setIntensityAfter}
      />

      <div className="pt-2">
        <Button variant="primary" size="lg" fullWidth onClick={handleFinish}>
          تسجيل النتيجة ومتابعة الخطة
        </Button>
      </div>
    </div>
  );
};
