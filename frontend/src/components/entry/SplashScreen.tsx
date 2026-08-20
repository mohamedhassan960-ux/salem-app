import { useEffect } from 'react';

export interface SplashScreenProps {
  onComplete: () => void;
  durationMs?: number;
}

export const SplashScreen = ({
  onComplete,
  durationMs = 1200,
}: SplashScreenProps) => {
  useEffect(() => {
    const timer = setTimeout(onComplete, durationMs);
    return () => clearTimeout(timer);
  }, [onComplete, durationMs]);

  return (
    <div
      className="w-full h-[100dvh] flex flex-col items-center justify-center bg-slate-950 text-white select-none"
      style={{ paddingTop: 'var(--sat)', paddingBottom: 'var(--sab)' }}
      role="status"
      aria-label="جارٍ تحميل سالم"
    >
      <div className="flex flex-col items-center gap-6">
        <div className="relative">
          <div className="absolute -inset-4 rounded-3xl bg-sky-500/20 blur-2xl animate-pulse" />
          <div className="relative w-28 h-28 rounded-3xl p-1 bg-gradient-to-b from-sky-400 via-blue-600 to-indigo-600 border border-sky-400/40 shadow-2xl overflow-hidden flex items-center justify-center">
            <img
              src="/logo.png"
              alt="سالم"
              className="w-full h-full object-cover rounded-2xl"
            />
          </div>
        </div>

        <div className="flex flex-col items-center gap-1 text-center">
          <h1 className="text-3xl font-extrabold tracking-tight text-white">سالم</h1>
          <p className="text-sm text-slate-300 font-medium">
            المساعد الطبي للإقلاع عن التدخين
          </p>
        </div>

        <div className="flex items-center gap-2 mt-1">
          <span className="w-2 h-2 rounded-full bg-sky-400 animate-ping" />
          <span className="text-[11px] text-slate-400 font-semibold">إرشادات منظمة الصحة العالمية 2024</span>
        </div>
      </div>
    </div>
  );
};
