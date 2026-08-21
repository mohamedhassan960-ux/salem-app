import type { HTMLAttributes } from 'react';

export interface DividerProps extends HTMLAttributes<HTMLDivElement> {
  label?: string;
}

export const Divider = ({ label, className = '', ...props }: DividerProps) => {
  if (!label) {
    return <hr className={`border-t border-[#D9E2F0] my-3 ${className}`} {...props} />;
  }

  return (
    <div className={`relative flex items-center justify-center my-4 font-arabic ${className}`} {...props}>
      <div className="absolute inset-0 flex items-center">
        <div className="w-full border-t border-[#D9E2F0]" />
      </div>
      <span className="relative bg-[#F7F9FC] px-3 text-xs text-[#8291A8] font-medium">
        {label}
      </span>
    </div>
  );
};
