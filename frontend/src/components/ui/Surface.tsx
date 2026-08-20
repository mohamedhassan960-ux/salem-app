import type { HTMLAttributes } from 'react';

export interface SurfaceProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'base' | 'card' | 'elevated' | 'glass';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  rounded?: 'none' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full';
}

export const Surface = ({
  children,
  variant = 'card',
  padding = 'md',
  rounded = 'xl',
  className = '',
  ...props
}: SurfaceProps) => {
  const variantClasses = {
    base: 'bg-slate-950/80 border border-slate-800/80',
    card: 'bg-slate-900/90 border border-slate-800/90 shadow-sm shadow-slate-950/40',
    elevated: 'bg-slate-800/90 border border-slate-700/60 shadow-lg shadow-slate-950/60',
    glass: 'bg-slate-900/75 backdrop-blur-md border border-slate-700/40 shadow-md shadow-slate-950/50',
  };

  const paddingClasses = {
    none: 'p-0',
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
  };

  const roundedClasses = {
    none: 'rounded-none',
    sm: 'rounded-lg',
    md: 'rounded-xl',
    lg: 'rounded-2xl',
    xl: 'rounded-3xl',
    '2xl': 'rounded-[2rem]',
    full: 'rounded-full',
  };

  return (
    <div
      className={`
        transition-colors
        ${variantClasses[variant]}
        ${paddingClasses[padding]}
        ${roundedClasses[rounded]}
        ${className}
      `}
      {...props}
    >
      {children}
    </div>
  );
};
