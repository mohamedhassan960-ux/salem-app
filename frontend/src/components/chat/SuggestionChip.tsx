export interface SuggestionChipProps {
  text: string;
  onClick: (text: string) => void;
  className?: string;
}

export const SuggestionChip = ({
  text,
  onClick,
  className = '',
}: SuggestionChipProps) => {
  return (
    <button
      type="button"
      onClick={() => onClick(text)}
      className={`px-3.5 py-2 rounded-xl text-xs font-semibold font-arabic bg-slate-900/90 hover:bg-slate-800 active:bg-slate-900 text-slate-200 hover:text-sky-300 active:text-sky-400 border border-slate-800 hover:border-sky-500/40 shadow-sm shadow-slate-950/50 transition-all duration-200 cursor-pointer active:scale-95 text-right whitespace-normal leading-relaxed ${className}`}
      dir="rtl"
    >
      {text}
    </button>
  );
};
