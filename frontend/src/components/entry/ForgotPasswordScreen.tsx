import { useState, type FormEvent } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { Mail, CheckCircle2, AlertCircle, ArrowRight, ShieldCheck } from 'lucide-react';

export const ForgotPasswordScreen = () => {
  const { resetPasswordForEmail, setAuthStep, status, errorMessage, clearError } = useAuth();
  const [email, setEmail] = useState('');
  const [isSuccess, setIsSuccess] = useState(false);
  const [emailError, setEmailError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setEmailError(null);
    clearError();

    const cleanEmail = email.trim();
    if (!cleanEmail) {
      setEmailError('اكتب بريدك الإلكتروني.');
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(cleanEmail)) {
      setEmailError('اكتب بريد إلكتروني صحيح.');
      return;
    }

    const ok = await resetPasswordForEmail(cleanEmail);
    if (ok) {
      setIsSuccess(true);
    }
  };

  const isLoading = status === 'loading';

  return (
    <div
      className="w-full min-h-[100dvh] flex flex-col justify-between bg-[#F7F9FC] text-[#061A3A] font-arabic p-4 sm:p-6 select-none"
      dir="rtl"
      style={{ paddingTop: 'calc(1.5rem + var(--sat))', paddingBottom: 'calc(1.5rem + var(--sab))' }}
    >
      <div className="w-full max-w-md mx-auto flex flex-col gap-6 my-auto">
        {/* Header with back button */}
        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={() => {
              clearError();
              setAuthStep('login');
            }}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#5F708C] hover:text-[#061A3A] transition-colors cursor-pointer"
          >
            <ArrowRight className="w-4 h-4" />
            <span>العودة لتسجيل الدخول</span>
          </button>
        </div>

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
              نسيت كلمة المرور؟
            </h1>
            <p className="text-sm text-[#5F708C] leading-relaxed max-w-xs">
              اكتب بريدك الإلكتروني وهنبعتلك خطوات إعادة التعيين.
            </p>
          </div>
        </div>

        {/* Form or Success Card */}
        <div className="bg-[#FFFFFF] border border-[#D9E2F0] rounded-3xl p-6 sm:p-7 shadow-sm flex flex-col gap-5">
          {isSuccess ? (
            <div className="flex flex-col items-center text-center gap-4 py-2">
              <div className="w-14 h-14 rounded-full bg-[#34D399]/15 text-[#047857] flex items-center justify-center">
                <CheckCircle2 className="w-7 h-7" />
              </div>
              <div className="flex flex-col gap-1.5">
                <h3 className="text-base font-bold text-[#061A3A]">راجع بريدك الإلكتروني</h3>
                <p className="text-xs text-[#5F708C] leading-relaxed">
                  أرسلنا رابط إعادة تعيين كلمة المرور إلى <strong>{email}</strong>. يرجى الضغط على الرابط في الرسالة لتعيين كلمة مرور جديدة.
                </p>
              </div>

              <Button
                variant="primary"
                size="lg"
                fullWidth
                onClick={() => {
                  clearError();
                  setAuthStep('login');
                }}
              >
                العودة لتسجيل الدخول
              </Button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
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

              {errorMessage && (
                <div className="flex items-center gap-2 p-3.5 rounded-xl bg-[#F87171]/10 border border-[#F87171]/30 text-xs text-[#B91C1C]">
                  <AlertCircle className="w-4 h-4 shrink-0 text-[#F87171]" />
                  <span className="leading-relaxed">{errorMessage}</span>
                </div>
              )}

              <Button
                type="submit"
                variant="primary"
                size="lg"
                fullWidth
                isLoading={isLoading}
              >
                إرسال رابط إعادة التعيين
              </Button>
            </form>
          )}
        </div>
      </div>

      {/* Trust Footnote */}
      <div className="text-center py-2 flex items-center justify-center gap-2 text-xs text-[#8291A8]">
        <ShieldCheck className="w-4 h-4 text-[#34D399]" />
        <span>بياناتك في أمان تام وتخضع لمعايير السرية الطبية.</span>
      </div>
    </div>
  );
};
