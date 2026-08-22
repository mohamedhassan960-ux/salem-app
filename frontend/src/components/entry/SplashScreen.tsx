import { useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';

export interface SplashScreenProps {
  durationMs?: number;
}

export const SplashScreen = ({
  durationMs = 600,
}: SplashScreenProps) => {
  const { setAuthStep } = useAuth();

  useEffect(() => {
    const timer = setTimeout(() => {
      setAuthStep('chat_ready');
    }, durationMs);

    return () => clearTimeout(timer);
  }, [setAuthStep, durationMs]);

  return (
    <div
      className="w-full h-[100dvh] flex flex-col items-center justify-center bg-gradient-to-b from-[#040F24] via-[#061A3A] to-[#0B2454] text-white select-none font-arabic"
      style={{ paddingTop: 'var(--sat)', paddingBottom: 'var(--sab)' }}
      role="status"
      aria-label="جارٍ تهيئة سالم"
    >
      <div className="flex flex-col items-center gap-6 animate-in fade-in zoom-in-95 duration-700">
        {/* Brand Logo */}
        <div className="relative">
          <div className="absolute -inset-4 rounded-3xl bg-[#2D8BFF]/20 blur-2xl animate-pulse" />
          <div className="relative w-28 h-28 rounded-3xl p-1 bg-gradient-to-b from-[#2D8BFF] via-[#1E3A8A] to-[#0B2454] border border-[#4D9BFF]/30 shadow-2xl overflow-hidden flex items-center justify-center">
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

        {/* Brand Titles */}
        <div className="flex flex-col items-center gap-1 text-center">
          <h1 className="text-3xl font-extrabold tracking-tight text-white">سالم</h1>
          <p className="text-sm text-[#A5C1FF] font-medium">
            مساعدك للإقلاع عن التدخين
          </p>
        </div>

        {/* Minimal indicator */}
        <div className="flex items-center gap-2 mt-2 px-3 py-1 rounded-full bg-white/10 border border-white/15">
          <span className="w-2 h-2 rounded-full bg-[#34D399] animate-ping" />
          <span className="text-xs text-white/90 font-medium">إرشادات منظمة الصحة العالمية 2024</span>
        </div>
      </div>
    </div>
  );
};
