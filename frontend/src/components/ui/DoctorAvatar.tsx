export interface DoctorAvatarProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showStatus?: boolean;
  className?: string;
}

export const DoctorAvatar = ({
  size = 'md',
  showStatus = true,
  className = '',
}: DoctorAvatarProps) => {
  const sizeMap = {
    sm: 'w-9 h-9',
    md: 'w-11 h-11',
    lg: 'w-16 h-16',
    xl: 'w-24 h-24',
  };

  const badgeSizeMap = {
    sm: 'w-2.5 h-2.5 -bottom-0.5 -left-0.5',
    md: 'w-3.5 h-3.5 -bottom-0.5 -left-0.5',
    lg: 'w-4 h-4 bottom-0 left-0',
    xl: 'w-5 h-5 bottom-1 left-1',
  };

  return (
    <div className={`relative inline-flex items-center justify-center shrink-0 ${className}`}>
      <div
        className={`${sizeMap[size]} rounded-full p-[2px] bg-gradient-to-tr from-sky-400 via-blue-500 to-sky-300 shadow-lg shadow-sky-950/50`}
      >
        <div className="w-full h-full rounded-full bg-white overflow-hidden flex items-center justify-center border border-slate-700/50">
          <img
            src="/logo.png"
            alt="سالم"
            className="w-full h-full object-cover object-top"
            loading="eager"
          />
        </div>
      </div>

      {showStatus && (
        <span
          className={`absolute ${badgeSizeMap[size]} bg-emerald-500 border-2 border-slate-900 rounded-full shadow-sm shadow-emerald-950/50`}
          title="سالم متصل"
        >
          <span className="absolute inset-0 rounded-full bg-emerald-400 animate-ping opacity-75" />
        </span>
      )}
    </div>
  );
};
