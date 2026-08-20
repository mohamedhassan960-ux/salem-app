import { useAuth } from '../../context/AuthContext';
import { GoogleSignInButton } from './GoogleSignInButton';
import { AlertCircle, Lock } from 'lucide-react';

export interface LoginScreenProps {
  onSuccess: () => void;
}

export const LoginScreen = ({ onSuccess }: LoginScreenProps) => {
  const { signInWithGoogle, status, errorMessage } = useAuth();

  const handleLogin = async () => {
    await signInWithGoogle();
    onSuccess();
  };

  return (
    <div
      className="w-full h-[100dvh] flex flex-col justify-between bg-slate-950 text-white select-none"
      style={{ paddingTop: 'var(--sat)', paddingBottom: 'var(--sab)' }}
      dir="rtl"
    >
      {/* Top badge */}
      <div className="pt-6 px-6 flex justify-center">
        <span className="px-3.5 py-1 rounded-full text-xs font-bold bg-sky-500/15 text-sky-300 border border-sky-500/25 tracking-wide">
          تطبيق سالم الطبي
        </span>
      </div>

      {/* Center content */}
      <div className="flex-1 flex flex-col items-center justify-center text-center px-8 gap-5">
        <div className="relative">
          <div className="absolute -inset-3 rounded-3xl bg-sky-500/20 blur-xl animate-pulse-subtle" />
          <div className="relative w-28 h-28 rounded-3xl p-1 bg-gradient-to-b from-sky-400 via-blue-600 to-indigo-600 border border-sky-400/40 shadow-2xl overflow-hidden flex items-center justify-center">
            <img
              src="/logo.png"
              alt="سالم"
              className="w-full h-full object-cover rounded-2xl"
            />
          </div>
        </div>

        <div className="flex flex-col gap-2 max-w-[300px]">
          <h1 className="text-2xl font-bold text-white tracking-tight">مرحبًا بك مع سالم</h1>
          <p className="text-sm text-slate-300 leading-relaxed">
            استشارك الطبي المتخصص للإقلاع عن التدخين، مستند لأحدث أدلة منظمة الصحة العالمية 2024.
          </p>
        </div>

        {errorMessage && (
          <div className="w-full max-w-[320px] flex items-center gap-2.5 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs text-right">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{errorMessage}</span>
          </div>
        )}

        <div className="w-full max-w-[320px]">
          <GoogleSignInButton
            onClick={handleLogin}
            isLoading={status === 'loading'}
          />
        </div>
      </div>

      {/* Disclaimer */}
      <div className="px-8 pb-6 text-center">
        <p className="text-[11px] text-slate-500 leading-relaxed flex items-center justify-center gap-1.5 max-w-xs mx-auto">
          <Lock className="w-3 h-3 shrink-0" />
          <span>سالم يقدم إرشادات توعوية ولا يُعدّ بديلاً عن الفحص السريري المباشر.</span>
        </p>
      </div>
    </div>
  );
};
