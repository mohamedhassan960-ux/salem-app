import os

files = {}

# ─────────────────────────────────────────────
# 1. main.tsx — fix process.env, register SW with import.meta.env
# ─────────────────────────────────────────────
files['src/main.tsx'] = """import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.tsx';
import { AuthProvider } from './context/AuthContext.tsx';

// Register PWA Service Worker only in production
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => {
      // Silently ignore SW registration failures (localhost / dev)
    });
  });
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </StrictMode>,
);
"""

# ─────────────────────────────────────────────
# 2. App.tsx — add missing imports, add body-scroll-lock when sidebar open,
#              fix settings wrapping (use full-screen not AppShell),
#              tighten offline-splash wrapping
# ─────────────────────────────────────────────
files['src/App.tsx'] = """import { useState, useEffect } from 'react';
import { useAuth } from './context/AuthContext';
import { SplashScreen } from './components/entry/SplashScreen';
import { OnboardingScreen } from './components/entry/OnboardingScreen';
import { LoginScreen } from './components/entry/LoginScreen';
import { AppShell } from './components/layout/AppShell';
import { ChatScreen } from './components/chat/ChatScreen';
import { SidebarDrawer } from './components/drawer/SidebarDrawer';
import { LogoutDialog } from './components/drawer/LogoutDialog';
import { SettingsScreen } from './components/settings/SettingsScreen';
import { NetworkBanner } from './components/pwa/NetworkBanner';
import { InstallPromptModal } from './components/pwa/InstallPromptModal';
import type { EntryStep } from './types/auth';
import type { ConversationSession } from './types/chat';

export function App() {
  const { user, hasSeenOnboarding, markOnboardingComplete, signOut } = useAuth();
  const [currentStep, setCurrentStep] = useState<EntryStep>('splash');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isLogoutDialogOpen, setIsLogoutDialogOpen] = useState(false);

  // Lock body scroll when sidebar is open
  useEffect(() => {
    if (isSidebarOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => { document.body.style.overflow = ''; };
  }, [isSidebarOpen]);

  const [conversations] = useState<ConversationSession[]>([
    {
      id: 'conv_1',
      title: 'كيفية البدء في خطة الإقلاع',
      group: 'اليوم',
      createdAt: Date.now() - 3600000,
      updatedAt: Date.now() - 3600000,
      messages: [
        {
          id: 'm1',
          role: 'user',
          content: 'عايز أبدأ خطة إقلاع تدريجية بدون توتر كبير.',
          timestamp: Date.now() - 3600000,
        },
        {
          id: 'm2',
          role: 'assistant',
          content: 'أهلاً بيك! التوقف التدريجي مع وضع تاريخ محدد للهدف (Quit Date) من أنجح الطرق المعتمدة في دليل WHO 2024.',
          timestamp: Date.now() - 3500000,
        },
      ],
    },
    {
      id: 'conv_2',
      title: 'التعامل مع أعراض الانسحاب والصداع',
      group: 'اليوم',
      createdAt: Date.now() - 7200000,
      updatedAt: Date.now() - 7200000,
      messages: [
        {
          id: 'm3',
          role: 'user',
          content: 'الصداع والعصبية بيزيدوا معايا بالليل، إيه الحل؟',
          timestamp: Date.now() - 7200000,
        },
      ],
    },
    {
      id: 'conv_3',
      title: 'بدائل النيكوتين (NRT) واللصقات',
      group: 'أمس',
      createdAt: Date.now() - 86400000,
      updatedAt: Date.now() - 86400000,
      messages: [],
    },
    {
      id: 'conv_4',
      title: 'خطة التوقف التدريجي خلال أسبوعين',
      group: 'هذا الأسبوع',
      createdAt: Date.now() - 259200000,
      updatedAt: Date.now() - 259200000,
      messages: [],
    },
  ]);

  const [activeConversationId, setActiveConversationId] = useState<string | null>('conv_1');
  const activeConversation = conversations.find((c) => c.id === activeConversationId) || null;

  const handleSplashComplete = () => {
    if (user) {
      setCurrentStep('chat_ready');
    } else if (!hasSeenOnboarding) {
      setCurrentStep('onboarding');
    } else {
      setCurrentStep('login');
    }
  };

  const handleOnboardingComplete = () => {
    markOnboardingComplete();
    setCurrentStep('login');
  };

  const handleLoginSuccess = () => setCurrentStep('chat_ready');
  const handleMenuToggle = () => setIsSidebarOpen((prev) => !prev);

  const handleSelectConversation = (conv: ConversationSession) => {
    setActiveConversationId(conv.id);
    setIsSidebarOpen(false);
  };

  const handleNewConversation = () => {
    setActiveConversationId(null);
    setIsSidebarOpen(false);
  };

  const handleOpenSettings = () => {
    setIsSidebarOpen(false);
    setCurrentStep('settings');
  };

  const handleOpenLogout = () => {
    setIsSidebarOpen(false);
    setIsLogoutDialogOpen(true);
  };

  const handleConfirmLogout = () => {
    setIsLogoutDialogOpen(false);
    signOut();
    setCurrentStep('login');
  };

  // ── Full-screen entry flows (no AppShell chrome) ──
  if (currentStep === 'splash') {
    return <SplashScreen onComplete={handleSplashComplete} />;
  }
  if (currentStep === 'onboarding') {
    return <OnboardingScreen onComplete={handleOnboardingComplete} />;
  }
  if (currentStep === 'login') {
    return <LoginScreen onSuccess={handleLoginSuccess} />;
  }

  // ── Settings ──
  if (currentStep === 'settings') {
    return (
      <>
        <div className="w-full h-[100dvh] flex justify-center bg-slate-950 overflow-hidden">
          <div className="w-full max-w-[440px] h-full flex flex-col bg-slate-900 shadow-2xl border-x border-slate-800/80 overflow-hidden">
            <SettingsScreen
              onBack={() => setCurrentStep('chat_ready')}
              onOpenLogoutDialog={handleOpenLogout}
            />
          </div>
        </div>
        <LogoutDialog
          isOpen={isLogoutDialogOpen}
          onConfirm={handleConfirmLogout}
          onCancel={() => setIsLogoutDialogOpen(false)}
        />
        <NetworkBanner />
      </>
    );
  }

  // ── Primary: Chat + Drawer ──
  return (
    <>
      <AppShell isMenuOpen={isSidebarOpen} onMenuClick={handleMenuToggle}>
        <ChatScreen activeConversation={activeConversation} />
      </AppShell>

      <SidebarDrawer
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
        onOpenSettings={handleOpenSettings}
        onOpenLogoutDialog={handleOpenLogout}
      />

      <LogoutDialog
        isOpen={isLogoutDialogOpen}
        onConfirm={handleConfirmLogout}
        onCancel={() => setIsLogoutDialogOpen(false)}
      />

      <NetworkBanner />
      <InstallPromptModal />
    </>
  );
}

export default App;
"""

# ─────────────────────────────────────────────
# 3. index.html — add manifest link, apple touch icon, fix theme-color
# ─────────────────────────────────────────────
files['index.html'] = """<!doctype html>
<html lang="ar" dir="rtl">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
    <meta name="theme-color" content="#0b1329" />
    <meta name="apple-mobile-web-app-capable" content="yes" />
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
    <meta name="apple-mobile-web-app-title" content="أوكسجين" />
    <meta name="format-detection" content="telephone=no" />
    <meta name="description" content="المساعد الطبي للإقلاع عن التدخين — مستند إلى إرشادات منظمة الصحة العالمية 2024" />
    <link rel="manifest" href="/manifest.json" />
    <link rel="icon" type="image/svg+xml" href="/icon-192.svg" />
    <link rel="apple-touch-icon" href="/icon-192.svg" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
    <title>أوكسجين — د. سالم | المساعد الطبي للإقلاع عن التدخين</title>
  </head>
  <body class="bg-slate-950 antialiased">
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
"""

# ─────────────────────────────────────────────
# 4. index.css — add reduced-motion, improve scroll, safe area tokens
# ─────────────────────────────────────────────
files['src/index.css'] = """@import "tailwindcss";

@layer theme {
  :root {
    --font-arabic: 'Cairo', system-ui, -apple-system, sans-serif;
    --font-sans: 'Cairo', system-ui, sans-serif;
  }
}

:root {
  --sat: env(safe-area-inset-top, 0px);
  --sar: env(safe-area-inset-right, 0px);
  --sab: env(safe-area-inset-bottom, 0px);
  --sal: env(safe-area-inset-left, 0px);
}

*, *::before, *::after {
  box-sizing: border-box;
}

html {
  height: 100%;
  height: 100dvh;
  overflow: hidden;
  overscroll-behavior: none;
}

body {
  height: 100%;
  height: 100dvh;
  margin: 0;
  padding: 0;
  background-color: #0b1329;
  font-family: 'Cairo', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  overflow: hidden;
  overscroll-behavior: none;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
  user-select: none;
  -webkit-user-select: none;
}

#root {
  height: 100%;
  height: 100dvh;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: stretch;
  background-color: #0b1329;
}

/* Scrollable areas inside the app */
.overflow-y-auto {
  -webkit-overflow-scrolling: touch;
  overscroll-behavior-y: contain;
}

/* Thin, subtle scrollbar for chat */
::-webkit-scrollbar {
  width: 4px;
  height: 4px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.18);
  border-radius: 9999px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(148, 163, 184, 0.35);
}

/* Reduce motion for accessibility */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Textarea auto-grow */
textarea {
  field-sizing: content;
}
"""

# ─────────────────────────────────────────────
# 5. AppShell — fix safe-area double-application, remove redundant sat div
# ─────────────────────────────────────────────
files['src/components/layout/AppShell.tsx'] = """import type { ReactNode } from 'react';
import { MobileHeader } from './MobileHeader';

export interface AppShellProps {
  children: ReactNode;
  onMenuClick?: () => void;
  isMenuOpen?: boolean;
  showHeader?: boolean;
}

export const AppShell = ({
  children,
  onMenuClick,
  isMenuOpen = false,
  showHeader = true,
}: AppShellProps) => {
  return (
    <div className="w-full h-[100dvh] flex justify-center bg-slate-950 overflow-hidden">
      <div className="w-full max-w-[440px] h-full flex flex-col bg-slate-900 shadow-2xl relative border-x border-slate-800/60 overflow-hidden">
        {showHeader && (
          <MobileHeader onMenuClick={onMenuClick} isMenuOpen={isMenuOpen} />
        )}
        <main className="flex-1 w-full overflow-y-auto overflow-x-hidden flex flex-col min-h-0">
          {children}
        </main>
      </div>
    </div>
  );
};
"""

# ─────────────────────────────────────────────
# 6. MobileHeader — proper safe-area top padding, cleaner layout
# ─────────────────────────────────────────────
files['src/components/layout/MobileHeader.tsx'] = """import { MenuButton } from '../ui/MenuButton';
import { DoctorAvatar } from '../ui/DoctorAvatar';
import { BrandMark } from '../ui/BrandMark';

export interface MobileHeaderProps {
  onMenuClick?: () => void;
  isMenuOpen?: boolean;
  className?: string;
}

export const MobileHeader = ({
  onMenuClick,
  isMenuOpen = false,
  className = '',
}: MobileHeaderProps) => {
  return (
    <header
      className={`w-full shrink-0 bg-slate-900/95 backdrop-blur-md border-b border-slate-800/80 px-4 flex items-center justify-between z-30 ${className}`}
      style={{ paddingTop: 'calc(0.875rem + var(--sat))', paddingBottom: '0.875rem' }}
      dir="rtl"
    >
      <div className="flex items-center gap-3 min-w-0">
        <DoctorAvatar size="md" showStatus={true} />
        <BrandMark showSubtitle={true} />
      </div>
      <div className="shrink-0 ml-2">
        <MenuButton onClick={onMenuClick} isOpen={isMenuOpen} />
      </div>
    </header>
  );
};
"""

# ─────────────────────────────────────────────
# 7. SplashScreen — shorter duration, no layout issues
# ─────────────────────────────────────────────
files['src/components/entry/SplashScreen.tsx'] = """import { useEffect } from 'react';
import { DoctorAvatar } from '../ui/DoctorAvatar';

export interface SplashScreenProps {
  onComplete: () => void;
  durationMs?: number;
}

export const SplashScreen = ({
  onComplete,
  durationMs = 1000,
}: SplashScreenProps) => {
  useEffect(() => {
    const timer = setTimeout(onComplete, durationMs);
    return () => clearTimeout(timer);
  }, [onComplete, durationMs]);

  return (
    <div
      className="w-full h-[100dvh] flex flex-col items-center justify-center bg-slate-950 text-white select-none"
      style={{ paddingTop: 'var(--sat)', paddingBottom: 'var(--sab)' }}
      role="status"
      aria-label="جارٍ تحميل أوكسجين"
    >
      <div className="flex flex-col items-center gap-6">
        <div className="relative">
          <div className="absolute -inset-3 rounded-full bg-sky-500/15 blur-xl" />
          <DoctorAvatar size="lg" showStatus={false} />
        </div>

        <div className="flex flex-col items-center gap-1.5 text-center">
          <div className="flex items-center gap-2">
            <h1 className="text-3xl font-extrabold tracking-tight text-white">أوكسجين</h1>
            <span className="px-2 py-0.5 rounded-md text-xs font-bold bg-sky-500/15 text-sky-400 border border-sky-500/25">
              د. سالم
            </span>
          </div>
          <p className="text-sm text-slate-400 font-medium">
            المساعد الطبي للإقلاع عن التدخين
          </p>
        </div>

        <div className="flex items-center gap-2 mt-2">
          <span className="w-1.5 h-1.5 rounded-full bg-sky-500 animate-ping" />
          <span className="text-[11px] text-slate-500">إرشادات WHO 2024</span>
        </div>
      </div>
    </div>
  );
};
"""

# ─────────────────────────────────────────────
# 8. OnboardingScreen — leaner text, better mobile layout
# ─────────────────────────────────────────────
files['src/components/entry/OnboardingScreen.tsx'] = """import { useState } from 'react';
import { Button } from '../ui/Button';
import { ShieldCheck, MessageSquareHeart, Lock } from 'lucide-react';

export interface OnboardingScreenProps {
  onComplete: () => void;
}

const slides = [
  {
    id: 'evidence',
    Icon: ShieldCheck,
    iconColor: 'text-sky-400',
    iconBg: 'bg-sky-500/10 border-sky-500/20',
    badge: 'دليل WHO 2024',
    title: 'مساعدة مبنية على الأدلة',
    body: 'إرشادات طبية موثوقة مستندة لأحدث أدلة منظمة الصحة العالمية للإقلاع الآمن عن التبغ.',
  },
  {
    id: 'natural',
    Icon: MessageSquareHeart,
    iconColor: 'text-emerald-400',
    iconBg: 'bg-emerald-500/10 border-emerald-500/20',
    badge: 'تواصل إنساني',
    title: 'اسأل بلغتك وبكل راحة',
    body: 'تحدث بطبيعتك. دكتور سالم يشرح بدائل النيكوتين والأعراض الانسحابية بأسلوب دافئ ومبسط.',
  },
  {
    id: 'privacy',
    Icon: Lock,
    iconColor: 'text-indigo-400',
    iconBg: 'bg-indigo-500/10 border-indigo-500/20',
    badge: 'أمان وسرية',
    title: 'خصوصيتك أولاً',
    body: 'محادثاتك في بيئة آمنة ومحمية تماماً. نحرص على سرية استفساراتك الصحية.',
  },
];

export const OnboardingScreen = ({ onComplete }: OnboardingScreenProps) => {
  const [index, setIndex] = useState(0);
  const slide = slides[index];
  const isLast = index === slides.length - 1;

  return (
    <div
      className="w-full h-[100dvh] flex flex-col bg-slate-950 text-white select-none"
      style={{ paddingTop: 'var(--sat)', paddingBottom: 'var(--sab)' }}
      dir="rtl"
    >
      {/* Top bar */}
      <div className="flex items-center justify-between px-6 pt-4 pb-2 shrink-0">
        <div className="flex items-center gap-1.5">
          {slides.map((_, i) => (
            <div
              key={i}
              className={`h-1 rounded-full transition-all duration-300 ${
                i === index
                  ? 'w-6 bg-sky-500'
                  : i < index
                  ? 'w-2.5 bg-sky-800'
                  : 'w-2 bg-slate-800'
              }`}
            />
          ))}
        </div>
        {!isLast && (
          <button
            type="button"
            onClick={onComplete}
            className="text-xs font-semibold text-slate-400 hover:text-white px-3 py-2 rounded-lg hover:bg-slate-900 transition-colors cursor-pointer"
          >
            تخطي
          </button>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col items-center justify-center text-center px-8 gap-6">
        <div className={`w-20 h-20 rounded-2xl flex items-center justify-center border ${slide.iconBg}`}>
          <slide.Icon className={`w-10 h-10 ${slide.iconColor}`} />
        </div>

        <div className="flex flex-col items-center gap-2">
          <span className="px-3 py-1 rounded-full text-[11px] font-bold bg-slate-900 text-sky-400 border border-slate-800">
            {slide.badge}
          </span>
          <h2 className="text-xl font-bold text-white tracking-tight">{slide.title}</h2>
          <p className="text-sm text-slate-300 leading-relaxed max-w-[280px]">{slide.body}</p>
        </div>
      </div>

      {/* Actions */}
      <div className="px-6 pb-6 flex flex-col gap-2 shrink-0">
        <Button
          variant="primary"
          size="lg"
          fullWidth
          onClick={() => isLast ? onComplete() : setIndex((i) => i + 1)}
        >
          {isLast ? 'ابدأ الآن' : 'التالي'}
        </Button>
        {index > 0 && (
          <Button variant="ghost" size="sm" fullWidth onClick={() => setIndex((i) => i - 1)}>
            السابق
          </Button>
        )}
      </div>
    </div>
  );
};
"""

# ─────────────────────────────────────────────
# 9. LoginScreen — tighter, cleaner, consistent with brand
# ─────────────────────────────────────────────
files['src/components/entry/LoginScreen.tsx'] = """import { useAuth } from '../../context/AuthContext';
import { DoctorAvatar } from '../ui/DoctorAvatar';
import { GoogleSignInButton } from './GoogleSignInButton';
import { AlertCircle, Lock } from 'lucide-react';

export interface LoginScreenProps {
  onSuccess: () => void;
}

export const LoginScreen = ({ onSuccess }: LoginScreenProps) => {
  const { signInWithGoogle, status, errorMessage } = useAuth();

  const handleLogin = async () => {
    await signInWithGoogle();
    onSuccess();
  };

  return (
    <div
      className="w-full h-[100dvh] flex flex-col justify-between bg-slate-950 text-white select-none"
      style={{ paddingTop: 'var(--sat)', paddingBottom: 'var(--sab)' }}
      dir="rtl"
    >
      {/* Top badge */}
      <div className="pt-6 px-6 flex justify-center">
        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-sky-500/10 text-sky-400 border border-sky-500/20">
          Oxygen Medical RAG
        </span>
      </div>

      {/* Center content */}
      <div className="flex-1 flex flex-col items-center justify-center text-center px-8 gap-5">
        <DoctorAvatar size="lg" showStatus />

        <div className="flex flex-col gap-2">
          <h1 className="text-2xl font-bold text-white tracking-tight">مرحبًا مع د. سالم</h1>
          <p className="text-sm text-slate-300 leading-relaxed max-w-[280px] mx-auto">
            إرشادات طبية مخصصة للإقلاع عن التدخين، مستندة لأدلة منظمة الصحة العالمية 2024.
          </p>
        </div>

        {errorMessage && (
          <div className="w-full max-w-[320px] flex items-center gap-2.5 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs text-right">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{errorMessage}</span>
          </div>
        )}

        <div className="w-full max-w-[320px]">
          <GoogleSignInButton
            onClick={handleLogin}
            isLoading={status === 'loading'}
          />
        </div>
      </div>

      {/* Disclaimer */}
      <div className="px-8 pb-6 text-center">
        <p className="text-[11px] text-slate-500 leading-relaxed flex items-center justify-center gap-1.5 max-w-xs mx-auto">
          <Lock className="w-3 h-3 shrink-0" />
          <span>هذا التطبيق يقدم إرشادات توعوية ولا يُعدّ بديلاً عن الاستشارة الطبية المباشرة.</span>
        </p>
      </div>
    </div>
  );
};
"""

# ─────────────────────────────────────────────
# 10. MobileComposer — fix keyboard/safe-area, proper textarea resizing
# ─────────────────────────────────────────────
files['src/components/chat/MobileComposer.tsx'] = """import { useState, useEffect, useRef } from 'react';
import type { FormEvent, KeyboardEvent } from 'react';
import { Send, Mic } from 'lucide-react';

export interface MobileComposerProps {
  onSendMessage?: (text: string) => void;
  disabled?: boolean;
  placeholder?: string;
  initialValue?: string;
}

export const MobileComposer = ({
  onSendMessage,
  disabled = false,
  placeholder = 'اسأل د. سالم...',
  initialValue = '',
}: MobileComposerProps) => {
  const [text, setText] = useState(initialValue);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (initialValue && initialValue !== text) {
      setText(initialValue);
    }
  }, [initialValue]);

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 120) + 'px';
  }, [text]);

  const canSend = text.trim().length > 0 && !disabled;

  const doSend = () => {
    if (!canSend) return;
    onSendMessage?.(text.trim());
    setText('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    doSend();
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      doSend();
    }
  };

  return (
    <div
      className="w-full shrink-0 bg-slate-900 border-t border-slate-800/80"
      style={{ paddingBottom: 'calc(0.625rem + var(--sab))', paddingTop: '0.625rem', paddingLeft: '0.875rem', paddingRight: '0.875rem' }}
      dir="rtl"
    >
      <form
        onSubmit={handleSubmit}
        className="flex items-end gap-2 bg-slate-800/80 rounded-2xl px-3 py-1.5 border border-slate-700/50 focus-within:border-sky-500/60 focus-within:ring-1 focus-within:ring-sky-500/30 transition-all"
      >
        <textarea
          ref={textareaRef}
          rows={1}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder={placeholder}
          aria-label="اكتب سؤالك الطبي"
          className="flex-1 bg-transparent text-slate-100 placeholder-slate-500 text-sm py-2 focus:outline-none resize-none min-h-[40px] max-h-[120px] leading-relaxed disabled:opacity-50"
          style={{ height: 'auto' }}
        />
        <button
          type="submit"
          disabled={!canSend}
          aria-label="إرسال السؤال"
          className={`shrink-0 w-9 h-9 mb-0.5 rounded-xl flex items-center justify-center transition-all duration-200 ${
            canSend
              ? 'bg-sky-500 hover:bg-sky-400 text-white active:scale-95'
              : 'bg-slate-700/60 text-slate-500 cursor-not-allowed'
          }`}
        >
          {canSend ? (
            <Send className="w-4 h-4 -scale-x-100" />
          ) : (
            <Mic className="w-4 h-4" />
          )}
        </button>
      </form>

      <p className="text-center text-[10px] text-slate-600 mt-1.5">
        مستند إلى دليل WHO 2024 الإكلينيكي
      </p>
    </div>
  );
};
"""

# ─────────────────────────────────────────────
# 11. ChatScreen — fix scroll container, keep composer always visible
# ─────────────────────────────────────────────
files['src/components/chat/ChatScreen.tsx'] = """import { useState, useRef, useEffect } from 'react';
import type { ChatMessage, ConversationSession } from '../../types/chat';
import { UserMessage } from './UserMessage';
import { AssistantMessage } from './AssistantMessage';
import { TypingIndicator } from './TypingIndicator';
import { EmptyChatState } from './EmptyChatState';
import { MobileComposer } from './MobileComposer';
import { AlertCircle, RefreshCw } from 'lucide-react';

export interface ChatScreenProps {
  activeConversation?: ConversationSession | null;
}

export const ChatScreen = ({ activeConversation }: ChatScreenProps) => {
  const [messages, setMessages] = useState<ChatMessage[]>(() =>
    activeConversation ? activeConversation.messages : []
  );
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [composerValue, setComposerValue] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMessages(activeConversation ? activeConversation.messages : []);
    setErrorMessage(null);
  }, [activeConversation]);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    // Instant scroll on new messages, smooth only on user action
    el.scrollTop = el.scrollHeight;
  }, [messages, isLoading]);

  const handleSelectSuggestion = (text: string) => setComposerValue(text);

  const handleSend = async (text: string) => {
    setErrorMessage(null);
    setComposerValue('');

    const userMsg: ChatMessage = {
      id: `u_${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: Date.now(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    setTimeout(() => {
      setIsLoading(false);
      const assistantMsg: ChatMessage = {
        id: `a_${Date.now()}`,
        role: 'assistant',
        content: '',
        structured: {
          paragraphs: [
            'أهلاً بيك، خطوة ممتازة إنك تسأل. في أول 3 أيام بعد التوقف، جسمك يبدأ يتخلص من النيكوتين تماماً، وطبيعي تحس ببعض الصداع والتوتر الخفيف.',
            'عشان تتعامل مع الصداع والتوتر بطريقة آمنة، منظمة الصحة العالمية (WHO 2024) بتوصي بالخطوات دي:',
          ],
          bulletPoints: [
            'شرب كميات وفيرة من المياه طول اليوم لتقليل الصداع.',
            'تمارين التنفس العميق لمدة 3 دقائق عند الرغبة الشديدة.',
            'لو بتشرب أكتر من 20 سيجارة يومياً، بدائل النيكوتين (لصقات 21 مجم أو علكة 2-4 مجم) تساعدك.',
          ],
          keyTakeaway: 'الأعراض بتكون في ذروتها خلال أول 72 ساعة، وبعدها بتقل بشكل ملحوظ.',
          safetyNote: 'لو عندك تاريخ مرضي مع القلب أو قرحة المعدة، استشر طبيبك قبل استخدام بدائل النيكوتين.',
        },
        evidence: [
          {
            id: 'ev_nrt',
            title: 'توصيات بدائل النيكوتين وجرعات البدء',
            sourceDoc: 'WHO Guideline 2024',
            section: 'Section 4.1: Pharmacotherapy',
            excerpt: 'Nicotine replacement therapies are strongly recommended as first-line treatment for tobacco cessation in adults.',
          },
          {
            id: 'ev_behav',
            title: 'الدعم السلوكي وإدارة المحفزات',
            sourceDoc: 'WHO Guideline 2024',
            section: 'Section 3.2: Behavioral Interventions',
            excerpt: 'Structured behavioral interventions combined with pharmacotherapy yield significantly higher cessation rates.',
          },
        ],
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    }, 1200);
  };

  const handleRetry = () => {
    const lastUser = [...messages].reverse().find((m) => m.role === 'user');
    if (lastUser) handleSend(lastUser.content);
  };

  return (
    <div className="w-full h-full flex flex-col bg-slate-950 text-slate-100 overflow-hidden">
      {/* Messages */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto overflow-x-hidden px-4 py-4 min-h-0"
      >
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <EmptyChatState onSelectSuggestion={handleSelectSuggestion} />
          </div>
        ) : (
          <div className="flex flex-col gap-1 max-w-2xl mx-auto pb-2">
            {messages.map((msg, idx) => {
              if (msg.role === 'user') {
                return <UserMessage key={msg.id} message={msg} />;
              }
              const prev = messages[idx - 1];
              return (
                <AssistantMessage
                  key={msg.id}
                  message={msg}
                  showAvatar={!prev || prev.role !== 'assistant'}
                />
              );
            })}

            {isLoading && <TypingIndicator className="mt-2" />}

            {errorMessage && (
              <div
                className="flex items-center justify-between gap-3 my-3 p-3 rounded-xl bg-rose-950/30 border border-rose-800/40 text-rose-300 text-xs"
                dir="rtl"
              >
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
                  <span>{errorMessage}</span>
                </div>
                <button
                  type="button"
                  onClick={handleRetry}
                  className="shrink-0 flex items-center gap-1 text-sky-400 hover:text-sky-300 px-2 py-1 rounded-lg bg-slate-900 border border-slate-700 cursor-pointer"
                >
                  <RefreshCw className="w-3 h-3" />
                  <span>أعد المحاولة</span>
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Composer — always rendered at bottom */}
      <MobileComposer
        onSendMessage={handleSend}
        initialValue={composerValue}
        disabled={isLoading}
        placeholder="اسأل د. سالم عن الإقلاع، الأدوية، أو الأعراض..."
      />
    </div>
  );
};
"""

# ─────────────────────────────────────────────
# 12. EmptyChatState — leaner, fewer suggestions
# ─────────────────────────────────────────────
files['src/components/chat/EmptyChatState.tsx'] = """import { DoctorAvatar } from '../ui/DoctorAvatar';
import { SuggestionChip } from './SuggestionChip';

export interface EmptyChatStateProps {
  onSelectSuggestion: (prompt: string) => void;
}

const SUGGESTIONS = [
  'إزاي أتعامل مع الصداع والعصبية في أول 3 أيام بدون تدخين؟',
  'إيه جرعة اللصقات (NRT) المناسبة لو بشرب علبة في اليوم؟',
  'عايز خطة تساعدني أوقف تدخين تدريجياً خلال أسبوعين.',
  'هل السجائر الإلكترونية وسيلة معتمدة طبياً للإقلاع؟',
];

export const EmptyChatState = ({ onSelectSuggestion }: EmptyChatStateProps) => {
  return (
    <div className="flex flex-col items-center text-center px-4 py-6 w-full max-w-sm mx-auto gap-6 select-none" dir="rtl">
      <div className="relative">
        <DoctorAvatar size="lg" showStatus />
      </div>

      <div className="flex flex-col gap-1.5">
        <h2 className="text-lg font-bold text-white tracking-tight">كيف يمكنني مساعدتك اليوم؟</h2>
        <p className="text-xs text-slate-400 leading-relaxed max-w-[260px] mx-auto">
          اسألني عن الإقلاع، بدائل النيكوتين، أو الأعراض — وفق أدلة WHO 2024.
        </p>
      </div>

      <div className="w-full flex flex-col gap-2 text-right">
        {SUGGESTIONS.map((text, i) => (
          <SuggestionChip key={i} text={text} onClick={onSelectSuggestion} />
        ))}
      </div>
    </div>
  );
};
"""

# ─────────────────────────────────────────────
# 13. AssistantMessage — cleaner layout, better evidence section label
# ─────────────────────────────────────────────
files['src/components/chat/AssistantMessage.tsx'] = """import type { ChatMessage } from '../../types/chat';
import { DoctorAvatar } from '../ui/DoctorAvatar';
import { EvidenceSection } from './EvidenceSection';
import { ShieldCheck, AlertTriangle } from 'lucide-react';

export interface AssistantMessageProps {
  message: ChatMessage;
  showAvatar?: boolean;
}

export const AssistantMessage = ({ message, showAvatar = true }: AssistantMessageProps) => {
  const s = message.structured;

  return (
    <div className="w-full flex items-start gap-2.5 my-1.5" dir="rtl">
      {showAvatar ? (
        <DoctorAvatar size="sm" showStatus={false} className="mt-1 shrink-0" />
      ) : (
        <div className="w-9 shrink-0" />
      )}

      <div className="flex-1 min-w-0 rounded-2xl rounded-tr-sm bg-slate-900 border border-slate-800/80 p-4 shadow-sm">
        {/* Author */}
        <div className="flex items-center gap-1.5 mb-2.5 pb-2 border-b border-slate-800/60">
          <span className="text-xs font-bold text-sky-400">د. سالم</span>
          <span className="text-[10px] text-slate-500">· استشاري إقلاع عن التدخين</span>
        </div>

        {s ? (
          <div className="flex flex-col gap-2.5 text-sm text-slate-200 leading-relaxed">
            {s.paragraphs.map((p, i) => (
              <p key={i} className="whitespace-pre-wrap">{p}</p>
            ))}

            {s.bulletPoints && s.bulletPoints.length > 0 && (
              <ul className="flex flex-col gap-1.5 pr-1">
                {s.bulletPoints.map((pt, i) => (
                  <li key={i} className="flex items-start gap-2 text-slate-300">
                    <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-sky-500 shrink-0" />
                    <span>{pt}</span>
                  </li>
                ))}
              </ul>
            )}

            {s.keyTakeaway && (
              <div className="flex items-start gap-2 p-2.5 rounded-xl bg-sky-950/40 border border-sky-800/30 text-sky-200 text-xs">
                <ShieldCheck className="w-3.5 h-3.5 shrink-0 text-sky-400 mt-0.5" />
                <span><strong>الخلاصة:</strong> {s.keyTakeaway}</span>
              </div>
            )}

            {s.safetyNote && (
              <div className="flex items-start gap-2 p-2.5 rounded-xl bg-amber-950/25 border border-amber-800/30 text-amber-200 text-xs">
                <AlertTriangle className="w-3.5 h-3.5 shrink-0 text-amber-400 mt-0.5" />
                <span>{s.safetyNote}</span>
              </div>
            )}
          </div>
        ) : (
          <p className="text-sm text-slate-200 leading-relaxed whitespace-pre-wrap">{message.content}</p>
        )}

        {message.evidence && message.evidence.length > 0 && (
          <EvidenceSection evidence={message.evidence} />
        )}
      </div>
    </div>
  );
};
"""

# ─────────────────────────────────────────────
# 14. SidebarDrawer — fix safe area in header, clean up bottom actions
# ─────────────────────────────────────────────
files['src/components/drawer/SidebarDrawer.tsx'] = """import { useEffect } from 'react';
import type { ConversationSession } from '../../types/chat';
import { DoctorAvatar } from '../ui/DoctorAvatar';
import { BrandMark } from '../ui/BrandMark';
import { ConversationItem } from './ConversationItem';
import { Plus, X, Settings, LogOut, MessageSquareDashed } from 'lucide-react';

export interface SidebarDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  conversations: ConversationSession[];
  activeConversationId: string | null;
  onSelectConversation: (c: ConversationSession) => void;
  onNewConversation: () => void;
  onOpenSettings: () => void;
  onOpenLogoutDialog: () => void;
}

export const SidebarDrawer = ({
  isOpen,
  onClose,
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onOpenSettings,
  onOpenLogoutDialog,
}: SidebarDrawerProps) => {
  // Escape key to close
  useEffect(() => {
    if (!isOpen) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [isOpen, onClose]);

  const groups = [
    { label: 'اليوم', items: conversations.filter((c) => c.group === 'اليوم') },
    { label: 'أمس', items: conversations.filter((c) => c.group === 'أمس') },
    { label: 'هذا الأسبوع', items: conversations.filter((c) => c.group === 'هذا الأسبوع') },
  ].filter((g) => g.items.length > 0);

  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-[2px]"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Drawer panel — slides from RIGHT (RTL) */}
      <div
        className={`fixed top-0 right-0 h-full z-50 w-[82%] max-w-[340px] bg-slate-900 border-l border-slate-800/80 shadow-2xl flex flex-col transition-transform duration-250 ease-out ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
        role="dialog"
        aria-modal="true"
        aria-label="القائمة الجانبية"
        style={{ paddingTop: 'var(--sat)', paddingBottom: 'var(--sab)' }}
        dir="rtl"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800/80">
          <div className="flex items-center gap-2.5">
            <DoctorAvatar size="sm" showStatus={false} />
            <BrandMark showSubtitle={false} />
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="إغلاق القائمة"
            className="w-9 h-9 flex items-center justify-center rounded-xl text-slate-400 hover:text-white hover:bg-slate-800/60 transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* New conversation */}
        <div className="px-3 py-2.5 border-b border-slate-800/60">
          <button
            type="button"
            onClick={onNewConversation}
            className="w-full h-10 px-3 rounded-xl bg-sky-500/10 hover:bg-sky-500/20 text-sky-400 font-bold text-xs border border-sky-500/25 flex items-center justify-center gap-2 transition-colors cursor-pointer active:scale-[0.98]"
          >
            <Plus className="w-4 h-4" />
            <span>محادثة جديدة</span>
          </button>
        </div>

        {/* Conversation list */}
        <div className="flex-1 overflow-y-auto px-2 py-3 flex flex-col gap-4 min-h-0">
          {groups.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center text-center text-slate-500 gap-2 py-8">
              <MessageSquareDashed className="w-8 h-8 text-slate-700" />
              <p className="text-xs">لا توجد محادثات بعد</p>
            </div>
          ) : (
            groups.map((g) => (
              <div key={g.label} className="flex flex-col gap-0.5">
                <span className="text-[10px] font-bold text-slate-500 px-2 mb-1 tracking-wider uppercase">
                  {g.label}
                </span>
                {g.items.map((conv) => (
                  <ConversationItem
                    key={conv.id}
                    conversation={conv}
                    isActive={conv.id === activeConversationId}
                    onClick={onSelectConversation}
                  />
                ))}
              </div>
            ))
          )}
        </div>

        {/* Footer actions */}
        <div className="border-t border-slate-800/80 px-2 py-2 flex flex-col gap-0.5">
          <button
            type="button"
            onClick={onOpenSettings}
            className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-slate-300 hover:text-white hover:bg-slate-800/60 text-xs font-medium transition-colors cursor-pointer"
          >
            <Settings className="w-4 h-4 text-slate-500" />
            <span>الإعدادات</span>
          </button>
          <button
            type="button"
            onClick={onOpenLogoutDialog}
            className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 text-xs font-medium transition-colors cursor-pointer"
          >
            <LogOut className="w-4 h-4" />
            <span>تسجيل الخروج</span>
          </button>
        </div>
      </div>
    </>
  );
};
"""

# ─────────────────────────────────────────────
# 15. SettingsScreen — cleaner, remove header double border, safe area
# ─────────────────────────────────────────────
files['src/components/settings/SettingsScreen.tsx'] = """import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { ArrowRight, User, Globe, Moon, Lock, Database, Info, ShieldCheck, LogOut, ChevronLeft, X } from 'lucide-react';

export interface SettingsScreenProps {
  onBack: () => void;
  onOpenLogoutDialog: () => void;
}

type ModalKey = 'privacy' | 'data' | 'about' | 'sources' | null;

const MODAL_CONTENT: Record<NonNullable<ModalKey>, { title: string; body: string[] }> = {
  privacy: {
    title: 'سياسة الخصوصية',
    body: [
      'نستخدم بيانات الحساب والمحادثات لتقديم تجربة المساعد الطبي وفق إعدادات الخدمة.',
      'لا نشارك أي بيانات صحية شخصية مع أطراف خارجية أو جهات دعائية.',
    ],
  },
  data: {
    title: 'البيانات والمحادثات',
    body: [
      'ترتبط المحادثات بحسابك لتسهيل استرجاع خطة الإقلاع ومتابعة تقدمك.',
      'يمكنك بدء محادثة جديدة أو إدارة الجلسات في أي وقت.',
    ],
  },
  about: {
    title: 'عن Oxygen Medical RAG',
    body: [
      'أوكسجين مساعد صحي وسلوكي مبني على تقنية استرجاع وتأصيل الإجابات (RAG).',
      'د. سالم مُدرَّب لتقديم نصائح مبسطة بالعامية مع الالتزام الصارم بالأدلة الطبية.',
    ],
  },
  sources: {
    title: 'المصادر والمنهجية',
    body: [
      'المصدر الطبي: دليل منظمة الصحة العالمية الإكلينيكي للإقلاع عن التبغ لدى البالغين (WHO 2024).',
      'تخضع جميع الإجابات لتدقيق دقيق لضمان سلامة التوصيات الطبية.',
    ],
  },
};

export const SettingsScreen = ({ onBack, onOpenLogoutDialog }: SettingsScreenProps) => {
  const { user } = useAuth();
  const [appearance, setAppearance] = useState<'dark' | 'light' | 'system'>('dark');
  const [modal, setModal] = useState<ModalKey>(null);

  return (
    <div className="w-full h-full flex flex-col bg-slate-950 text-white" dir="rtl">
      {/* Header */}
      <div
        className="shrink-0 bg-slate-900 border-b border-slate-800/80 px-4 flex items-center gap-3"
        style={{ paddingTop: 'calc(0.875rem + var(--sat))', paddingBottom: '0.875rem' }}
      >
        <button
          type="button"
          onClick={onBack}
          aria-label="الرجوع إلى المحادثة"
          className="w-9 h-9 flex items-center justify-center rounded-xl text-slate-400 hover:text-white hover:bg-slate-800/60 transition-colors cursor-pointer"
        >
          <ArrowRight className="w-5 h-5" />
        </button>
        <h1 className="text-base font-bold text-white">الإعدادات</h1>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="px-4 py-5 flex flex-col gap-5" style={{ paddingBottom: 'calc(1.5rem + var(--sab))' }}>

          {/* Account */}
          <Section label="الحساب">
            <div className="flex items-center gap-3.5 px-4 py-3.5">
              <div className="w-11 h-11 rounded-full bg-gradient-to-br from-sky-500 to-blue-700 flex items-center justify-center text-white font-bold text-base border border-sky-400/30 shrink-0">
                {user?.name ? user.name.slice(0, 1) : <User className="w-5 h-5" />}
              </div>
              <div className="flex flex-col min-w-0">
                <span className="text-sm font-semibold text-white truncate">{user?.name || 'محمد حسن'}</span>
                <span className="text-xs text-slate-400 truncate">{user?.email || 'mohamed.hassan@gmail.com'}</span>
                <span className="text-[10px] text-sky-400 font-medium mt-0.5">{user?.provider || 'Google Account'}</span>
              </div>
            </div>
          </Section>

          {/* App preferences */}
          <Section label="التطبيق">
            <SettingsRow
              icon={<Globe className="w-4 h-4 text-sky-400" />}
              label="اللغة"
              trailing={<span className="text-xs text-slate-400 bg-slate-800 px-2 py-1 rounded-lg">العربية</span>}
            />
            <div className="border-t border-slate-800/60" />
            <div className="flex items-center justify-between px-4 py-3">
              <div className="flex items-center gap-2.5 text-xs text-slate-200 font-medium">
                <Moon className="w-4 h-4 text-sky-400" />
                <span>المظهر</span>
              </div>
              <div className="flex items-center bg-slate-950 rounded-lg p-0.5 border border-slate-800 text-[11px]">
                {(['dark', 'light', 'system'] as const).map((opt) => (
                  <button
                    key={opt}
                    type="button"
                    onClick={() => setAppearance(opt)}
                    className={`px-2.5 py-1 rounded-md font-medium transition-colors cursor-pointer ${
                      appearance === opt ? 'bg-sky-500 text-white' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    {opt === 'dark' ? 'داكن' : opt === 'light' ? 'فاتح' : 'النظام'}
                  </button>
                ))}
              </div>
            </div>
          </Section>

          {/* Privacy */}
          <Section label="الخصوصية والبيانات">
            <SettingsButton
              icon={<Lock className="w-4 h-4 text-sky-400" />}
              label="سياسة الخصوصية"
              onClick={() => setModal('privacy')}
            />
            <div className="border-t border-slate-800/60" />
            <SettingsButton
              icon={<Database className="w-4 h-4 text-sky-400" />}
              label="البيانات والمحادثات"
              onClick={() => setModal('data')}
            />
          </Section>

          {/* About */}
          <Section label="عن التطبيق">
            <SettingsButton
              icon={<Info className="w-4 h-4 text-sky-400" />}
              label="عن Oxygen Medical RAG"
              onClick={() => setModal('about')}
            />
            <div className="border-t border-slate-800/60" />
            <SettingsButton
              icon={<ShieldCheck className="w-4 h-4 text-sky-400" />}
              label="المصادر والمنهجية الطبية"
              onClick={() => setModal('sources')}
            />
          </Section>

          {/* Logout */}
          <div className="rounded-xl border border-rose-900/40 overflow-hidden">
            <button
              type="button"
              onClick={onOpenLogoutDialog}
              className="w-full flex items-center gap-2.5 px-4 py-3.5 text-rose-400 hover:bg-rose-500/10 transition-colors cursor-pointer text-xs font-semibold"
            >
              <LogOut className="w-4 h-4" />
              <span>تسجيل الخروج</span>
            </button>
          </div>

          <p className="text-center text-[11px] text-slate-600">
            أوكسجين · الإصدار 1.0.0 · WHO 2024
          </p>
        </div>
      </div>

      {/* Modal */}
      {modal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-5 bg-black/70 backdrop-blur-sm"
          dir="rtl"
          role="dialog"
          aria-modal="true"
        >
          <div className="w-full max-w-sm bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl flex flex-col max-h-[70vh]">
            <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800">
              <h3 className="text-sm font-bold text-white">{MODAL_CONTENT[modal].title}</h3>
              <button
                type="button"
                onClick={() => setModal(null)}
                aria-label="إغلاق"
                className="w-8 h-8 flex items-center justify-center rounded-xl text-slate-400 hover:text-white hover:bg-slate-800/60 cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto px-4 py-4 flex flex-col gap-3">
              {MODAL_CONTENT[modal].body.map((p, i) => (
                <p key={i} className="text-xs text-slate-300 leading-relaxed">{p}</p>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// ── Small helper components ──────────────────
const Section = ({ label, children }: { label: string; children: React.ReactNode }) => (
  <div className="flex flex-col gap-2">
    <span className="text-[10px] font-bold text-slate-500 px-1 tracking-wider uppercase">{label}</span>
    <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 overflow-hidden">
      {children}
    </div>
  </div>
);

const SettingsRow = ({
  icon,
  label,
  trailing,
}: {
  icon: React.ReactNode;
  label: string;
  trailing?: React.ReactNode;
}) => (
  <div className="flex items-center justify-between px-4 py-3">
    <div className="flex items-center gap-2.5 text-xs text-slate-200 font-medium">
      {icon}
      <span>{label}</span>
    </div>
    {trailing}
  </div>
);

const SettingsButton = ({
  icon,
  label,
  onClick,
}: {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
}) => (
  <button
    type="button"
    onClick={onClick}
    className="w-full flex items-center justify-between px-4 py-3 hover:bg-slate-800/50 transition-colors cursor-pointer"
  >
    <div className="flex items-center gap-2.5 text-xs text-slate-200 font-medium">
      {icon}
      <span>{label}</span>
    </div>
    <ChevronLeft className="w-4 h-4 text-slate-500" />
  </button>
);
"""

# ─────────────────────────────────────────────
# Write all files
# ─────────────────────────────────────────────
for rel_path, content in files.items():
    abs_path = rel_path if os.path.isabs(rel_path) else os.path.join(os.getcwd(), rel_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Written:', rel_path)

print('\\nAll audit fixes applied!')
