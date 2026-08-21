export interface DoctorAvatarProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showStatus?: boolean;
  className?: string;
}

export const DoctorAvatar = ({
  size = 'md',
  showStatus = false,
  className = '',
}: DoctorAvatarProps) => {
  const sizeMap = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-14 h-14',
    xl: 'w-20 h-20',
  };

  const badgeSizeMap = {
    sm: 'w-2 h-2 -bottom-0.5 -left-0.5',
    md: 'w-2.5 h-2.5 -bottom-0.5 -left-0.5',
    lg: 'w-3.5 h-3.5 bottom-0 left-0',
    xl: 'w-4 h-4 bottom-1 left-1',
  };

  return (
    <div className={`relative inline-flex items-center justify-center shrink-0 ${className}`}>
      <div
        className={`${sizeMap[size]} rounded-full p-[1.5px] bg-gradient-to-tr from-[#1E3A8A] via-[#2D8BFF] to-[#7FAFFF] shadow-xs`}
      >
        <div className="w-full h-full rounded-full bg-white overflow-hidden flex items-center justify-center border border-[#D9E2F0]">
          <img
            src="/salem-logo.png"
            alt="سالم"
            className="w-full h-full object-cover object-top"
            loading="eager"
            onError={(e) => {
              // fallback if image not found
              const target = e.currentTarget;
              target.onerror = null;
              target.src = '/logo.png';
            }}
          />
        </div>
      </div>

      {showStatus && (
        <span
          className={`absolute ${badgeSizeMap[size]} bg-[#34D399] border-2 border-white rounded-full`}
          title="سالم جاهز لمساعدتك"
        />
      )}
    </div>
  );
};
