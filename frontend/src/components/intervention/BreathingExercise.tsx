import { useState, useEffect } from 'react';
import { Button } from '../ui/Button';
import { Wind, Play, Pause, RotateCcw } from 'lucide-react';

export interface BreathingExerciseProps {
  onComplete: () => void;
}

type Phase = 'inhale' | 'hold' | 'exhale' | 'ready';

export const BreathingExercise = ({ onComplete }: BreathingExerciseProps) => {
  const [phase, setPhase] = useState<Phase>('ready');
  const [secondsLeft, setSecondsLeft] = useState<number>(4);
  const [cyclesCompleted, setCyclesCompleted] = useState<number>(0);
  const [isActive, setIsActive] = useState<boolean>(false);

  const totalCycles = 3;

  useEffect(() => {
    if (!isActive || phase === 'ready') return;

    const timer = setInterval(() => {
      setSecondsLeft((prev) => {
        if (prev > 1) return prev - 1;

        // Transition to next phase
        if (phase === 'inhale') {
          setPhase('hold');
          return 7;
        } else if (phase === 'hold') {
          setPhase('exhale');
          return 8;
        } else if (phase === 'exhale') {
          const nextCycle = cyclesCompleted + 1;
          setCyclesCompleted(nextCycle);
          if (nextCycle >= totalCycles) {
            setIsActive(false);
            setPhase('ready');
            onComplete();
            return 4;
          } else {
            setPhase('inhale');
            return 4;
          }
        }
        return 4;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [isActive, phase, cyclesCompleted, onComplete]);

  const handleStart = () => {
    setIsActive(true);
    setPhase('inhale');
    setSecondsLeft(4);
    setCyclesCompleted(0);
  };

  const handleReset = () => {
    setIsActive(false);
    setPhase('ready');
    setSecondsLeft(4);
    setCyclesCompleted(0);
  };

  const getPhaseText = () => {
    switch (phase) {
      case 'inhale':
        return 'شـهـيـق عـمـيـق (4 ثوانٍ)';
      case 'hold':
        return 'احـبـس أنـفـاسـك (7 ثوانٍ)';
      case 'exhale':
        return 'زفـيـر بـطـيء (8 ثوانٍ)';
      default:
        return 'تمرين التنفس 4-7-8 لتهدئة الرغبة';
    }
  };

  const getCircleScale = () => {
    if (phase === 'inhale') return 'scale-125 duration-[4000ms]';
    if (phase === 'hold') return 'scale-125 duration-0';
    if (phase === 'exhale') return 'scale-90 duration-[8000ms]';
    return 'scale-100 duration-300';
  };

  return (
    <div className="flex flex-col items-center text-center gap-6 py-4 font-arabic" dir="rtl">
      {/* Animated breathing circle */}
      <div className="relative w-48 h-48 flex items-center justify-center">
        <div
          className={`
            absolute inset-0 rounded-full bg-[#2D8BFF]/10 border-2 border-[#2D8BFF]/30
            transition-transform ease-in-out ${getCircleScale()}
          `}
        />
        <div className="relative z-10 flex flex-col items-center justify-center">
          <Wind className="w-8 h-8 text-[#2D8BFF] mb-1" />
          <span className="text-3xl font-black text-[#061A3A]">{secondsLeft}</span>
          <span className="text-xs text-[#5F708C] font-semibold mt-0.5">
            دورة {Math.min(cyclesCompleted + 1, totalCycles)} من {totalCycles}
          </span>
        </div>
      </div>

      <div className="flex flex-col gap-1 max-w-xs">
        <h4 className="text-base font-bold text-[#061A3A]">{getPhaseText()}</h4>
        <p className="text-xs text-[#5F708C] leading-relaxed">
          التنفس البطيء يهدئ الجهاز العصبي ويخفض تركيز هرمونات التوتر والرغبة اللحظية.
        </p>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-3 w-full max-w-xs">
        {!isActive ? (
          <Button
            variant="primary"
            size="lg"
            fullWidth
            onClick={handleStart}
            leftIcon={<Play className="w-4 h-4" />}
          >
            ابدأ التمرين الآن
          </Button>
        ) : (
          <>
            <Button
              variant="secondary"
              size="md"
              fullWidth
              onClick={() => setIsActive(false)}
              leftIcon={<Pause className="w-4 h-4" />}
            >
              إيقاف مؤقت
            </Button>
            <Button
              variant="ghost"
              size="md"
              onClick={handleReset}
              leftIcon={<RotateCcw className="w-4 h-4" />}
            >
              إعادة
            </Button>
          </>
        )}
      </div>
    </div>
  );
};
