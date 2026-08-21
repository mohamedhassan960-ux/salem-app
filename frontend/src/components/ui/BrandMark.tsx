export interface BrandMarkProps {
  showSubtitle?: boolean;
  theme?: 'light' | 'navy';
  className?: string;
}

export const BrandMark = ({
  showSubtitle = true,
  theme = 'light',
  className = '',
}: BrandMarkProps) => {
  const isLight = theme === 'light';

  return (
    <div className={`flex flex-col items-start select-none font-arabic ${className}`} dir="rtl">
      <div className="flex items-center gap-2">
        <span
          className={`text-xl font-bold tracking-tight ${
            isLight ? 'text-[#061A3A]' : 'text-white'
          }`}
        >
          سالم
        </span>
        <span
          className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold border ${
            isLight
              ? 'bg-[#2D8BFF]/10 text-[#1E3A8A] border-[#2D8BFF]/25'
              : 'bg-white/10 text-white border-white/20'
          }`}
        >
          مساعدك للإقلاع
        </span>
      </div>
      {showSubtitle && (
        <span
          className={`text-xs font-normal mt-0.5 ${
            isLight ? 'text-[#5F708C]' : 'text-[#A5C1FF]'
          }`}
        >
          دعم علمي وسلوكي خطوة بخطوة
        </span>
      )}
    </div>
  );
};
