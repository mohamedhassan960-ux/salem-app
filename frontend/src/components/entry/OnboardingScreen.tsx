import { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useUserState } from '../../state/UserStateContext';
import { onboardingService } from '../../services/onboardingService';
import { Button } from '../ui/Button';
import type { OnboardingAnswers, GoalOption } from '../../types/onboarding';
import {
  Cigarette,
  Flame,
  Clock,
  Zap,
  Target,
  Gauge,
  ArrowRight,
  ArrowLeft,
  Check,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';

export interface OnboardingScreenProps {
  onComplete: () => void;
}

export const OnboardingScreen = ({ onComplete }: OnboardingScreenProps) => {
  const { user, markOnboardingComplete } = useAuth();
  const { updateSmokingProfile } = useUserState();

  const userId = user?.id || 'guest_user';

  // Current onboarding step: 0 = Intro, 1..6 = Questions, 7 = Completion
  const [step, setStep] = useState<number>(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Form State initialized with any saved draft or defaults
  const [answers, setAnswers] = useState<OnboardingAnswers>(() => {
    const savedDraft = onboardingService.getDraft(userId);
    return {
      tobaccoTypes: savedDraft?.tobaccoTypes || ['cigarettes'],
      dailyCount: savedDraft?.dailyCount !== undefined ? savedDraft.dailyCount : 15,
      lastSmokedAt: savedDraft?.lastSmokedAt || Date.now(),
      lastSmokedOption: savedDraft?.lastSmokedOption || 'today',
      primaryTriggers: savedDraft?.primaryTriggers || ['التوتر'],
      goal: savedDraft?.goal || 'quit_completely',
      readiness: savedDraft?.readiness || 4,
    };
  });

  // Save draft whenever answers change
  useEffect(() => {
    onboardingService.saveDraft(userId, answers);
  }, [answers, userId]);

  const totalQuestionSteps = 6;

  const handleNext = async () => {
    setErrorMessage(null);

    // Validation per step
    if (step === 1 && answers.tobaccoTypes.length === 0) {
      setErrorMessage('اختار إجابة عشان نكمل.');
      return;
    }
    if (step === 4 && answers.primaryTriggers.length === 0) {
      setErrorMessage('اختار محفز واحد على الأقل.');
      return;
    }

    if (step < totalQuestionSteps) {
      setStep((s) => s + 1);
    } else if (step === totalQuestionSteps) {
      // Move to Completion step
      setStep(7);
    } else if (step === 7) {
      // Submit authoritative to Supabase & UserStateContext
      setIsSubmitting(true);
      try {
        const { profile } = await onboardingService.submitOnboarding(userId, answers);
        updateSmokingProfile(profile);
        markOnboardingComplete();
        onComplete();
      } catch (err) {
        console.error('[OnboardingScreen] Error submitting onboarding:', err);
        setErrorMessage('حصلت مشكلة وأنا بحفظ بياناتك. جرّب تاني.');
      } finally {
        setIsSubmitting(false);
      }
    }
  };

  const handleBack = () => {
    setErrorMessage(null);
    if (step > 0) {
      setStep((s) => s - 1);
    }
  };

  const toggleTobaccoType = (type: string) => {
    setAnswers((prev) => {
      const exists = prev.tobaccoTypes.includes(type);
      return {
        ...prev,
        tobaccoTypes: exists
          ? prev.tobaccoTypes.filter((t) => t !== type)
          : [...prev.tobaccoTypes, type],
      };
    });
  };

  const toggleTrigger = (trig: string) => {
    setAnswers((prev) => {
      const exists = prev.primaryTriggers.includes(trig);
      return {
        ...prev,
        primaryTriggers: exists
          ? prev.primaryTriggers.filter((t) => t !== trig)
          : [...prev.primaryTriggers, trig],
      };
    });
  };

  const handleLastSmokedSelect = (opt: 'today' | 'yesterday' | 'days_ago' | 'not_yet') => {
    let timestamp = Date.now();
    if (opt === 'yesterday') {
      timestamp = Date.now() - 24 * 60 * 60 * 1000;
    } else if (opt === 'days_ago') {
      timestamp = Date.now() - 3 * 24 * 60 * 60 * 1000;
    } else if (opt === 'not_yet') {
      timestamp = Date.now();
    }

    setAnswers((prev) => ({
      ...prev,
      lastSmokedOption: opt,
      lastSmokedAt: timestamp,
    }));
  };

  return (
    <div
      className="w-full min-h-[100dvh] flex flex-col justify-between bg-[#F7F9FC] text-[#061A3A] font-arabic p-4 sm:p-6 select-none"
      dir="rtl"
      style={{ paddingTop: 'calc(1rem + var(--sat))', paddingBottom: 'calc(1.5rem + var(--sab))' }}
    >
      {/* Top Header / Progress Indicator */}
      <div className="w-full max-w-lg mx-auto flex items-center justify-between pb-3">
        {step > 0 && step <= totalQuestionSteps ? (
          <div className="flex items-center gap-3">
            <div className="flex gap-1.5">
              {Array.from({ length: totalQuestionSteps }).map((_, i) => (
                <div
                  key={i}
                  className={`h-2 rounded-full transition-all duration-300 ${
                    i + 1 === step
                      ? 'w-7 bg-[#2D8BFF]'
                      : i + 1 < step
                      ? 'w-2.5 bg-[#1E3A8A]'
                      : 'w-2.5 bg-[#D9E2F0]'
                  }`}
                />
              ))}
            </div>
            <span className="text-xs font-bold text-[#5F708C] mr-1">
              {step} من {totalQuestionSteps}
            </span>
          </div>
        ) : (
          <div />
        )}

        {step > 0 && step <= totalQuestionSteps && (
          <button
            type="button"
            onClick={handleBack}
            className="flex items-center gap-1 text-xs font-semibold text-[#5F708C] hover:text-[#061A3A] cursor-pointer transition-colors"
          >
            <ArrowRight className="w-4 h-4" />
            <span>السابق</span>
          </button>
        )}
      </div>

      {/* Main Content Card Container */}
      <div className="w-full max-w-lg mx-auto flex-1 flex flex-col justify-center my-auto">
        <div className="bg-[#FFFFFF] border border-[#D9E2F0] rounded-3xl p-6 sm:p-8 shadow-sm flex flex-col gap-6 animate-in fade-in duration-200">
          {/* ── Step 0: Intro ── */}
          {step === 0 && (
            <div className="flex flex-col items-center text-center gap-5 py-2">
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

              <div className="flex flex-col gap-2 max-w-sm">
                <h1 className="text-2xl font-extrabold text-[#061A3A] tracking-tight">
                  خلينا نتعرف عليك شوية.
                </h1>
                <p className="text-sm text-[#5F708C] leading-relaxed">
                  مش محتاج تكون جاهز لكل حاجة دلوقتي. سالم هيمشي معاك خطوة بخطوة وبدون أي أحكام.
                </p>
              </div>

              <div className="w-full pt-3">
                <Button
                  variant="primary"
                  size="lg"
                  fullWidth
                  onClick={() => setStep(1)}
                  leftIcon={<ArrowLeft className="w-4 h-4" />}
                >
                  نبدأ
                </Button>
              </div>
            </div>
          )}

          {/* ── Question 01: Tobacco Type ── */}
          {step === 1 && (
            <div className="flex flex-col gap-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl bg-[#2D8BFF]/10 text-[#2D8BFF] flex items-center justify-center shrink-0">
                  <Cigarette className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-lg sm:text-xl font-bold text-[#061A3A]">
                    بتدخن إيه حاليًا؟
                  </h2>
                  <p className="text-xs text-[#5F708C]">اختر ما ينطبق عليك لتخصيص الدعم</p>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 mt-2">
                {[
                  { id: 'cigarettes', label: 'سجائر' },
                  { id: 'shisha', label: 'شيشة / معسل' },
                  { id: 'vape', label: 'سجائر إلكترونية (فيب)' },
                  { id: 'heated_tobacco', label: 'تبغ مسخن' },
                  { id: 'other', label: 'أكثر من نوع / تبغ آخر' },
                ].map((item) => {
                  const isSelected = answers.tobaccoTypes.includes(item.id);
                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => toggleTobaccoType(item.id)}
                      className={`
                        min-h-[48px] p-4 rounded-2xl border text-right font-arabic flex items-center justify-between transition-all duration-150 cursor-pointer
                        ${
                          isSelected
                            ? 'border-[#2D8BFF] bg-[#2D8BFF]/5 font-bold text-[#1E3A8A] ring-2 ring-[#2D8BFF]/20'
                            : 'border-[#D9E2F0] bg-[#F4F7FB] text-[#061A3A] hover:border-[#C4D1E3]'
                        }
                      `}
                    >
                      <span className="text-sm">{item.label}</span>
                      {isSelected && <Check className="w-4 h-4 text-[#2D8BFF]" />}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* ── Question 02: Daily Count ── */}
          {step === 2 && (
            <div className="flex flex-col gap-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl bg-[#2D8BFF]/10 text-[#2D8BFF] flex items-center justify-center shrink-0">
                  <Flame className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-lg sm:text-xl font-bold text-[#061A3A]">
                    بتدخن قد إيه تقريبًا؟
                  </h2>
                  <p className="text-xs text-[#5F708C]">تقدير تقريبي لعدد السجائر أو الجلسات يوميًا</p>
                </div>
              </div>

              <div className="flex flex-col gap-2.5 mt-2">
                {[
                  { value: 5, label: 'أقل من 10 سجائر يوميًا' },
                  { value: 15, label: '10 إلى 20 سيجارة (علبة تقريبًا)' },
                  { value: 25, label: '20 إلى 30 سيجارة (علبة ونصف)' },
                  { value: 40, label: 'أكثر من علبتين يوميًا' },
                  { value: 'unsure', label: 'مش متأكد / بيختلف من يوم للتاني' },
                ].map((item) => {
                  const isSelected = answers.dailyCount === item.value;
                  return (
                    <button
                      key={String(item.value)}
                      type="button"
                      onClick={() =>
                        setAnswers((prev) => ({
                          ...prev,
                          dailyCount: item.value as number | 'unsure',
                        }))
                      }
                      className={`
                        min-h-[48px] p-4 rounded-2xl border text-right font-arabic flex items-center justify-between transition-all duration-150 cursor-pointer
                        ${
                          isSelected
                            ? 'border-[#2D8BFF] bg-[#2D8BFF]/5 font-bold text-[#1E3A8A] ring-2 ring-[#2D8BFF]/20'
                            : 'border-[#D9E2F0] bg-[#F4F7FB] text-[#061A3A] hover:border-[#C4D1E3]'
                        }
                      `}
                    >
                      <span className="text-sm">{item.label}</span>
                      {isSelected && <Check className="w-4 h-4 text-[#2D8BFF]" />}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* ── Question 03: Last Smoked Time ── */}
          {step === 3 && (
            <div className="flex flex-col gap-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl bg-[#2D8BFF]/10 text-[#2D8BFF] flex items-center justify-center shrink-0">
                  <Clock className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-lg sm:text-xl font-bold text-[#061A3A]">
                    إمتى كانت آخر مرة دخنت؟
                  </h2>
                  <p className="text-xs text-[#5F708C]">لحساب بداية مرحلة التعافي وخطتك بدقة</p>
                </div>
              </div>

              <div className="flex flex-col gap-2.5 mt-2">
                {[
                  { id: 'today', label: 'اليوم (خلال الساعات القليلة الماضية)' },
                  { id: 'yesterday', label: 'أمس (أكثر من 24 ساعة بدون تدخين)' },
                  { id: 'days_ago', label: 'منذ عدة أيام' },
                  { id: 'not_yet', label: 'لسه ما بدأتش، ناوي أبدأ قريبًا' },
                ].map((item) => {
                  const isSelected = answers.lastSmokedOption === item.id;
                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => handleLastSmokedSelect(item.id as any)}
                      className={`
                        min-h-[48px] p-4 rounded-2xl border text-right font-arabic flex items-center justify-between transition-all duration-150 cursor-pointer
                        ${
                          isSelected
                            ? 'border-[#2D8BFF] bg-[#2D8BFF]/5 font-bold text-[#1E3A8A] ring-2 ring-[#2D8BFF]/20'
                            : 'border-[#D9E2F0] bg-[#F4F7FB] text-[#061A3A] hover:border-[#C4D1E3]'
                        }
                      `}
                    >
                      <span className="text-sm">{item.label}</span>
                      {isSelected && <Check className="w-4 h-4 text-[#2D8BFF]" />}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* ── Question 04: Triggers ── */}
          {step === 4 && (
            <div className="flex flex-col gap-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl bg-[#2D8BFF]/10 text-[#2D8BFF] flex items-center justify-center shrink-0">
                  <Zap className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-lg sm:text-xl font-bold text-[#061A3A]">
                    إيه أكثر حاجة بتخليك ترغب في التدخين؟
                  </h2>
                  <p className="text-xs text-[#5F708C]">يمكنك اختيار أكثر من محفز</p>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 mt-2">
                {[
                  'التوتر وضغط العمل',
                  'القهوة أو الشاي',
                  'بعد الأكل مباشرة',
                  'الصحاب والتجمعات',
                  'الملل والفراغ',
                  'أوقات معينة في اليوم',
                  'مش عارف بالضبط',
                ].map((trig) => {
                  const isSelected = answers.primaryTriggers.includes(trig);
                  return (
                    <button
                      key={trig}
                      type="button"
                      onClick={() => toggleTrigger(trig)}
                      className={`
                        min-h-[48px] p-3.5 rounded-2xl border text-right font-arabic flex items-center justify-between transition-all duration-150 cursor-pointer
                        ${
                          isSelected
                            ? 'border-[#2D8BFF] bg-[#2D8BFF]/5 font-bold text-[#1E3A8A] ring-2 ring-[#2D8BFF]/20'
                            : 'border-[#D9E2F0] bg-[#F4F7FB] text-[#061A3A] hover:border-[#C4D1E3]'
                        }
                      `}
                    >
                      <span className="text-xs sm:text-sm">{trig}</span>
                      {isSelected && <Check className="w-4 h-4 text-[#2D8BFF]" />}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* ── Question 05: Goal ── */}
          {step === 5 && (
            <div className="flex flex-col gap-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl bg-[#2D8BFF]/10 text-[#2D8BFF] flex items-center justify-center shrink-0">
                  <Target className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-lg sm:text-xl font-bold text-[#061A3A]">
                    إيه هدفك دلوقتي؟
                  </h2>
                  <p className="text-xs text-[#5F708C]">سالم هيتكيف تماماً مع استعدادك الحالي</p>
                </div>
              </div>

              <div className="flex flex-col gap-2.5 mt-2">
                {[
                  { id: 'quit_completely', label: 'أوقف نهائيًا' },
                  { id: 'reduce', label: 'أبدأ أقلل تدريجيًا' },
                  { id: 'undecided', label: 'لسه بحاول أحدد خطتي' },
                ].map((item) => {
                  const isSelected = answers.goal === item.id;
                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() =>
                        setAnswers((prev) => ({
                          ...prev,
                          goal: item.id as GoalOption,
                        }))
                      }
                      className={`
                        min-h-[48px] p-4 rounded-2xl border text-right font-arabic flex items-center justify-between transition-all duration-150 cursor-pointer
                        ${
                          isSelected
                            ? 'border-[#2D8BFF] bg-[#2D8BFF]/5 font-bold text-[#1E3A8A] ring-2 ring-[#2D8BFF]/20'
                            : 'border-[#D9E2F0] bg-[#F4F7FB] text-[#061A3A] hover:border-[#C4D1E3]'
                        }
                      `}
                    >
                      <span className="text-sm">{item.label}</span>
                      {isSelected && <Check className="w-4 h-4 text-[#2D8BFF]" />}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* ── Question 06: Readiness ── */}
          {step === 6 && (
            <div className="flex flex-col gap-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl bg-[#2D8BFF]/10 text-[#2D8BFF] flex items-center justify-center shrink-0">
                  <Gauge className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-lg sm:text-xl font-bold text-[#061A3A]">
                    قد إيه حاسس إنك مستعد تبدأ؟
                  </h2>
                  <p className="text-xs text-[#5F708C]">تقييم بسيط يساعدنا نحدد وتيرة الخطة المناسبة ليك</p>
                </div>
              </div>

              <div className="flex flex-col gap-2.5 mt-2">
                {[
                  { level: 1, label: '1 · لسه بفكر ومتردد شوية' },
                  { level: 2, label: '2 · حابب أستكشف الفكرة' },
                  { level: 3, label: '3 · مستعد أبدأ بخطوات صغيرة' },
                  { level: 4, label: '4 · جاهز وعندي دافع قوي' },
                  { level: 5, label: '5 · متحمس ومصمم تماماً' },
                ].map((item) => {
                  const isSelected = answers.readiness === item.level;
                  return (
                    <button
                      key={item.level}
                      type="button"
                      onClick={() =>
                        setAnswers((prev) => ({
                          ...prev,
                          readiness: item.level,
                        }))
                      }
                      className={`
                        min-h-[48px] p-4 rounded-2xl border text-right font-arabic flex items-center justify-between transition-all duration-150 cursor-pointer
                        ${
                          isSelected
                            ? 'border-[#2D8BFF] bg-[#2D8BFF]/5 font-bold text-[#1E3A8A] ring-2 ring-[#2D8BFF]/20'
                            : 'border-[#D9E2F0] bg-[#F4F7FB] text-[#061A3A] hover:border-[#C4D1E3]'
                        }
                      `}
                    >
                      <span className="text-sm">{item.label}</span>
                      {isSelected && <Check className="w-4 h-4 text-[#2D8BFF]" />}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* ── Step 7: Completion Screen ── */}
          {step === 7 && (
            <div className="flex flex-col items-center text-center gap-5 py-2">
              <div className="w-16 h-16 rounded-full bg-[#34D399]/15 text-[#047857] flex items-center justify-center">
                <CheckCircle2 className="w-8 h-8" />
              </div>

              <div className="flex flex-col gap-1.5 max-w-sm">
                <h2 className="text-2xl font-extrabold text-[#061A3A] tracking-tight">
                  تمام، كده سالم عرف يبدأ معاك منين.
                </h2>
                <p className="text-sm text-[#5F708C] leading-relaxed">
                  من هنا هنمشي خطوة بخطوة.
                </p>
              </div>

              {errorMessage && (
                <div className="flex items-center gap-2 p-3.5 rounded-xl bg-[#F87171]/10 border border-[#F87171]/30 text-xs text-[#B91C1C]">
                  <AlertCircle className="w-4 h-4 shrink-0 text-[#F87171]" />
                  <span className="leading-relaxed">{errorMessage}</span>
                </div>
              )}

              <div className="w-full pt-3">
                <Button
                  variant="primary"
                  size="lg"
                  fullWidth
                  isLoading={isSubmitting}
                  onClick={handleNext}
                >
                  ابدأ مع سالم
                </Button>
              </div>
            </div>
          )}

          {/* Error Message */}
          {errorMessage && step !== 7 && (
            <div className="flex items-center gap-2 p-3 rounded-xl bg-[#F87171]/10 border border-[#F87171]/30 text-xs text-[#B91C1C]">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Bottom Action for Steps 1-6 */}
          {step >= 1 && step <= totalQuestionSteps && (
            <div className="pt-2">
              <Button
                variant="primary"
                size="lg"
                fullWidth
                onClick={handleNext}
                leftIcon={<ArrowLeft className="w-4 h-4" />}
              >
                {step === totalQuestionSteps ? 'مراجعة وبدء الخطة' : 'التالي'}
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
