import { useState, type FormEvent } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { Divider } from '../ui/Divider';
import { GoogleSignInButton } from './GoogleSignInButton';
import { Eye, EyeOff, Mail, Lock, AlertCircle, ShieldCheck } from 'lucide-react';

export const LoginScreen = () => {
  const { signInWithGoogle, signInWithEmail, setAuthStep, status, errorMessage, clearError } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [emailError, setEmailError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);

  const validateForm = (): boolean => {
    let isValid = true;
    setEmailError(null);
    setPasswordError(null);
    clearError();

    const cleanEmail = email.trim();
    if (!cleanEmail) {
      setEmailError('اكتب بريدك الإلكتروني.');
      isValid = false;
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(cleanEmail)) {
      setEmailError('اكتب بريد إلكتروني صحيح.');
      isValid = false;
    }

    if (!password) {
      setPasswordError('اكتب كلمة المرور.');
      isValid = false;
    }

    return isValid;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;
    await signInWithEmail(email.trim(), password);
  };

  const handleGoogleClick = async () => {
    clearError();
    await signInWithGoogle();
  };

  const isLoading = status === 'loading';

  return (
    <div
      className="w-full min-h-[100dvh] flex flex-col justify-between bg-[#F7F9FC] text-[#061A3A] font-arabic p-4 sm:p-6 select-none"
      dir="rtl"
      style={{ paddingTop: 'calc(1.5rem + var(--sat))', paddingBottom: 'calc(1.5rem + var(--sab))' }}
    >
      <div className="w-full max-w-md mx-auto flex flex-col gap-6 my-auto">
        {/* Brand Header */}
        <div className="flex flex-col items-center text-center gap-3">
          <div className="relative">
            <div className="w-20 h-20 rounded-3xl p-1 bg-gradient-to-b from-[#2D8BFF] to-[#0B2454] border border-[#D9E2F0] shadow-md flex items-center justify-center">
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

          <div className="flex flex-col gap-1">
            <h1 className="text-2xl font-extrabold text-[#061A3A] tracking-tight">
              أهلاً بيك في سالم
            </h1>
            <p className="text-sm text-[#5F708C] leading-relaxed max-w-xs">
              مساعدك للإقلاع، خطوة بخطوة.
            </p>
          </div>
        </div>

        {/* Auth Form Card */}
        <div className="bg-[#FFFFFF] border border-[#D9E2F0] rounded-3xl p-6 sm:p-7 shadow-sm flex flex-col gap-5">
          {/* Google OAuth Button */}
          <GoogleSignInButton
            onClick={handleGoogleClick}
            isLoading={isLoading}
          />

          <Divider label="أو" />

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            {/* Email Input */}
            <Input
              label="البريد الإلكتروني"
              type="email"
              placeholder="name@example.com"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                if (emailError) setEmailError(null);
                if (errorMessage) clearError();
              }}
              error={emailError || undefined}
              startIcon={<Mail className="w-4 h-4" />}
              autoComplete="email"
              disabled={isLoading}
            />

            {/* Password Input with Visibility Toggle */}
            <div className="flex flex-col gap-1">
              <Input
                label="كلمة المرور"
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (passwordError) setPasswordError(null);
                  if (errorMessage) clearError();
                }}
                error={passwordError || undefined}
                startIcon={<Lock className="w-4 h-4" />}
                endIcon={
                  <button
                    type="button"
                    onClick={() => setShowPassword((prev) => !prev)}
                    aria-label={showPassword ? 'إخفاء كلمة المرور' : 'إظهار كلمة المرور'}
                    className="w-8 h-8 min-w-[32px] min-h-[32px] flex items-center justify-center text-[#8291A8] hover:text-[#061A3A] transition-colors cursor-pointer"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                }
                autoComplete="current-password"
                disabled={isLoading}
              />

              <button
                type="button"
                onClick={() => setAuthStep('forgot_password')}
                className="self-end text-xs text-[#2D8BFF] hover:text-[#1E3A8A] font-semibold transition-colors mt-1 cursor-pointer"
              >
                نسيت كلمة المرور؟
              </button>
            </div>

            {/* Server / Auth Error Banner */}
            {errorMessage && (
              <div className="flex items-center gap-2 p-3.5 rounded-xl bg-[#F87171]/10 border border-[#F87171]/30 text-xs text-[#B91C1C]">
                <AlertCircle className="w-4 h-4 shrink-0 text-[#F87171]" />
                <span className="leading-relaxed">{errorMessage}</span>
              </div>
            )}

            {/* Submit CTA */}
            <Button
              type="submit"
              variant="primary"
              size="lg"
              fullWidth
              isLoading={isLoading}
            >
              تسجيل الدخول
            </Button>
          </form>

          {/* Create Account Switcher */}
          <div className="flex items-center justify-center gap-1.5 pt-2 border-t border-[#D9E2F0] text-xs text-[#5F708C]">
            <span>لسه معندكش حساب؟</span>
            <button
              type="button"
              onClick={() => {
                clearError();
                setAuthStep('signup');
              }}
              className="text-[#2D8BFF] hover:text-[#1E3A8A] font-bold cursor-pointer transition-colors"
            >
              إنشاء حساب
            </button>
          </div>
        </div>
      </div>

      {/* Safety & Trust Footnote */}
      <div className="text-center py-2 flex items-center justify-center gap-2 text-xs text-[#8291A8]">
        <ShieldCheck className="w-4 h-4 text-[#34D399]" />
        <span>بياناتك في أمان تام وتخضع لمعايير السرية الطبية.</span>
      </div>
    </div>
  );
};
