import type { HTMLAttributes } from 'react';

export interface SkeletonProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'text' | 'circular' | 'rounded';
}

export const Skeleton = ({
  variant = 'rounded',
  className = '',
  ...props
}: SkeletonProps) => {
  const variantClasses = {
    text: 'h-4 rounded-md',
    circular: 'rounded-full',
    rounded: 'rounded-xl',
  };

  return (
    <div
      className={`bg-[#E8EFF8] animate-pulse ${variantClasses[variant]} ${className}`}
      {...props}
    />
  );
};
