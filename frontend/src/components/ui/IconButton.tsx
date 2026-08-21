import type { ButtonHTMLAttributes, ReactNode } from 'react';

export interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  'aria-label': string;
  variant?: 'default' | 'subtle' | 'navy' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
}

export const IconButton = ({
  children,
  'aria-label': ariaLabel,
  variant = 'default',
  size = 'md',
  className = '',
  disabled,
  ...props
}: IconButtonProps) => {
  const sizeClasses = {
    sm: 'w-9 h-9 min-w-[36px] min-h-[36px] p-1.5 rounded-lg',
    md: 'w-11 h-11 min-w-[44px] min-h-[44px] p-2.5 rounded-xl',
    lg: 'w-13 h-13 min-w-[52px] min-h-[52px] p-3 rounded-xl',
  };

  const variantClasses = {
    default: 'bg-[#FFFFFF] hover:bg-[#F4F7FB] active:bg-[#E8EFF8] text-[#061A3A] border border-[#D9E2F0] shadow-sm',
    subtle: 'bg-[#F1F5FA] hover:bg-[#E8EFF8] active:bg-[#DCE7F5] text-[#5F708C] hover:text-[#061A3A] border border-[#D9E2F0]',
    navy: 'bg-[#061A3A] hover:bg-[#0B2454] active:bg-[#0F2D5E] text-white border border-[#061A3A]',
    ghost: 'bg-transparent hover:bg-[#F1F5FA] active:bg-[#E8EFF8] text-[#5F708C] hover:text-[#061A3A] border-transparent',
  };

  return (
    <button
      aria-label={ariaLabel}
      disabled={disabled}
      className={`
        inline-flex items-center justify-center transition-all duration-150 cursor-pointer
        active:scale-[0.96] touch-manipulation select-none outline-none
        focus-visible:ring-2 focus-visible:ring-[#2D8BFF]/40
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
