import { ShieldCheck, BookOpen, ArrowLeft, CheckCircle2 } from 'lucide-react';
import { Button } from '../ui/Button';
import { BrandMark } from '../ui/BrandMark';

export interface MarketingPageProps {
  onStartApp: () => void;
}

export const MarketingPage = ({ onStartApp }: MarketingPageProps) => {
  return (
    <div className="w-full min-h-screen bg-[#F7F9FC] text-[#061A3A] font-arabic select-none overflow-y-auto" dir="rtl">
      {/* Navigation Bar */}
      <nav className="w-full bg-[#FFFFFF] border-b border-[#D9E2F0] px-4 sm:px-8 py-4 flex items-center justify-between sticky top-0 z-30 shadow-xs">
        <div className="flex items-center gap-3">
          <BrandMark showSubtitle={false} theme="light" />
        </div>

        <Button variant="primary" size="sm" onClick={onStartApp}>
          دخول التطبيق
        </Button>
      </nav>

      {/* Hero Section (Navy Brand Visual Moment) */}
      <section className="w-full bg-gradient-to-b from-[#061A3A] via-[#0B2454] to-[#0F2D5E] text-white px-4 sm:px-8 py-16 sm:py-24 relative overflow-hidden">
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row items-center justify-between gap-12 relative z-10">
          <div className="flex-1 flex flex-col items-center md:items-start text-center md:text-right gap-6">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/10 border border-white/20 text-xs font-semibold text-[#A5C1FF]">
              <ShieldCheck className="w-4 h-4 text-[#34D399]" />
              <span>مستند لأحدث إرشادات منظمة الصحة العالمية 2024</span>
            </div>

            <h1 className="text-3xl sm:text-5xl font-black tracking-tight leading-tight max-w-xl">
              سالم يساعدك على الإقلاع عن التدخين، خطوة بخطوة.
            </h1>

            <p className="text-sm sm:text-base text-[#A5C1FF] leading-relaxed max-w-lg">
              مساعد رقمي يجمع بين المعرفة العلمية الموثوقة والدعم السلوكي في تجربة شخصية وبسيطة بدون أي أحكام أو ضغوط.
            </p>

            <div className="flex flex-col sm:flex-row items-center gap-3 w-full sm:w-auto pt-2">
              <button
                type="button"
                onClick={onStartApp}
                className="w-full sm:w-auto h-13 px-8 rounded-2xl bg-[#2D8BFF] hover:bg-[#1E7AE6] active:bg-[#1569CC] text-white text-base font-bold flex items-center justify-center gap-2 shadow-lg shadow-[#061A3A]/40 transition-all duration-150 active:scale-95 cursor-pointer"
              >
                <span>ابدأ رحلتك الآن</span>
                <ArrowLeft className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Dr. Salem Character Visual */}
          <div className="flex-1 flex justify-center">
            <div className="relative">
              <div className="absolute -inset-4 rounded-full bg-[#2D8BFF]/20 blur-3xl" />
              <div className="relative w-64 h-64 sm:w-80 sm:h-80 rounded-full p-2 bg-gradient-to-tr from-[#2D8BFF] via-[#1E3A8A] to-[#A5C1FF] border-2 border-white/20 shadow-2xl overflow-hidden flex items-center justify-center">
                <img
                  src="/salem-logo.png"
                  alt="سالم"
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    const t = e.currentTarget;
                    t.onerror = null;
                    t.src = '/logo.png';
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How Salem Works (Technology explanation in human terms) */}
      <section className="w-full py-16 px-4 sm:px-8 max-w-5xl mx-auto flex flex-col gap-12">
        <div className="text-center flex flex-col items-center gap-2">
          <span className="text-xs font-bold text-[#2D8BFF] uppercase tracking-wider">
            كيف يعمل سالم؟
          </span>
          <h2 className="text-2xl sm:text-3xl font-black text-[#061A3A]">
            سالم لا يعتمد على التخمين.
          </h2>
          <p className="text-sm text-[#5F708C] max-w-lg leading-relaxed">
            يبحث سالم في مصادر إكلينيكية موثوقة قبل تقديم المعلومة أو التدخل السلوكي المناسب لك.
          </p>
        </div>

        {/* 5-Step Process */}
        <div className="grid grid-cols-1 sm:grid-cols-5 gap-4">
          {[
            { step: '1', title: 'يفهم حالتك', desc: 'يستوعب دوافعك ونمط تدخينك ومحفزاتك' },
            { step: '2', title: 'يبحث في المصادر', desc: 'يراجع إرشادات WHO الإكلينيكية 2024' },
            { step: '3', title: 'يتحقق من المعلومة', desc: 'يطابق السلامة والجرعات بدقة' },
            { step: '4', title: 'يحدد الخطوة', desc: 'يقترح تدخلاً سلوكياً يناسب لحظتك' },
            { step: '5', title: 'يتابع تقدمك', desc: 'يرافقك يوميًا في خطتك الشخصية' },
          ].map((item) => (
            <div
              key={item.step}
              className="bg-[#FFFFFF] border border-[#D9E2F0] rounded-3xl p-5 shadow-xs flex flex-col items-start gap-3 text-right"
            >
              <div className="w-8 h-8 rounded-xl bg-[#2D8BFF]/10 text-[#1E3A8A] font-black text-sm flex items-center justify-center">
                {item.step}
              </div>
              <h3 className="text-sm font-bold text-[#061A3A]">{item.title}</h3>
              <p className="text-xs text-[#5F708C] leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Clinical Grounding & Trust */}
      <section className="w-full bg-[#FFFFFF] border-y border-[#D9E2F0] py-16 px-4 sm:px-8">
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row items-center justify-between gap-8">
          <div className="flex-1 flex flex-col gap-4 text-right">
            <div className="w-12 h-12 rounded-2xl bg-[#34D399]/15 text-[#047857] flex items-center justify-center">
              <BookOpen className="w-6 h-6" />
            </div>
            <h2 className="text-2xl font-black text-[#061A3A]">
              مرجعية طبية مثبتة من منظمة الصحة العالمية
            </h2>
            <p className="text-xs sm:text-sm text-[#5F708C] leading-relaxed">
              كل معلومة وتوصية يقدمها سالم مستندة تماماً إلى أحدث بروتوكولات الإقلاع عن التبغ للبالغين الصادرة عن منظمة الصحة العالمية (WHO Clinical Treatment Guideline 2024).
            </p>
          </div>

          <div className="flex-1 w-full max-w-md bg-[#F4F7FB] border border-[#D9E2F0] rounded-3xl p-6 flex flex-col gap-3">
            <div className="flex items-center gap-2 text-xs font-bold text-[#061A3A]">
              <CheckCircle2 className="w-4 h-4 text-[#34D399]" />
              <span>مبني على أدلة علاجية وسلوكية معتمدة</span>
            </div>
            <div className="flex items-center gap-2 text-xs font-bold text-[#061A3A]">
              <CheckCircle2 className="w-4 h-4 text-[#34D399]" />
              <span>سرية تامة وأمان كامل لبياناتك</span>
            </div>
            <div className="flex items-center gap-2 text-xs font-bold text-[#061A3A]">
              <CheckCircle2 className="w-4 h-4 text-[#34D399]" />
              <span>دعم غير مشروط وبدون أي لوم عند الانتكاس</span>
            </div>
          </div>
        </div>
      </section>

      {/* Footer CTA */}
      <footer className="w-full py-12 px-4 sm:px-8 text-center flex flex-col items-center gap-5">
        <h3 className="text-xl font-bold text-[#061A3A]">
          جاهز لبدء حياة صحية جديدة بدون تدخين؟
        </h3>
        <button
          type="button"
          onClick={onStartApp}
          className="h-12 px-8 rounded-2xl bg-[#2D8BFF] hover:bg-[#1E7AE6] active:bg-[#1569CC] text-white text-sm font-bold flex items-center justify-center gap-2 shadow-xs transition-all duration-150 active:scale-95 cursor-pointer"
        >
          <span>ابدأ الآن مع سالم</span>
          <ArrowLeft className="w-4 h-4" />
        </button>
        <p className="text-xs text-[#8291A8] pt-2">
          سالم · المساعد الطبي السلوكي للإقلاع عن التدخين · 2026
        </p>
      </footer>
    </div>
  );
};
