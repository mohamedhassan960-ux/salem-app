import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Button } from '../ui/Button';
import { MailCheck, RefreshCw, ArrowRight, ShieldCheck } from 'lucide-react';

export const EmailConfirmationScreen = () => {
  const { setAuthStep, user } = useAuth();
  const [resendStatus, setResendStatus] = useState<'idle' | 'sending' | 'sent'>('idle');

  const handleResend = async () => {
    setResendStatus('sending');
    await new Promise((resolve) => setTimeout(resolve, 800));
    setResendStatus('sent');
  };

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
              راجع بريدك الإلكتروني
            </h1>
            <p className="text-sm text-[#5F708C] leading-relaxed max-w-xs">
              بعتنالك رسالة لتأكيد حسابك والبدء في رحلتك مع سالم.
            </p>
          </div>
        </div>

        {/* Confirmation Card */}
        <div className="bg-[#FFFFFF] border border-[#D9E2F0] rounded-3xl p-6 sm:p-7 shadow-sm flex flex-col gap-5 text-center items-center">
          <div className="w-16 h-16 rounded-3xl bg-[#2D8BFF]/10 text-[#2D8BFF] flex items-center justify-center">
            <MailCheck className="w-8 h-8" />
          </div>

          <div className="flex flex-col gap-1.5">
            <h3 className="text-base font-bold text-[#061A3A]">تأكيد البريد الإلكتروني</h3>
            <p className="text-xs text-[#5F708C] leading-relaxed">
              افتح الرابط الموجود في الرسالة المرسلة إلى بريدك{user?.email ? ` (${user.email})` : ''} لتفعيل حسابك، ثم اضغط تسجيل الدخول.
            </p>
          </div>

          <div className="w-full flex flex-col gap-3 pt-2">
            <Button
              variant="primary"
              size="lg"
              fullWidth
              onClick={() => setAuthStep('login')}
            >
              الانتقال لتسجيل الدخول
            </Button>

            <Button
              variant="outline"
              size="md"
              fullWidth
              isLoading={resendStatus === 'sending'}
              onClick={handleResend}
              leftIcon={<RefreshCw className="w-4 h-4" />}
            >
              {resendStatus === 'sent' ? 'تمت إعادة إرسال الرسالة بنجاح' : 'إعادة إرسال رسالة التأكيد'}
            </Button>
          </div>

          <button
            type="button"
            onClick={() => setAuthStep('signup')}
            className="inline-flex items-center gap-1 text-xs text-[#5F708C] hover:text-[#061A3A] font-semibold cursor-pointer pt-2"
          >
            <ArrowRight className="w-3.5 h-3.5" />
            <span>تغيير البريد الإلكتروني أو إنشاء حساب آخر</span>
          </button>
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
