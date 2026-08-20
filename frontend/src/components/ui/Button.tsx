import type { ButtonHTMLAttributes, ReactNode } from 'react';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
}

export const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  leftIcon,
  rightIcon,
  className = '',
  ...props
}: ButtonProps) => {
  const sizeClasses = {
    sm: 'h-10 px-3 text-xs gap-1.5 min-h-[40px]',
    md: 'h-12 px-4 text-sm gap-2 min-h-[48px]',
    lg: 'h-14 px-6 text-base gap-2.5 min-h-[52px]',
  };

  const variantClasses = {
    primary: 'bg-sky-500 hover:bg-sky-400 active:bg-sky-600 text-white font-semibold shadow-md shadow-sky-950/40 border border-sky-400/30',
    secondary: 'bg-slate-800 hover:bg-slate-700 active:bg-slate-800/90 text-slate-100 font-medium border border-slate-700/60',
    outline: 'border border-sky-500/50 hover:bg-sky-500/10 active:bg-sky-500/20 text-sky-400 font-medium',
    ghost: 'text-slate-300 hover:text-white hover:bg-slate-800/50 active:bg-slate-800',
    danger: 'bg-rose-600 hover:bg-rose-500 active:bg-rose-700 text-white font-semibold shadow-md shadow-rose-950/40',
  };

  return (
    <button
      className={`
        inline-flex items-center justify-center rounded-xl font-arabic transition-all duration-200 cursor-pointer
        active:scale-[0.98] touch-manipulation focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-500
        disabled:opacity-40 disabled:cursor-not-allowed disabled:active:scale-100
        ${fullWidth ? 'w-full' : ''}
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        ${className}
      `}
      {...props}
    >
      {leftIcon && <span className="shrink-0">{leftIcon}</span>}
      <span>{children}</span>
      {rightIcon && <span className="shrink-0">{rightIcon}</span>}
    </button>
  );
};
