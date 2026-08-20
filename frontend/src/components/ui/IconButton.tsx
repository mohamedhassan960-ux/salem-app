import type { ButtonHTMLAttributes } from 'react';

export interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'ghost' | 'filled' | 'outline' | 'primary';
  size?: 'sm' | 'md' | 'lg';
  ariaLabel: string;
}

export const IconButton = ({
  children,
  variant = 'ghost',
  size = 'md',
  ariaLabel,
  className = '',
  ...props
}: IconButtonProps) => {
  const sizeClasses = {
    sm: 'w-10 h-10 min-w-[40px] min-h-[40px]',
    md: 'w-11 h-11 min-w-[44px] min-h-[44px]',
    lg: 'w-12 h-12 min-w-[48px] min-h-[48px]',
  };

  const variantClasses = {
    ghost: 'text-slate-300 hover:text-white hover:bg-slate-800/60 active:bg-slate-800',
    filled: 'bg-slate-800/90 text-slate-200 hover:bg-slate-700 active:bg-slate-800 border border-slate-700/50',
    outline: 'border border-slate-700 text-slate-300 hover:text-white hover:bg-slate-800/40 active:bg-slate-800',
    primary: 'bg-sky-500 text-white hover:bg-sky-400 active:bg-sky-600 shadow-md shadow-sky-950/40',
  };

  return (
    <button
      type="button"
      aria-label={ariaLabel}
      className={`
        inline-flex items-center justify-center rounded-xl transition-all duration-200 cursor-pointer
        active:scale-95 touch-manipulation focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-500
        disabled:opacity-40 disabled:cursor-not-allowed disabled:active:scale-100
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        ${className}
      `}
      {...props}
    >
      {children}
    </button>
  );
};
