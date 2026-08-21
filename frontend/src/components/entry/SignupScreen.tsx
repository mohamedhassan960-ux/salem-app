import { useState, type FormEvent } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { User, Mail, Lock, Eye, EyeOff, AlertCircle, ShieldCheck } from 'lucide-react';

export const SignupScreen = () => {
  const { signUpWithEmail, setAuthStep, status, errorMessage, clearError } = useAuth();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  // Errors
  const [nameError, setNameError] = useState<string | null>(null);
  const [emailError, setEmailError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [confirmPasswordError, setConfirmPasswordError] = useState<string | null>(null);

  // Password strength calculation
  const getPasswordStrength = () => {
    if (!password) return 0;
    let strength = 0;
    if (password.length >= 8) strength += 1;
    if (/[A-Z]/.test(password) || /[a-z]/.test(password)) strength += 1;
    if (/\d/.test(password) || /[^A-Za-z0-9]/.test(password)) strength += 1;
    return strength;
  };

  const strength = getPasswordStrength();

  const validateForm = (): boolean => {
    let isValid = true;
    setNameError(null);
    setEmailError(null);
    setPasswordError(null);
    setConfirmPasswordError(null);
    clearError();

    if (!name.trim()) {
      setNameError('اكتب اسمك للمتابعة.');
      isValid = false;
    }

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
    } else if (password.length < 8) {
      setPasswordError('كلمة المرور يجب أن تكون 8 أحرف على الأقل.');
      isValid = false;
    }

    if (password !== confirmPassword) {
      setConfirmPasswordError('كلمتا المرور غير متطابقتين.');
      isValid = false;
    }

    return isValid;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;
    await signUpWithEmail(email.trim(), password, name.trim());
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
              أنشئ حسابك
            </h1>
            <p className="text-sm text-[#5F708C] leading-relaxed max-w-xs">
              هنستخدم بياناتك عشان نخلي رحلة سالم مناسبة ليك.
            </p>
          </div>
        </div>

        {/* Signup Form Card */}
        <div className="bg-[#FFFFFF] border border-[#D9E2F0] rounded-3xl p-6 sm:p-7 shadow-sm flex flex-col gap-5">
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            {/* Name Input */}
            <Input
              label="الاسم"
              type="text"
              placeholder="مثال: أحمد مصطفى"
              value={name}
              onChange={(e) => {
                setName(e.target.value);
                if (nameError) setNameError(null);
              }}
              error={nameError || undefined}
              startIcon={<User className="w-4 h-4" />}
              autoComplete="name"
              disabled={isLoading}
            />

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

            {/* Password Input */}
            <div className="flex flex-col gap-1.5">
              <Input
                label="كلمة المرور"
                type={showPassword ? 'text' : 'password'}
                placeholder="8 أحرف على الأقل"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (passwordError) setPasswordError(null);
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
                autoComplete="new-password"
                disabled={isLoading}
              />

              {/* Password Strength Indicator */}
              {password.length > 0 && (
                <div className="flex items-center gap-1.5 mt-1 px-1">
                  <div className="flex-1 flex gap-1 h-1.5 rounded-full overflow-hidden bg-[#E8EFF8]">
                    <div
                      className={`h-full transition-all duration-300 ${
                        strength === 1
                          ? 'w-1/3 bg-[#F87171]'
                          : strength === 2
                          ? 'w-2/3 bg-[#FBBF24]'
                          : 'w-full bg-[#34D399]'
                      }`}
                    />
                  </div>
                  <span className="text-[11px] text-[#5F708C] font-medium">
                    {strength === 1 ? 'مقبولة' : strength === 2 ? 'جيدة' : 'قوية وممتازة'}
                  </span>
                </div>
              )}
            </div>

            {/* Confirm Password Input */}
            <Input
              label="تأكيد كلمة المرور"
              type={showPassword ? 'text' : 'password'}
              placeholder="••••••••"
              value={confirmPassword}
              onChange={(e) => {
                setConfirmPassword(e.target.value);
                if (confirmPasswordError) setConfirmPasswordError(null);
              }}
              error={confirmPasswordError || undefined}
              startIcon={<Lock className="w-4 h-4" />}
              autoComplete="new-password"
              disabled={isLoading}
            />

            {/* Server Error */}
            {errorMessage && (
              <div className="flex items-center gap-2 p-3.5 rounded-xl bg-[#F87171]/10 border border-[#F87171]/30 text-xs text-[#B91C1C]">
                <AlertCircle className="w-4 h-4 shrink-0 text-[#F87171]" />
                <span className="leading-relaxed">{errorMessage}</span>
              </div>
            )}

            {/* Terms & Consent */}
            <p className="text-xs text-[#5F708C] leading-relaxed mt-1">
              بإنشاء الحساب، أنت توافق على{' '}
              <span className="text-[#1E3A8A] font-semibold underline underline-offset-2">
                شروط الاستخدام
              </span>{' '}
              و{' '}
              <span className="text-[#1E3A8A] font-semibold underline underline-offset-2">
                سياسة الخصوصية
              </span>
              .
            </p>

            {/* Submit CTA */}
            <Button
              type="submit"
              variant="primary"
              size="lg"
              fullWidth
              isLoading={isLoading}
            >
              إنشاء الحساب
            </Button>
          </form>

          {/* Login Switcher */}
          <div className="flex items-center justify-center gap-1.5 pt-2 border-t border-[#D9E2F0] text-xs text-[#5F708C]">
            <span>عندي حساب بالفعل؟</span>
            <button
              type="button"
              onClick={() => {
                clearError();
                setAuthStep('login');
              }}
              className="text-[#2D8BFF] hover:text-[#1E3A8A] font-bold cursor-pointer transition-colors"
            >
              تسجيل الدخول
            </button>
          </div>
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
