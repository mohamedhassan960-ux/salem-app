import { forwardRef, type InputHTMLAttributes, type ReactNode } from 'react';
import { AlertCircle } from 'lucide-react';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  startIcon?: ReactNode;
  endIcon?: ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, startIcon, endIcon, className = '', id, disabled, ...props }, ref) => {
    const inputId = id || (label ? `input_${label.replace(/\s+/g, '_')}` : undefined);

    return (
      <div className="w-full flex flex-col gap-1.5 font-arabic" dir="rtl">
        {label && (
          <label htmlFor={inputId} className="text-sm font-medium text-[#061A3A] select-none">
            {label}
          </label>
        )}

        <div className="relative flex items-center w-full">
          {startIcon && (
            <div className="absolute right-3.5 flex items-center pointer-events-none text-[#8291A8]">
              {startIcon}
            </div>
          )}

          <input
            ref={ref}
            id={inputId}
            disabled={disabled}
            className={`
              w-full h-12 bg-[#F1F5FA] text-[#061A3A] text-sm rounded-xl border transition-all duration-150 outline-none
              placeholder:text-[#8291A8]
              focus:bg-[#FFFFFF] focus:border-[#2D8BFF] focus:ring-2 focus:ring-[#2D8BFF]/20
              disabled:opacity-50 disabled:bg-[#E8EFF8] disabled:cursor-not-allowed
              ${startIcon ? 'pr-11' : 'pr-4'}
              ${endIcon || error ? 'pl-11' : 'pl-4'}
              ${error ? 'border-[#F87171] focus:border-[#F87171] focus:ring-[#F87171]/20' : 'border-[#D9E2F0]'}
              ${className}
            `}
            {...props}
          />

          {error ? (
            <div className="absolute left-3.5 flex items-center pointer-events-none text-[#F87171]">
              <AlertCircle className="w-4 h-4" />
            </div>
          ) : endIcon ? (
            <div className="absolute left-3.5 flex items-center text-[#8291A8]">
              {endIcon}
            </div>
          ) : null}
        </div>

        {error ? (
          <span className="text-xs text-[#F87171] flex items-center gap-1 mt-0.5">
            {error}
          </span>
        ) : helperText ? (
          <span className="text-xs text-[#5F708C] mt-0.5">
            {helperText}
          </span>
        ) : null}
      </div>
    );
  }
);

Input.displayName = 'Input';
