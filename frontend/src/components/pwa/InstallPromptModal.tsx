import { useState, useEffect } from 'react';
import { Surface } from '../ui/Surface';
import { Button } from '../ui/Button';
import { Download, X } from 'lucide-react';

const INSTALL_DISMISSED_KEY = 'oxygen_pwa_install_dismissed_v1';

export const InstallPromptModal = () => {
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const isDismissed = localStorage.getItem(INSTALL_DISMISSED_KEY) === 'true';
    if (isDismissed) return;

    const handleBeforeInstall = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setIsVisible(true);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstall);
    return () => window.removeEventListener('beforeinstallprompt', handleBeforeInstall);
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === 'accepted') {
      localStorage.setItem(INSTALL_DISMISSED_KEY, 'true');
    }
    setIsVisible(false);
    setDeferredPrompt(null);
  };

  const handleDismiss = () => {
    localStorage.setItem(INSTALL_DISMISSED_KEY, 'true');
    setIsVisible(false);
  };

  if (!isVisible) return null;

  return (
    <div
      className="fixed bottom-20 left-4 right-4 max-w-sm mx-auto z-40 animate-in slide-in-from-bottom-3 duration-300 select-none"
      dir="rtl"
    >
      <Surface
        variant="elevated"
        padding="md"
        rounded="2xl"
        className="bg-slate-900/95 backdrop-blur-md border border-sky-500/30 shadow-2xl shadow-black/60 flex flex-col gap-3"
      >
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-xl bg-sky-500/15 border border-sky-500/30 flex items-center justify-center text-sky-400 shrink-0">
              <Download className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-white font-arabic">ثبّت التطبيق على هاتفك</h4>
              <p className="text-[11px] text-slate-300 font-arabic leading-tight">
                للوصول السريع إلى د. سالم وتجربة تطبيق مستقلة.
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={handleDismiss}
            aria-label="إغلاق نافذة التثبيت"
            className="text-slate-400 hover:text-white p-1 cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="flex items-center gap-2 pt-1">
          <Button
            variant="primary"
            size="sm"
            fullWidth
            onClick={handleInstall}
            className="font-bold text-xs h-9 min-h-[36px]"
          >
            تثبيت
          </Button>
          <Button
            variant="secondary"
            size="sm"
            fullWidth
            onClick={handleDismiss}
            className="text-xs h-9 min-h-[36px]"
          >
            ليس الآن
          </Button>
        </div>
      </Surface>
    </div>
  );
};
