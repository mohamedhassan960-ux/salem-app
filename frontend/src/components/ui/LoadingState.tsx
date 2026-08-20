import { Loader2 } from 'lucide-react';

export interface LoadingStateProps {
  message?: string;
  className?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'ÌÇÑí ÇáÊÍãíá...',
  className = '',
}) => {
  return (
    <div className={`flex flex-col items-center justify-center p-8 gap-3 text-center ${className}`}>
      <div className="relative flex items-center justify-center">
        <div className="w-10 h-10 rounded-full border-2 border-sky-500/20 border-t-sky-500 animate-spin" />
        <Loader2 className="w-5 h-5 text-sky-400 absolute animate-pulse" />
      </div>
      <p className="text-sm font-medium text-slate-400 font-arabic">{message}</p>
    </div>
  );
};
