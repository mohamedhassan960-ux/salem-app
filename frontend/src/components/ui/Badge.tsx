import type { HTMLAttributes, ReactNode } from 'react';

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  children: ReactNode;
  variant?: 'primary' | 'navy' | 'success' | 'warning' | 'error' | 'neutral';
  size?: 'sm' | 'md';
}

export const Badge = ({
  children,
  variant = 'neutral',
  size = 'sm',
  className = '',
  ...props
}: BadgeProps) => {
  const variantClasses = {
    primary: 'bg-[#2D8BFF]/10 text-[#1E3A8A] border-[#2D8BFF]/30',
    navy: 'bg-[#061A3A]/10 text-[#061A3A] border-[#061A3A]/20',
    success: 'bg-[#34D399]/15 text-[#047857] border-[#34D399]/30',
    warning: 'bg-[#FBBF24]/15 text-[#B45309] border-[#FBBF24]/30',
    error: 'bg-[#F87171]/15 text-[#B91C1C] border-[#F87171]/30',
    neutral: 'bg-[#F1F5FA] text-[#5F708C] border-[#D9E2F0]',
  };

  const sizeClasses = {
    sm: 'px-2.5 py-0.5 text-xs font-semibold rounded-full',
    md: 'px-3 py-1 text-sm font-semibold rounded-full',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 border font-arabic select-none ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      {...props}
    >
      {children}
    </span>
  );
};
