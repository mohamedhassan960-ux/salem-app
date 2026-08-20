export interface BrandMarkProps {
  showSubtitle?: boolean;
  className?: string;
}

export const BrandMark = ({
  showSubtitle = true,
  className = '',
}: BrandMarkProps) => {
  return (
    <div className={`flex flex-col items-start select-none ${className}`} dir="rtl">
      <div className="flex items-center gap-2">
        <span className="text-xl font-extrabold tracking-tight text-white font-arabic">
          سالم
        </span>
        <span className="inline-flex items-center px-1.5 py-0.5 rounded-md text-[10px] font-bold bg-sky-500/15 text-sky-400 border border-sky-500/30 tracking-wide">
          المساعد الطبي
        </span>
      </div>
      {showSubtitle && (
        <span className="text-[11px] font-medium text-slate-400 leading-tight">
          رفيقك للإقلاع عن التدخين
        </span>
      )}
    </div>
  );
};
