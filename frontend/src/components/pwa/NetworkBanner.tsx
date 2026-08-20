import { useState, useEffect } from 'react';
import { WifiOff, Wifi } from 'lucide-react';

export const NetworkBanner = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [showRestored, setShowRestored] = useState(false);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      setShowRestored(true);
      const timer = setTimeout(() => {
        setShowRestored(false);
      }, 3000);
      return () => clearTimeout(timer);
    };

    const handleOffline = () => {
      setIsOnline(false);
      setShowRestored(false);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (isOnline && !showRestored) return null;

  return (
    <div
      className={`fixed top-0 left-0 right-0 z-50 py-1.5 px-3 flex items-center justify-center gap-2 text-xs font-arabic font-semibold transition-all duration-300 ${
        isOnline
          ? 'bg-emerald-600 text-white shadow-md'
          : 'bg-amber-600 text-white shadow-md'
      }`}
      dir="rtl"
      role="alert"
    >
      {isOnline ? (
        <>
          <Wifi className="w-3.5 h-3.5" />
          <span>تم استعادة الاتصال بالإنترنت</span>
        </>
      ) : (
        <>
          <WifiOff className="w-3.5 h-3.5 animate-pulse" />
          <span>لا يوجد اتصال بالإنترنت · يمكنك استعراض المحادثات المحفوظة</span>
        </>
      )}
    </div>
  );
};
