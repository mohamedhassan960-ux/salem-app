import type { ButtonHTMLAttributes, ReactNode } from 'react';
import { Loader2 } from 'lucide-react';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'navy';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  isLoading?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
}

export const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  isLoading = false,
  leftIcon,
  rightIcon,
  className = '',
  disabled,
  ...props
}: ButtonProps) => {
  const sizeClasses = {
    sm: 'h-10 px-3.5 text-xs gap-1.5 min-h-[40px] rounded-lg',
    md: 'h-12 px-5 text-sm font-semibold gap-2 min-h-[44px] rounded-xl',
    lg: 'h-14 px-6 text-base font-semibold gap-2.5 min-h-[48px] rounded-xl',
  };

  const variantClasses = {
    primary:
      'bg-[#2D8BFF] hover:bg-[#1E7AE6] active:bg-[#1569CC] text-white shadow-sm border border-[#2D8BFF] focus-visible:ring-2 focus-visible:ring-[#2D8BFF]/40',
    navy:
      'bg-[#061A3A] hover:bg-[#0B2454] active:bg-[#0F2D5E] text-white shadow-sm border border-[#061A3A] focus-visible:ring-2 focus-visible:ring-[#061A3A]/30',
    secondary:
      'bg-[#F4F7FB] hover:bg-[#E8EFF8] active:bg-[#DCE7F5] text-[#061A3A] border border-[#D9E2F0] focus-visible:ring-2 focus-visible:ring-[#1E3A8A]/20',
    outline:
      'bg-transparent hover:bg-[#F4F7FB] active:bg-[#E8EFF8] text-[#1E3A8A] border border-[#C4D1E3] focus-visible:ring-2 focus-visible:ring-[#1E3A8A]/20',
    ghost:
      'bg-transparent hover:bg-[#F4F7FB] active:bg-[#E8EFF8] text-[#5F708C] hover:text-[#061A3A] border-transparent focus-visible:ring-2 focus-visible:ring-[#1E3A8A]/20',
    danger:
      'bg-[#F87171] hover:bg-[#EF4444] active:bg-[#DC2626] text-white shadow-sm border border-[#F87171] focus-visible:ring-2 focus-visible:ring-[#F87171]/40',
  };

  return (
    <button
      disabled={disabled || isLoading}
      className={`
        inline-flex items-center justify-center font-arabic transition-all duration-150 cursor-pointer
        active:scale-[0.98] touch-manipulation select-none outline-none
        disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100
        ${fullWidth ? 'w-full' : ''}
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        ${className}
      `}
      {...props}
    >
      {isLoading ? (
        <Loader2 className="w-4 h-4 animate-spin shrink-0" />
      ) : (
        <>
          {leftIcon && <span className="shrink-0">{leftIcon}</span>}
          <span>{children}</span>
          {rightIcon && <span className="shrink-0">{rightIcon}</span>}
        </>
      )}
    </button>
  );
};
