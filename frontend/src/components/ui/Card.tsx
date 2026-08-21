import type { HTMLAttributes, ReactNode } from 'react';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  variant?: 'default' | 'subtle' | 'navy' | 'interactive';
  selected?: boolean;
}

export const Card = ({
  children,
  variant = 'default',
  selected = false,
  className = '',
  ...props
}: CardProps) => {
  const variantClasses = {
    default: 'bg-[#FFFFFF] border-[#D9E2F0] text-[#061A3A] shadow-sm',
    subtle: 'bg-[#F4F7FB] border-[#D9E2F0] text-[#061A3A]',
    navy: 'bg-[#061A3A] border-[#0F2D5E] text-white shadow-md',
    interactive:
      'bg-[#FFFFFF] border-[#D9E2F0] hover:border-[#4D9BFF] hover:shadow-md cursor-pointer transition-all duration-150 active:scale-[0.99] text-[#061A3A]',
  };

  const selectedClass = selected
    ? 'ring-2 ring-[#2D8BFF] border-[#2D8BFF] bg-[#F4F7FB]'
    : '';

  return (
    <div
      className={`rounded-2xl border p-4 sm:p-5 font-arabic ${variantClasses[variant]} ${selectedClass} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};
