import { useState, useEffect, useRef } from 'react';
import { Button } from '../ui/Button';
import { Play, Pause, RotateCcw, CheckCircle2 } from 'lucide-react';

export interface InterventionTimerProps {
  totalSeconds?: number;
  label?: string;
  supportingText?: string;
  onComplete: () => void;
  className?: string;
}

export const InterventionTimer = ({
  totalSeconds = 60,
  label = 'دقيقة تأجيل الرغبة',
  supportingText = 'خليك معايا لحد ما الوقت يخلص. الرغبة بتبدأ تنكسر تدريجيًا.',
  onComplete,
  className = '',
}: InterventionTimerProps) => {
  const [secondsRemaining, setSecondsRemaining] = useState<number>(totalSeconds);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [isFinished, setIsFinished] = useState<boolean>(false);

  const endTimeRef = useRef<number | null>(null);

  useEffect(() => {
    if (!isRunning) return;

    // Set authoritative target end time
    if (!endTimeRef.current) {
      endTimeRef.current = Date.now() + secondsRemaining * 1000;
    }

    const interval = setInterval(() => {
      if (!endTimeRef.current) return;
      const leftMs = Math.max(0, endTimeRef.current - Date.now());
      const leftSec = Math.ceil(leftMs / 1000);

      setSecondsRemaining(leftSec);

      if (leftSec <= 0) {
        setIsRunning(false);
        setIsFinished(true);
        endTimeRef.current = null;
        clearInterval(interval);
        onComplete();
      }
    }, 200);

    return () => clearInterval(interval);
  }, [isRunning, onComplete, secondsRemaining]);

  const handleStart = () => {
    endTimeRef.current = Date.now() + secondsRemaining * 1000;
    setIsRunning(true);
  };

  const handlePause = () => {
    setIsRunning(false);
    endTimeRef.current = null;
  };

  const handleReset = () => {
    setIsRunning(false);
    setIsFinished(false);
    endTimeRef.current = null;
    setSecondsRemaining(totalSeconds);
  };

  const minutes = Math.floor(secondsRemaining / 60);
  const seconds = secondsRemaining % 60;
  const formattedTime = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

  const progressPercent = Math.max(0, Math.min(100, ((totalSeconds - secondsRemaining) / totalSeconds) * 100));

  return (
    <div className={`flex flex-col items-center text-center gap-5 py-4 font-arabic select-none ${className}`} dir="rtl">
      {/* Big Readable Countdown Circle */}
      <div className="relative w-48 h-48 flex items-center justify-center">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r="44"
            className="text-[#E8EFF8] stroke-current"
            strokeWidth="6"
            fill="transparent"
          />
          <circle
            cx="50"
            cy="50"
            r="44"
            className="text-[#2D8BFF] stroke-current transition-all duration-300"
            strokeWidth="6"
            strokeDasharray="276.46"
            strokeDashoffset={276.46 - (276.46 * progressPercent) / 100}
            strokeLinecap="round"
            fill="transparent"
          />
        </svg>

        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl sm:text-4xl font-black text-[#061A3A] tracking-wider font-mono">
            {formattedTime}
          </span>
          <span className="text-xs text-[#5F708C] font-semibold mt-1">
            {isFinished ? 'انتهى الوقت' : isRunning ? 'جارٍ العد...' : 'جاهز'}
          </span>
        </div>
      </div>

      <div className="flex flex-col gap-1 max-w-xs">
        <h4 className="text-base font-bold text-[#061A3A]">{label}</h4>
        <p className="text-xs text-[#5F708C] leading-relaxed">{supportingText}</p>
      </div>

      {/* Timer Controls */}
      <div className="flex items-center gap-3 w-full max-w-xs pt-2">
        {!isRunning && !isFinished ? (
          <Button
            variant="primary"
            size="lg"
            fullWidth
            onClick={handleStart}
            leftIcon={<Play className="w-4 h-4" />}
          >
            ابدأ العد التنازلي
          </Button>
        ) : isRunning ? (
          <>
            <Button
              variant="secondary"
              size="md"
              fullWidth
              onClick={handlePause}
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
        ) : (
          <div className="flex items-center justify-center gap-2 text-sm font-bold text-[#047857] bg-[#34D399]/15 p-3 rounded-2xl border border-[#34D399]/30 w-full">
            <CheckCircle2 className="w-5 h-5 text-[#34D399]" />
            <span>تم إتمام الدقيقة بنجاح!</span>
          </div>
        )}
      </div>
    </div>
  );
};
