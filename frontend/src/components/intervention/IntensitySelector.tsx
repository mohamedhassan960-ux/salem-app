export interface IntensitySelectorProps {
  value: number;
  onChange: (val: number) => void;
  label?: string;
  className?: string;
}

export const IntensitySelector = ({
  value,
  onChange,
  label = 'شدة الرغبة الحالية',
  className = '',
}: IntensitySelectorProps) => {
  const levels = [
    { num: 1, label: 'خفيفة جداً' },
    { num: 3, label: 'خفيفة' },
    { num: 5, label: 'متوسطة' },
    { num: 7, label: 'قوية' },
    { num: 9, label: 'قوية جداً' },
    { num: 10, label: 'قصوى' },
  ];

  return (
    <div className={`flex flex-col gap-2 font-arabic select-none ${className}`} dir="rtl">
      <div className="flex items-center justify-between">
        <label className="text-xs font-bold text-[#061A3A]">{label}</label>
        <span className="text-xs font-extrabold text-[#2D8BFF]">
          {value} من 10
        </span>
      </div>

      <div className="grid grid-cols-6 gap-1.5">
        {levels.map((item) => {
          const isSelected = value === item.num;
          return (
            <button
              key={item.num}
              type="button"
              onClick={() => onChange(item.num)}
              className={`
                min-h-[44px] h-11 rounded-xl border flex flex-col items-center justify-center transition-all duration-150 cursor-pointer
                ${
                  isSelected
                    ? 'bg-[#2D8BFF] text-white border-[#2D8BFF] font-bold shadow-xs'
                    : 'bg-[#F4F7FB] border-[#D9E2F0] text-[#061A3A] hover:border-[#C4D1E3]'
                }
              `}
              aria-label={`شدة الرغبة ${item.num}: ${item.label}`}
            >
              <span className="text-xs font-bold">{item.num}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
