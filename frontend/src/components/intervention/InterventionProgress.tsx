export interface InterventionProgressProps {
  currentStep: number;
  totalSteps: number;
  className?: string;
}

export const InterventionProgress = ({
  currentStep,
  totalSteps,
  className = '',
}: InterventionProgressProps) => {
  return (
    <div className={`flex items-center gap-3 font-arabic select-none ${className}`} dir="rtl">
      <div className="flex items-center gap-1.5" aria-hidden="true">
        {Array.from({ length: totalSteps }).map((_, i) => (
          <div
            key={i}
            className={`h-2 rounded-full transition-all duration-300 ${
              i + 1 === currentStep
                ? 'w-7 bg-[#2D8BFF]'
                : i + 1 < currentStep
                ? 'w-2.5 bg-[#1E3A8A]'
                : 'w-2.5 bg-[#D9E2F0]'
            }`}
          />
        ))}
      </div>
      <span className="text-xs font-bold text-[#5F708C]" aria-label={`الخطوة ${currentStep} من ${totalSteps}`}>
        الخطوة {currentStep} من {totalSteps}
      </span>
    </div>
  );
};
