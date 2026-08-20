import os

files = {
'src/tokens/index.ts': '''export const tokens = {
  colors: {
    primary: {
      50: '#eff6ff',
      100: '#dbeafe',
      200: '#bfdbfe',
      300: '#93c5fd',
      400: '#60a5fa',
      500: '#3b82f6',
      600: '#2563eb',
      700: '#1d4ed8',
      800: '#1e40af',
      900: '#1e3a8a',
      navy: '#0a192f',
    },
    medical: {
      teal: '#0d9488',
      cyan: '#0284c7',
      emerald: '#059669',
      slate: '#0f172a',
      darkSurface: '#0b1329',
      cardSurface: '#131f3d',
      borderSubtle: '#1e293b',
    },
    text: {
      primary: '#f8fafc',
      secondary: '#94a3b8',
      muted: '#64748b',
      accent: '#38bdf8',
    }
  },
  typography: {
    fontFamily: {
      arabic: "'Cairo', system-ui, -apple-system, sans-serif",
      latin: "'Plus Jakarta Sans', system-ui, sans-serif",
    },
    sizes: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
    }
  },
  spacing: {
    touchTarget: '48px',
    headerHeight: '64px',
    composerHeight: '76px',
    maxAppWidth: '440px',
  },
  radius: {
    sm: '0.375rem',
    md: '0.75rem',
    lg: '1rem',
    xl: '1.25rem',
    full: '9999px',
  },
  shadows: {
    glow: '0 0 20px -5px rgba(56, 189, 248, 0.25)',
    header: '0 4px 20px -2px rgba(0, 0, 0, 0.3)',
    card: '0 8px 24px -4px rgba(0, 0, 0, 0.4)',
    composer: '0 -4px 24px -2px rgba(0, 0, 0, 0.35)',
  }
} as const;

export type DesignTokens = typeof tokens;
''',

'src/types/auth.ts': '''export type EntryStep = 'splash' | 'onboarding' | 'login' | 'chat_ready' | 'settings';

export type AuthStatus = 'idle' | 'loading' | 'success' | 'error';

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  avatarUrl?: string;
  provider?: string;
  createdAt?: number;
  lastLoginAt?: number;
}

export interface AuthContextType {
  user: UserProfile | null;
  status: AuthStatus;
  errorMessage: string | null;
  hasSeenOnboarding: boolean;
  signInWithGoogle: () => Promise<void>;
  signOut: () => void;
  markOnboardingComplete: () => void;
  resetOnboarding: () => void;
}
''',

'src/types/chat.ts': '''export type MessageRole = 'user' | 'assistant';

export interface EvidenceSource {
  id: string;
  title: string;
  sourceDoc: string;
  section?: string;
  excerpt?: string;
}

export interface StructuredContent {
  paragraphs: string[];
  bulletPoints?: string[];
  keyTakeaway?: string;
  safetyNote?: string;
}

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  structured?: StructuredContent;
  evidence?: EvidenceSource[];
  timestamp: number;
}

export interface ConversationSession {
  id: string;
  title: string;
  group: 'اليوم' | 'أمس' | 'هذا الأسبوع';
  createdAt: number;
  updatedAt: number;
  messages: ChatMessage[];
}
''',

'src/context/AuthContext.tsx': '''import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { AuthContextType, AuthStatus, UserProfile } from '../types/auth';

const ONBOARDING_STORAGE_KEY = 'oxygen_has_seen_onboarding_v1';
const USER_STORAGE_KEY = 'oxygen_mock_user_v1';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<UserProfile | null>(() => {
    try {
      const saved = localStorage.getItem(USER_STORAGE_KEY);
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const [hasSeenOnboarding, setHasSeenOnboarding] = useState<boolean>(() => {
    try {
      return localStorage.getItem(ONBOARDING_STORAGE_KEY) === 'true';
    } catch {
      return false;
    }
  });

  const [status, setStatus] = useState<AuthStatus>('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    try {
      if (user) {
        localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
      } else {
        localStorage.removeItem(USER_STORAGE_KEY);
      }
    } catch {
      // Ignore storage errors
    }
  }, [user]);

  const markOnboardingComplete = () => {
    setHasSeenOnboarding(true);
    try {
      localStorage.setItem(ONBOARDING_STORAGE_KEY, 'true');
    } catch {
      // Ignore storage errors
    }
  };

  const resetOnboarding = () => {
    setHasSeenOnboarding(false);
    try {
      localStorage.removeItem(ONBOARDING_STORAGE_KEY);
    } catch {
      // Ignore storage errors
    }
  };

  const signInWithGoogle = async (): Promise<void> => {
    setStatus('loading');
    setErrorMessage(null);

    try {
      await new Promise((resolve) => setTimeout(resolve, 800));

      const mockUser: UserProfile = {
        id: 'usr_google_123',
        name: 'محمد حسن',
        email: 'mohamed.hassan@gmail.com',
        provider: 'Google Account',
        createdAt: Date.now() - 604800000,
        lastLoginAt: Date.now(),
      };

      setUser(mockUser);
      setStatus('success');
    } catch {
      setStatus('error');
      setErrorMessage('تعذر تسجيل الدخول. حاول مرة أخرى.');
    }
  };

  const signOut = () => {
    setUser(null);
    setStatus('idle');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        status,
        errorMessage,
        hasSeenOnboarding,
        signInWithGoogle,
        signOut,
        markOnboardingComplete,
        resetOnboarding,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
''',

'src/components/ui/DoctorAvatar.tsx': '''export interface DoctorAvatarProps {
  size?: 'sm' | 'md' | 'lg';
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
  };

  const badgeSizeMap = {
    sm: 'w-2.5 h-2.5 -bottom-0.5 -left-0.5',
    md: 'w-3.5 h-3.5 -bottom-0.5 -left-0.5',
    lg: 'w-4 h-4 bottom-0 left-0',
  };

  return (
    <div className={`relative inline-flex items-center justify-center shrink-0 ${className}`}>
      <div
        className={`${sizeMap[size]} rounded-full p-[2px] bg-gradient-to-tr from-sky-500 via-blue-600 to-indigo-500 shadow-md shadow-sky-950/40`}
      >
        <div className="w-full h-full rounded-full bg-slate-900 overflow-hidden flex items-center justify-center border border-slate-800">
          <svg
            viewBox="0 0 48 48"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="w-full h-full text-slate-200"
            aria-label="دكتور سالم"
          >
            <circle cx="24" cy="24" r="24" fill="#0f172a" />
            <path
              d="M10 44C10 35.1634 16.268 28 24 28C31.732 28 38 35.1634 38 44"
              fill="#1e293b"
            />
            <path
              d="M18 36L24 44L30 36"
              stroke="#38bdf8"
              strokeWidth="2"
              strokeLinecap="round"
            />
            <circle cx="24" cy="20" r="8" fill="#cbd5e1" />
            <path
              d="M16 18C16 13.5817 19.5817 10 24 10C28.4183 10 32 13.5817 32 18C32 19 31.5 19.5 30 19C28.5 18.5 27 17 24 17C21 17 19.5 18.5 18 19C16.5 19.5 16 19 16 18Z"
              fill="#334155"
            />
            <circle cx="24" cy="38" r="2" fill="#38bdf8" />
          </svg>
        </div>
      </div>

      {showStatus && (
        <span
          className={`absolute ${badgeSizeMap[size]} bg-emerald-500 border-2 border-slate-900 rounded-full shadow-sm shadow-emerald-950/50`}
          title="د. سالم متصل"
        >
          <span className="absolute inset-0 rounded-full bg-emerald-400 animate-ping opacity-75" />
        </span>
      )}
    </div>
  );
};
''',

'src/components/ui/BrandMark.tsx': '''export interface BrandMarkProps {
  showSubtitle?: boolean;
  className?: string;
}

export const BrandMark = ({
  showSubtitle = true,
  className = '',
}: BrandMarkProps) => {
  return (
    <div className={`flex flex-col items-start select-none ${className}`} dir="rtl">
      <div className="flex items-center gap-1.5">
        <span className="text-xl font-extrabold tracking-tight text-white font-arabic">
          أوكسجين
        </span>
        <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold bg-sky-500/10 text-sky-400 border border-sky-500/20 tracking-wide">
          د. سالم
        </span>
      </div>
      {showSubtitle && (
        <span className="text-[11px] font-medium text-slate-400 leading-tight">
          المساعد الطبي للإقلاع عن التدخين
        </span>
      )}
    </div>
  );
};
''',

'src/components/ui/IconButton.tsx': '''import type { ButtonHTMLAttributes } from 'react';

export interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'ghost' | 'filled' | 'outline' | 'primary';
  size?: 'sm' | 'md' | 'lg';
  ariaLabel: string;
}

export const IconButton = ({
  children,
  variant = 'ghost',
  size = 'md',
  ariaLabel,
  className = '',
  ...props
}: IconButtonProps) => {
  const sizeClasses = {
    sm: 'w-10 h-10 min-w-[40px] min-h-[40px]',
    md: 'w-11 h-11 min-w-[44px] min-h-[44px]',
    lg: 'w-12 h-12 min-w-[48px] min-h-[48px]',
  };

  const variantClasses = {
    ghost: 'text-slate-300 hover:text-white hover:bg-slate-800/60 active:bg-slate-800',
    filled: 'bg-slate-800/90 text-slate-200 hover:bg-slate-700 active:bg-slate-800 border border-slate-700/50',
    outline: 'border border-slate-700 text-slate-300 hover:text-white hover:bg-slate-800/40 active:bg-slate-800',
    primary: 'bg-sky-500 text-white hover:bg-sky-400 active:bg-sky-600 shadow-md shadow-sky-950/40',
  };

  return (
    <button
      type="button"
      aria-label={ariaLabel}
      className={`
        inline-flex items-center justify-center rounded-xl transition-all duration-200 cursor-pointer
        active:scale-95 touch-manipulation focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-500
        disabled:opacity-40 disabled:cursor-not-allowed disabled:active:scale-100
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        ${className}
      `}
      {...props}
    >
      {children}
    </button>
  );
};
''',

'src/components/ui/MenuButton.tsx': '''import { Menu } from 'lucide-react';
import { IconButton } from './IconButton';

export interface MenuButtonProps {
  onClick?: () => void;
  isOpen?: boolean;
  className?: string;
}

export const MenuButton = ({
  onClick,
  isOpen = false,
  className = '',
}: MenuButtonProps) => {
  return (
    <IconButton
      ariaLabel={isOpen ? 'إغلاق القائمة' : 'فتح القائمة الرئيسية ومحادثات سابقة'}
      onClick={onClick}
      variant="filled"
      size="md"
      className={`relative group ${className}`}
    >
      <Menu className={`w-5 h-5 transition-transform duration-200 ${isOpen ? 'rotate-90' : ''}`} />
    </IconButton>
  );
};
''',

'src/components/ui/Button.tsx': '''import type { ButtonHTMLAttributes, ReactNode } from 'react';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
}

export const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  leftIcon,
  rightIcon,
  className = '',
  ...props
}: ButtonProps) => {
  const sizeClasses = {
    sm: 'h-10 px-3 text-xs gap-1.5 min-h-[40px]',
    md: 'h-12 px-4 text-sm gap-2 min-h-[48px]',
    lg: 'h-14 px-6 text-base gap-2.5 min-h-[52px]',
  };

  const variantClasses = {
    primary: 'bg-sky-500 hover:bg-sky-400 active:bg-sky-600 text-white font-semibold shadow-md shadow-sky-950/40 border border-sky-400/30',
    secondary: 'bg-slate-800 hover:bg-slate-700 active:bg-slate-800/90 text-slate-100 font-medium border border-slate-700/60',
    outline: 'border border-sky-500/50 hover:bg-sky-500/10 active:bg-sky-500/20 text-sky-400 font-medium',
    ghost: 'text-slate-300 hover:text-white hover:bg-slate-800/50 active:bg-slate-800',
    danger: 'bg-rose-600 hover:bg-rose-500 active:bg-rose-700 text-white font-semibold shadow-md shadow-rose-950/40',
  };

  return (
    <button
      className={`
        inline-flex items-center justify-center rounded-xl font-arabic transition-all duration-200 cursor-pointer
        active:scale-[0.98] touch-manipulation focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-500
        disabled:opacity-40 disabled:cursor-not-allowed disabled:active:scale-100
        ${fullWidth ? 'w-full' : ''}
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        ${className}
      `}
      {...props}
    >
      {leftIcon && <span className="shrink-0">{leftIcon}</span>}
      <span>{children}</span>
      {rightIcon && <span className="shrink-0">{rightIcon}</span>}
    </button>
  );
};
''',

'src/components/ui/Surface.tsx': '''import type { HTMLAttributes } from 'react';

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
''',

'src/components/entry/SplashScreen.tsx': '''import { useEffect } from 'react';
import { DoctorAvatar } from '../ui/DoctorAvatar';
import { Sparkles } from 'lucide-react';

export interface SplashScreenProps {
  onComplete: () => void;
  durationMs?: number;
}

export const SplashScreen = ({
  onComplete,
  durationMs = 1200,
}: SplashScreenProps) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onComplete();
    }, durationMs);

    return () => clearTimeout(timer);
  }, [onComplete, durationMs]);

  return (
    <div
      className="w-full h-full flex flex-col items-center justify-between p-8 bg-gradient-to-b from-slate-900 via-slate-950 to-slate-950 text-white select-none animate-in fade-in duration-300"
      dir="rtl"
      role="status"
      aria-label="شاشة التحميل والترحيب"
    >
      <div className="pt-4" />

      <div className="flex flex-col items-center text-center gap-5 my-auto">
        <div className="relative group">
          <div className="absolute -inset-2 bg-sky-500/20 rounded-full blur-xl animate-pulse" />
          <DoctorAvatar size="lg" showStatus={false} className="relative z-10" />
          <div className="absolute -top-1 -right-1 z-20 bg-sky-500 text-white p-1 rounded-full shadow-md shadow-sky-900/60">
            <Sparkles className="w-3.5 h-3.5" />
          </div>
        </div>

        <div className="flex flex-col items-center gap-2">
          <div className="flex items-center gap-2">
            <h1 className="text-3xl font-extrabold tracking-tight text-white font-arabic">
              أوكسجين
            </h1>
            <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-bold bg-sky-500/15 text-sky-400 border border-sky-500/30">
              د. سالم
            </span>
          </div>

          <p className="text-sm font-medium text-slate-300 font-arabic max-w-[260px] leading-relaxed">
            مرشدك الطبي للإقلاع عن التدخين
          </p>
        </div>
      </div>

      <div className="w-full flex flex-col items-center gap-3 pb-[calc(1rem+var(--sab))]">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-sky-500 animate-ping" />
          <span className="text-[12px] font-medium text-slate-400 font-arabic">
            إرشادات منظمة الصحة العالمية 2024
          </span>
        </div>
      </div>
    </div>
  );
};
''',

'src/components/entry/OnboardingScreen.tsx': '''import { useState } from 'react';
import { Button } from '../ui/Button';
import { Surface } from '../ui/Surface';
import { ShieldCheck, MessageSquareHeart, Lock } from 'lucide-react';

export interface OnboardingScreenProps {
  onComplete: () => void;
}

export const OnboardingScreen = ({ onComplete }: OnboardingScreenProps) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  const slides = [
    {
      id: 'evidence',
      icon: ShieldCheck,
      iconColor: 'text-sky-400',
      iconBg: 'bg-sky-500/10 border-sky-500/20',
      title: 'مساعدة مبنية على الأدلة',
      description:
        'إرشادات طبية وسلوكية موثوقة ومستندة بنسبة 100% إلى أحدث أدلة منظمة الصحة العالمية (WHO 2024) للإقلاع الآمن عن التبغ.',
      badge: 'دليل WHO 2024',
    },
    {
      id: 'natural_language',
      icon: MessageSquareHeart,
      iconColor: 'text-emerald-400',
      iconBg: 'bg-emerald-500/10 border-emerald-500/20',
      title: 'اسأل بلغتك وبكل راحة',
      description:
        'تحدث بطبيعتك وبلهجتك. دكتور سالم يشرح لك بدائل النيكوتين، التعامل مع الأعراض الانسحابية، وخطوات التدرج بأسلوب دافئ ومبسط.',
      badge: 'تواصل إنساني مباشر',
    },
    {
      id: 'privacy',
      icon: Lock,
      iconColor: 'text-indigo-400',
      iconBg: 'bg-indigo-500/10 border-indigo-500/20',
      title: 'خصوصيتك أولاً',
      description:
        'محادثاتك في بيئة آمنة ومحمية تماماً. نحن نحرص على سرية استفساراتك لنضمن لك مساحة دعم صحي مريحة وموثوقة.',
      badge: 'أمان وسرية',
    },
  ];

  const currentSlide = slides[currentIndex];
  const isLastSlide = currentIndex === slides.length - 1;

  const handleNext = () => {
    if (isLastSlide) {
      onComplete();
    } else {
      setCurrentIndex((prev) => prev + 1);
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1);
    }
  };

  return (
    <div
      className="w-full h-full flex flex-col justify-between p-6 bg-slate-950 text-white select-none"
      dir="rtl"
    >
      <div className="flex items-center justify-between pt-2">
        <div className="flex items-center gap-1.5">
          {slides.map((_, idx) => (
            <div
              key={idx}
              className={`h-1.5 rounded-full transition-all duration-300 ${
                idx === currentIndex
                  ? 'w-7 bg-sky-500 shadow-sm shadow-sky-500/50'
                  : idx < currentIndex
                  ? 'w-2.5 bg-sky-800'
                  : 'w-2 bg-slate-800'
              }`}
            />
          ))}
        </div>

        {!isLastSlide ? (
          <button
            type="button"
            onClick={onComplete}
            className="text-xs font-semibold text-slate-400 hover:text-white px-2.5 py-1.5 rounded-lg hover:bg-slate-900 transition-colors cursor-pointer active:scale-95"
            aria-label="تخطي الشروحات والذهاب لتسجيل الدخول"
          >
            تخطي
          </button>
        ) : (
          <span className="w-10" />
        )}
      </div>

      <div className="my-auto flex flex-col items-center text-center max-w-sm mx-auto px-2">
        <Surface
          variant="glass"
          padding="lg"
          rounded="2xl"
          className="mb-8 relative flex items-center justify-center border border-slate-800 shadow-xl shadow-slate-950/70 group"
        >
          <div
            className={`w-20 h-20 rounded-2xl flex items-center justify-center border ${currentSlide.iconBg} transition-transform duration-300 group-hover:scale-105`}
          >
            <currentSlide.icon className={`w-10 h-10 ${currentSlide.iconColor}`} />
          </div>
        </Surface>

        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-slate-900 text-sky-400 border border-slate-800 mb-3 shadow-inner">
          {currentSlide.badge}
        </span>

        <h2 className="text-2xl font-bold text-white mb-3 tracking-tight font-arabic">
          {currentSlide.title}
        </h2>

        <p className="text-sm font-normal text-slate-300 leading-relaxed font-arabic">
          {currentSlide.description}
        </p>
      </div>

      <div className="w-full flex flex-col gap-3 pb-[calc(1rem+var(--sab))]">
        <Button
          variant="primary"
          size="lg"
          fullWidth
          onClick={handleNext}
          className="shadow-lg shadow-sky-950/60 font-bold"
        >
          {isLastSlide ? 'ابدأ الآن' : 'التالي'}
        </Button>

        {currentIndex > 0 && (
          <Button
            variant="ghost"
            size="sm"
            fullWidth
            onClick={handlePrev}
            className="text-slate-400 hover:text-slate-200"
          >
            السابق
          </Button>
        )}
      </div>
    </div>
  );
};
''',

'src/components/entry/GoogleSignInButton.tsx': '''import { Loader2 } from 'lucide-react';

export interface GoogleSignInButtonProps {
  onClick: () => void;
  isLoading?: boolean;
  disabled?: boolean;
  className?: string;
}

export const GoogleSignInButton = ({
  onClick,
  isLoading = false,
  disabled = false,
  className = '',
}: GoogleSignInButtonProps) => {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled || isLoading}
      aria-label="تسجيل الدخول باستخدام Google"
      className={`w-full h-13 min-h-[50px] px-4 rounded-xl bg-white hover:bg-slate-50 active:bg-slate-100 text-slate-800 font-semibold text-sm font-arabic border border-slate-200 shadow-md shadow-black/20 flex items-center justify-center gap-3 transition-all duration-200 cursor-pointer active:scale-[0.98] touch-manipulation disabled:opacity-60 disabled:cursor-not-allowed disabled:active:scale-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-500 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900 ${className}`}
      dir="rtl"
    >
      {isLoading ? (
        <>
          <Loader2 className="w-5 h-5 animate-spin text-sky-600" />
          <span>جارٍ تسجيل الدخول...</span>
        </>
      ) : (
        <>
          <svg className="w-5 h-5 shrink-0" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.17z"
            />
            <path
              fill="#34A853"
              d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.33 24 12 24z"
            />
            <path
              fill="#FBBC05"
              d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.98 0 12s.45 3.82 1.25 5.42l4.03-3.15z"
            />
            <path
              fill="#EA4335"
              d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"
            />
          </svg>
          <span className="font-semibold text-slate-800">المتابعة باستخدام Google</span>
        </>
      )}
    </button>
  );
};
''',

'src/components/entry/LoginScreen.tsx': '''import { useAuth } from '../../context/AuthContext';
import { DoctorAvatar } from '../ui/DoctorAvatar';
import { Surface } from '../ui/Surface';
import { GoogleSignInButton } from './GoogleSignInButton';
import { ShieldCheck, Lock, AlertCircle } from 'lucide-react';

export interface LoginScreenProps {
  onSuccess: () => void;
}

export const LoginScreen = ({ onSuccess }: LoginScreenProps) => {
  const { signInWithGoogle, status, errorMessage } = useAuth();

  const handleGoogleLogin = async () => {
    await signInWithGoogle();
    onSuccess();
  };

  return (
    <div
      className="w-full h-full flex flex-col justify-between p-6 bg-slate-950 text-white select-none animate-in fade-in duration-300"
      dir="rtl"
    >
      <div className="pt-2 flex justify-center">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-sky-500/10 text-sky-400 border border-sky-500/20">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>منصة أوكسجين الطبية</span>
        </span>
      </div>

      <div className="my-auto flex flex-col items-center text-center max-w-sm mx-auto w-full px-2">
        <div className="mb-6 relative">
          <DoctorAvatar size="lg" showStatus={true} />
        </div>

        <h1 className="text-2xl font-bold text-white mb-2 font-arabic tracking-tight">
          مرحبًا بك مع د. سالم
        </h1>

        <p className="text-sm text-slate-300 font-arabic leading-relaxed mb-6">
          احصل على إرشادات طبية وسلوكية مخصصة للإقلاع عن التدخين، مستندة إلى إرشادات منظمة الصحة العالمية.
        </p>

        {errorMessage && (
          <Surface
            variant="card"
            padding="sm"
            rounded="lg"
            className="w-full mb-4 bg-rose-500/10 border-rose-500/30 text-rose-300 flex items-center gap-2.5 text-right text-xs"
          >
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{errorMessage}</span>
          </Surface>
        )}

        <div className="w-full">
          <GoogleSignInButton
            onClick={handleGoogleLogin}
            isLoading={status === 'loading'}
          />
        </div>
      </div>

      <div className="w-full text-center pb-[calc(1rem+var(--sab))] pt-4">
        <p className="text-[11px] text-slate-400 font-arabic leading-normal flex items-center justify-center gap-1.5 max-w-xs mx-auto">
          <Lock className="w-3 h-3 shrink-0 text-slate-400" />
          <span>هذا التطبيق يقدم إرشادات معرفية وتوعوية، ولا يعد بديلاً عن الاستشارة الطبية المباشرة أو حالات الطوارئ.</span>
        </p>
      </div>
    </div>
  );
};
''',

'src/components/layout/MobileHeader.tsx': '''import { MenuButton } from '../ui/MenuButton';
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
      className={`w-full h-16 shrink-0 bg-slate-900/90 backdrop-blur-lg border-b border-slate-800/90 px-3.5 flex items-center justify-between z-30 transition-colors sticky top-0 ${className}`}
      dir="rtl"
    >
      <div className="flex items-center gap-3">
        <DoctorAvatar size="md" showStatus={true} />
        <BrandMark showSubtitle={true} />
      </div>

      <div className="flex items-center">
        <MenuButton onClick={onMenuClick} isOpen={isMenuOpen} />
      </div>
    </header>
  );
};
''',

'src/components/layout/AppShell.tsx': '''import type { ReactNode } from 'react';
import { MobileHeader } from './MobileHeader';

export interface AppShellProps {
  children: ReactNode;
  footer?: ReactNode;
  onMenuClick?: () => void;
  isMenuOpen?: boolean;
  showHeader?: boolean;
}

export const AppShell = ({
  children,
  footer,
  onMenuClick,
  isMenuOpen = false,
  showHeader = true,
}: AppShellProps) => {
  return (
    <div className="w-full h-[100dvh] flex justify-center bg-slate-950 text-slate-100 overflow-hidden font-arabic select-none md:select-auto">
      <div className="w-full max-w-[440px] h-full flex flex-col bg-slate-900 shadow-2xl relative border-x border-slate-800/80 overflow-hidden">
        <div className="w-full pt-[var(--sat)] bg-slate-900/90 shrink-0" />
        {showHeader && <MobileHeader onMenuClick={onMenuClick} isMenuOpen={isMenuOpen} />}
        <main className="flex-1 w-full overflow-y-auto overflow-x-hidden flex flex-col relative">
          {children}
        </main>
        {footer && (
          <footer className="w-full shrink-0">
            {footer}
          </footer>
        )}
      </div>
    </div>
  );
};
''',

'src/components/chat/TypingIndicator.tsx': '''import { DoctorAvatar } from '../ui/DoctorAvatar';

export interface TypingIndicatorProps {
  className?: string;
}

export const TypingIndicator = ({ className = '' }: TypingIndicatorProps) => {
  return (
    <div className={`flex items-start gap-3 w-full animate-in fade-in duration-200 ${className}`} dir="rtl">
      <DoctorAvatar size="sm" showStatus={false} className="mt-1" />
      <div className="bg-slate-900 border border-slate-800 text-slate-200 rounded-2xl rounded-tr-sm px-4 py-3.5 flex items-center gap-1.5 shadow-sm shadow-slate-950/40">
        <span className="w-2 h-2 rounded-full bg-sky-400 animate-bounce [animation-delay:-0.3s]" />
        <span className="w-2 h-2 rounded-full bg-sky-400 animate-bounce [animation-delay:-0.15s]" />
        <span className="w-2 h-2 rounded-full bg-sky-400 animate-bounce" />
      </div>
    </div>
  );
};
''',

'src/components/chat/EvidenceSection.tsx': '''import { useState } from 'react';
import type { EvidenceSource } from '../../types/chat';
import { BookOpen, ChevronDown } from 'lucide-react';

export interface EvidenceSectionProps {
  evidence: EvidenceSource[];
  className?: string;
}

export const EvidenceSection = ({ evidence, className = '' }: EvidenceSectionProps) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!evidence || evidence.length === 0) return null;

  return (
    <div className={`mt-3 pt-2.5 border-t border-slate-800/80 w-full ${className}`} dir="rtl">
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        className="flex items-center justify-between w-full text-xs font-semibold text-sky-400 hover:text-sky-300 py-1 cursor-pointer transition-colors active:scale-[0.99]"
      >
        <span className="flex items-center gap-1.5">
          <BookOpen className="w-3.5 h-3.5 text-sky-400" />
          <span>المصادر الإكلينيكية المعتمدة ({evidence.length})</span>
        </span>
        <ChevronDown className={`w-3.5 h-3.5 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="mt-2 flex flex-col gap-2 animate-in fade-in slide-in-from-top-1 duration-200">
          {evidence.map((item) => (
            <div
              key={item.id}
              className="p-2.5 rounded-xl bg-slate-950/80 border border-slate-800 text-[12px] font-arabic text-slate-300 flex flex-col gap-1"
            >
              <div className="flex items-center justify-between font-semibold text-slate-200">
                <span>{item.title}</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-sky-500/10 text-sky-400 border border-sky-500/20">
                  {item.sourceDoc}
                </span>
              </div>
              {item.section && (
                <div className="text-[11px] text-slate-400">
                  <span>القسم: {item.section}</span>
                </div>
              )}
              {item.excerpt && (
                <p className="text-[11px] text-slate-400 italic bg-slate-900/60 p-2 rounded-lg border-r-2 border-sky-500 mt-0.5">
                  &ldquo;{item.excerpt}&rdquo;
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
''',

'src/components/chat/UserMessage.tsx': '''import type { ChatMessage } from '../../types/chat';

export interface UserMessageProps {
  message: ChatMessage;
}

export const UserMessage = ({ message }: UserMessageProps) => {
  return (
    <div className="w-full flex justify-start my-2 animate-in fade-in slide-in-from-bottom-2 duration-200" dir="rtl">
      <div className="max-w-[85%] sm:max-w-[75%] rounded-2xl rounded-tr-sm bg-gradient-to-br from-sky-600 to-blue-700 text-white px-4 py-3 shadow-md shadow-sky-950/40 border border-sky-500/40">
        <p className="text-sm font-arabic font-medium leading-relaxed whitespace-pre-wrap">
          {message.content}
        </p>
      </div>
    </div>
  );
};
''',

'src/components/chat/AssistantMessage.tsx': '''import type { ChatMessage } from '../../types/chat';
import { DoctorAvatar } from '../ui/DoctorAvatar';
import { EvidenceSection } from './EvidenceSection';
import { ShieldCheck, Info } from 'lucide-react';

export interface AssistantMessageProps {
  message: ChatMessage;
  showAvatar?: boolean;
}

export const AssistantMessage = ({
  message,
  showAvatar = true,
}: AssistantMessageProps) => {
  const structured = message.structured;

  return (
    <div className="w-full flex items-start gap-3 my-3 animate-in fade-in slide-in-from-bottom-2 duration-200" dir="rtl">
      {showAvatar ? (
        <DoctorAvatar size="sm" showStatus={false} className="mt-1 shrink-0" />
      ) : (
        <div className="w-9 shrink-0" />
      )}

      <div className="flex-1 max-w-[92%] sm:max-w-[85%] rounded-2xl rounded-tr-sm bg-slate-900 border border-slate-800/90 text-slate-100 p-4 shadow-sm shadow-slate-950/50">
        <div className="flex items-center gap-1.5 mb-2 pb-1.5 border-b border-slate-800/60">
          <span className="text-xs font-bold text-sky-400 font-arabic">د. سالم</span>
          <span className="text-[10px] font-medium text-slate-400">· استشاري طب وعلاج الإدمان</span>
        </div>

        {structured ? (
          <div className="flex flex-col gap-3 text-sm font-arabic leading-relaxed text-slate-200">
            {structured.paragraphs.map((p, idx) => (
              <p key={idx} className="whitespace-pre-wrap">{p}</p>
            ))}

            {structured.bulletPoints && structured.bulletPoints.length > 0 && (
              <ul className="list-disc list-inside flex flex-col gap-1.5 pr-1 text-slate-300">
                {structured.bulletPoints.map((point, idx) => (
                  <li key={idx} className="leading-snug">{point}</li>
                ))}
              </ul>
            )}

            {structured.keyTakeaway && (
              <div className="p-3 rounded-xl bg-sky-950/40 border border-sky-800/40 text-sky-200 text-xs flex items-start gap-2">
                <ShieldCheck className="w-4 h-4 shrink-0 text-sky-400 mt-0.5" />
                <span><strong>الخلاصة الطبية:</strong> {structured.keyTakeaway}</span>
              </div>
            )}

            {structured.safetyNote && (
              <div className="p-3 rounded-xl bg-amber-950/30 border border-amber-800/40 text-amber-200 text-xs flex items-start gap-2">
                <Info className="w-4 h-4 shrink-0 text-amber-400 mt-0.5" />
                <span>{structured.safetyNote}</span>
              </div>
            )}
          </div>
        ) : (
          <p className="text-sm font-arabic font-normal leading-relaxed text-slate-200 whitespace-pre-wrap">
            {message.content}
          </p>
        )}

        {message.evidence && message.evidence.length > 0 && (
          <EvidenceSection evidence={message.evidence} />
        )}
      </div>
    </div>
  );
};
''',

'src/components/chat/SuggestionChip.tsx': '''export interface SuggestionChipProps {
  text: string;
  onClick: (text: string) => void;
  className?: string;
}

export const SuggestionChip = ({
  text,
  onClick,
  className = '',
}: SuggestionChipProps) => {
  return (
    <button
      type="button"
      onClick={() => onClick(text)}
      className={`px-3.5 py-2 rounded-xl text-xs font-semibold font-arabic bg-slate-900/90 hover:bg-slate-800 active:bg-slate-900 text-slate-200 hover:text-sky-300 active:text-sky-400 border border-slate-800 hover:border-sky-500/40 shadow-sm shadow-slate-950/50 transition-all duration-200 cursor-pointer active:scale-95 text-right whitespace-normal leading-relaxed ${className}`}
      dir="rtl"
    >
      {text}
    </button>
  );
};
''',

'src/components/chat/EmptyChatState.tsx': '''import { DoctorAvatar } from '../ui/DoctorAvatar';
import { SuggestionChip } from './SuggestionChip';
import { Sparkles, MessageCircleQuestion } from 'lucide-react';

export interface EmptyChatStateProps {
  onSelectSuggestion: (prompt: string) => void;
  className?: string;
}

export const EmptyChatState = ({
  onSelectSuggestion,
  className = '',
}: EmptyChatStateProps) => {
  const suggestions = [
    'إزاي أتعامل مع الصداع والعصبية في أول 3 أيام بدون تدخين؟',
    'إيه جرعة اللصقات أو العلكة (NRT) المناسبة لو بشرب علبة في اليوم؟',
    'عايز خطة عملية تساعدني أوقف تدخين تدريجياً خلال أسبوعين.',
    'هل السجائر الإلكترونية (الفيب) وسيلة معتمدة طبياً للإقلاع؟',
  ];

  return (
    <div
      className={`flex flex-col items-center justify-center text-center px-4 py-6 max-w-md mx-auto w-full select-none ${className}`}
      dir="rtl"
    >
      <div className="relative mb-4">
        <DoctorAvatar size="lg" showStatus={true} />
        <div className="absolute -top-1 -right-1 bg-sky-500 text-white p-1 rounded-full shadow-md shadow-sky-950">
          <Sparkles className="w-3.5 h-3.5" />
        </div>
      </div>

      <h2 className="text-xl font-bold text-white mb-1.5 font-arabic tracking-tight">
        كيف يمكنني مساعدتك اليوم؟
      </h2>
      <p className="text-xs text-slate-300 mb-6 leading-relaxed font-arabic max-w-xs">
        اسألني عن الإقلاع، بدائل النيكوتين، التعامل مع الأعراض، أو خطتك المخصصة وفقاً لأدلة WHO 2024.
      </p>

      <div className="w-full flex flex-col gap-2 text-right">
        <div className="flex items-center gap-1.5 text-slate-400 text-xs font-semibold px-1 mb-1">
          <MessageCircleQuestion className="w-3.5 h-3.5 text-sky-400" />
          <span>أسئلة شائعة يمكنك البدء بها:</span>
        </div>
        <div className="flex flex-col gap-2">
          {suggestions.map((text, idx) => (
            <SuggestionChip
              key={idx}
              text={text}
              onClick={onSelectSuggestion}
            />
          ))}
        </div>
      </div>
    </div>
  );
};
''',

'src/components/chat/MobileComposer.tsx': '''import { useState, useEffect } from 'react';
import type { FormEvent, KeyboardEvent } from 'react';
import { Send, Sparkles } from 'lucide-react';
import { IconButton } from '../ui/IconButton';

export interface MobileComposerProps {
  onSendMessage?: (text: string) => void;
  disabled?: boolean;
  placeholder?: string;
  initialValue?: string;
  className?: string;
}

export const MobileComposer = ({
  onSendMessage,
  disabled = false,
  placeholder = "اسأل د. سالم عن الإقلاع، الأدوية، أو الأعراض...",
  initialValue = '',
  className = '',
}: MobileComposerProps) => {
  const [text, setText] = useState(initialValue);

  useEffect(() => {
    if (initialValue) {
      setText(initialValue);
    }
  }, [initialValue]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (text.trim() && !disabled) {
      onSendMessage?.(text.trim());
      setText('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div
      className={`w-full shrink-0 bg-slate-900/95 backdrop-blur-xl border-t border-slate-800/80 p-3 pb-[calc(0.75rem+var(--sab))] transition-all z-20 ${className}`}
      dir="rtl"
    >
      <form
        onSubmit={handleSubmit}
        className="flex items-end gap-2 bg-slate-800/90 rounded-2xl p-1.5 border border-slate-700/60 focus-within:border-sky-500/80 focus-within:ring-1 focus-within:ring-sky-500/50 transition-all shadow-inner"
      >
        <textarea
          rows={1}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder={placeholder}
          aria-label="مربع كتابة السؤال الطبي"
          className="flex-1 bg-transparent text-slate-100 placeholder-slate-400 text-sm font-arabic py-2.5 px-3 focus:outline-none resize-none max-h-32 min-h-[44px] disabled:opacity-50 leading-relaxed"
        />

        <div className="shrink-0 pb-0.5">
          <IconButton
            type="submit"
            ariaLabel="إرسال السؤال"
            disabled={!text.trim() || disabled}
            variant="primary"
            size="sm"
            className="w-10 h-10 rounded-xl"
          >
            {text.trim() ? (
              <Send className="w-4 h-4 -scale-x-100" />
            ) : (
              <Sparkles className="w-4 h-4 text-white/70" />
            )}
          </IconButton>
        </div>
      </form>

      <div className="text-center mt-2">
        <p className="text-[10px] text-slate-400 font-arabic flex items-center justify-center gap-1">
          <span>🛡️ مستند إلى الدليل الإكلينيكي لمنظمة الصحة العالمية 2024</span>
        </p>
      </div>
    </div>
  );
};
''',

'src/components/drawer/LogoutDialog.tsx': '''import { Button } from '../ui/Button';
import { Surface } from '../ui/Surface';
import { LogOut, AlertTriangle } from 'lucide-react';

export interface LogoutDialogProps {
  isOpen: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export const LogoutDialog = ({
  isOpen,
  onConfirm,
  onCancel,
}: LogoutDialogProps) => {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs animate-in fade-in duration-200"
      dir="rtl"
      role="dialog"
      aria-modal="true"
      aria-labelledby="logout-title"
    >
      <Surface
        variant="elevated"
        padding="lg"
        rounded="2xl"
        className="w-full max-w-xs text-center border border-slate-700 bg-slate-900 shadow-2xl flex flex-col items-center gap-4"
      >
        <div className="w-12 h-12 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-center justify-center">
          <AlertTriangle className="w-6 h-6" />
        </div>

        <div className="flex flex-col gap-1.5">
          <h3 id="logout-title" className="text-base font-bold text-white font-arabic">
            هل تريد تسجيل الخروج؟
          </h3>
          <p className="text-xs text-slate-300 font-arabic leading-relaxed">
            سيتم إنهاء جلسة تسجيل الدخول الحالية والعودة لشاشة البدء.
          </p>
        </div>

        <div className="w-full flex items-center gap-2 mt-2">
          <Button
            variant="danger"
            size="md"
            fullWidth
            onClick={onConfirm}
            leftIcon={<LogOut className="w-4 h-4" />}
          >
            تسجيل الخروج
          </Button>
          <Button
            variant="secondary"
            size="md"
            fullWidth
            onClick={onCancel}
          >
            إلغاء
          </Button>
        </div>
      </Surface>
    </div>
  );
};
''',

'src/components/drawer/ConversationItem.tsx': '''import type { ConversationSession } from '../../types/chat';
import { MessageSquare } from 'lucide-react';

export interface ConversationItemProps {
  conversation: ConversationSession;
  isActive: boolean;
  onClick: (conversation: ConversationSession) => void;
}

export const ConversationItem = ({
  conversation,
  isActive,
  onClick,
}: ConversationItemProps) => {
  return (
    <button
      type="button"
      onClick={() => onClick(conversation)}
      className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-right transition-all duration-200 cursor-pointer active:scale-[0.99] group ${
        isActive
          ? 'bg-sky-500/15 border border-sky-500/40 text-white font-semibold'
          : 'hover:bg-slate-800/70 active:bg-slate-800 text-slate-300 hover:text-white border border-transparent'
      }`}
      dir="rtl"
    >
      <MessageSquare
        className={`w-4 h-4 shrink-0 transition-colors ${
          isActive ? 'text-sky-400' : 'text-slate-400 group-hover:text-slate-300'
        }`}
      />
      <span className="text-xs font-arabic truncate flex-1">
        {conversation.title}
      </span>
    </button>
  );
};
''',

'src/components/drawer/SidebarDrawer.tsx': '''import { useEffect } from 'react';
import type { ConversationSession } from '../../types/chat';
import { DoctorAvatar } from '../ui/DoctorAvatar';
import { BrandMark } from '../ui/BrandMark';
import { IconButton } from '../ui/IconButton';
import { ConversationItem } from './ConversationItem';
import { Plus, X, Settings, LogOut, MessageSquareDashed } from 'lucide-react';

export interface SidebarDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  conversations: ConversationSession[];
  activeConversationId: string | null;
  onSelectConversation: (conv: ConversationSession) => void;
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
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const groups: Array<{ name: string; items: ConversationSession[] }> = [
    { name: 'اليوم', items: conversations.filter((c) => c.group === 'اليوم') },
    { name: 'أمس', items: conversations.filter((c) => c.group === 'أمس') },
    { name: 'هذا الأسبوع', items: conversations.filter((c) => c.group === 'هذا الأسبوع') },
  ].filter((g) => g.items.length > 0);

  return (
    <div className="fixed inset-0 z-40 flex justify-end" dir="rtl">
      <div
        onClick={onClose}
        className="fixed inset-0 bg-black/60 backdrop-blur-xs transition-opacity duration-300 animate-in fade-in"
        aria-hidden="true"
      />

      <div
        className="relative w-[85%] max-w-[360px] h-full bg-slate-900 border-l border-slate-800 shadow-2xl flex flex-col justify-between z-50 animate-in slide-in-from-right duration-300 select-none"
        role="dialog"
        aria-label="القائمة الجانبية والمحادثات"
      >
        <div className="p-4 border-b border-slate-800/80 flex items-center justify-between pt-[calc(1rem+var(--sat))]">
          <div className="flex items-center gap-2.5">
            <DoctorAvatar size="sm" showStatus={false} />
            <BrandMark showSubtitle={false} />
          </div>
          <IconButton
            ariaLabel="إغلاق القائمة"
            onClick={onClose}
            variant="ghost"
            size="sm"
            className="text-slate-400 hover:text-white"
          >
            <X className="w-5 h-5" />
          </IconButton>
        </div>

        <div className="p-3 border-b border-slate-800/60">
          <button
            type="button"
            onClick={onNewConversation}
            className="w-full h-11 px-3.5 rounded-xl bg-sky-500/10 hover:bg-sky-500/20 active:bg-sky-500/30 text-sky-400 font-bold text-xs font-arabic border border-sky-500/30 flex items-center justify-center gap-2 transition-all duration-200 cursor-pointer active:scale-[0.98]"
          >
            <Plus className="w-4 h-4" />
            <span>محادثة جديدة</span>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-3 flex flex-col gap-4">
          {groups.length === 0 ? (
            <div className="my-auto flex flex-col items-center justify-center text-center p-4 text-slate-400 gap-2">
              <MessageSquareDashed className="w-8 h-8 text-slate-500" />
              <p className="text-xs font-arabic">لا توجد محادثات سابقة بعد</p>
            </div>
          ) : (
            groups.map((group) => (
              <div key={group.name} className="flex flex-col gap-1">
                <span className="text-[11px] font-bold text-slate-400 px-2 uppercase tracking-wider font-arabic">
                  {group.name}
                </span>
                <div className="flex flex-col gap-1">
                  {group.items.map((conv) => (
                    <ConversationItem
                      key={conv.id}
                      conversation={conv}
                      isActive={conv.id === activeConversationId}
                      onClick={onSelectConversation}
                    />
                  ))}
                </div>
              </div>
            ))
          )}
        </div>

        <div className="p-3 border-t border-slate-800/90 flex flex-col gap-1 bg-slate-950/60 pb-[calc(0.75rem+var(--sab))]">
          <button
            type="button"
            onClick={onOpenSettings}
            className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-slate-300 hover:text-white hover:bg-slate-800/60 transition-colors text-xs font-arabic font-medium cursor-pointer"
          >
            <Settings className="w-4 h-4 text-slate-400" />
            <span>الإعدادات</span>
          </button>

          <button
            type="button"
            onClick={onOpenLogoutDialog}
            className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 transition-colors text-xs font-arabic font-medium cursor-pointer"
          >
            <LogOut className="w-4 h-4 text-rose-400" />
            <span>تسجيل الخروج</span>
          </button>
        </div>
      </div>
    </div>
  );
};
''',

'src/components/settings/SettingsScreen.tsx': '''import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Surface } from '../ui/Surface';
import { IconButton } from '../ui/IconButton';
import {
  ArrowRight,
  User,
  Globe,
  Moon,
  Lock,
  Database,
  Info,
  ShieldCheck,
  LogOut,
  ChevronLeft,
  X
} from 'lucide-react';

export interface SettingsScreenProps {
  onBack: () => void;
  onOpenLogoutDialog: () => void;
}

export const SettingsScreen = ({
  onBack,
  onOpenLogoutDialog,
}: SettingsScreenProps) => {
  const { user } = useAuth();
  const [appearance, setAppearance] = useState<'system' | 'light' | 'dark'>('dark');
  const [activeModal, setActiveModal] = useState<'privacy' | 'data' | 'about' | 'sources' | null>(null);

  return (
    <div className="w-full h-full flex flex-col justify-between bg-slate-950 text-white select-none font-arabic" dir="rtl">
      {/* Header */}
      <div className="w-full h-16 shrink-0 bg-slate-900 border-b border-slate-800 px-4 flex items-center justify-between pt-[var(--sat)]">
        <div className="flex items-center gap-3">
          <IconButton
            ariaLabel="الرجوع إلى المحادثة"
            onClick={onBack}
            variant="ghost"
            size="sm"
          >
            <ArrowRight className="w-5 h-5 text-slate-200" />
          </IconButton>
          <h1 className="text-base font-bold text-white font-arabic">الإعدادات</h1>
        </div>
      </div>

      {/* Main Settings List */}
      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-5">
        {/* 1. Account Section */}
        <div className="flex flex-col gap-2">
          <span className="text-[11px] font-bold text-slate-400 px-1 uppercase tracking-wider">
            الحساب
          </span>
          <Surface variant="card" padding="md" rounded="xl" className="flex items-center gap-3.5 border border-slate-800">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-sky-500 to-blue-700 flex items-center justify-center text-white font-bold text-lg border border-sky-400/40 shrink-0 shadow-md">
              {user?.name ? user.name.slice(0, 1) : <User className="w-6 h-6" />}
            </div>
            <div className="flex flex-col overflow-hidden">
              <span className="text-sm font-bold text-white truncate">
                {user?.name || 'محمد حسن'}
              </span>
              <span className="text-xs text-slate-400 truncate">
                {user?.email || 'mohamed.hassan@gmail.com'}
              </span>
              <span className="text-[10px] text-sky-400 font-semibold mt-0.5 flex items-center gap-1">
                <span>✓</span>
                <span>{user?.provider || 'Google Account'}</span>
              </span>
            </div>
          </Surface>
        </div>

        {/* 2. Application Preferences */}
        <div className="flex flex-col gap-2">
          <span className="text-[11px] font-bold text-slate-400 px-1 uppercase tracking-wider">
            التطبيق
          </span>
          <Surface variant="card" padding="none" rounded="xl" className="divide-y divide-slate-800/80 border border-slate-800 overflow-hidden">
            {/* Language */}
            <div className="flex items-center justify-between p-3.5">
              <div className="flex items-center gap-3 text-xs text-slate-200 font-medium">
                <Globe className="w-4 h-4 text-sky-400" />
                <span>اللغة</span>
              </div>
              <span className="text-xs text-slate-400 font-semibold px-2 py-1 rounded bg-slate-800">
                العربية
              </span>
            </div>

            {/* Appearance */}
            <div className="flex items-center justify-between p-3.5">
              <div className="flex items-center gap-3 text-xs text-slate-200 font-medium">
                <Moon className="w-4 h-4 text-sky-400" />
                <span>المظهر</span>
              </div>
              <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800 text-[11px]">
                <button
                  type="button"
                  onClick={() => setAppearance('dark')}
                  className={`px-2 py-0.5 rounded font-medium transition-colors ${appearance === 'dark' ? 'bg-sky-500 text-white' : 'text-slate-400 hover:text-white'}`}
                >
                  داكن
                </button>
                <button
                  type="button"
                  onClick={() => setAppearance('light')}
                  className={`px-2 py-0.5 rounded font-medium transition-colors ${appearance === 'light' ? 'bg-sky-500 text-white' : 'text-slate-400 hover:text-white'}`}
                >
                  فاتح
                </button>
                <button
                  type="button"
                  onClick={() => setAppearance('system')}
                  className={`px-2 py-0.5 rounded font-medium transition-colors ${appearance === 'system' ? 'bg-sky-500 text-white' : 'text-slate-400 hover:text-white'}`}
                >
                  النظام
                </button>
              </div>
            </div>
          </Surface>
        </div>

        {/* 3. Privacy & Data */}
        <div className="flex flex-col gap-2">
          <span className="text-[11px] font-bold text-slate-400 px-1 uppercase tracking-wider">
            الخصوصية والبيانات
          </span>
          <Surface variant="card" padding="none" rounded="xl" className="divide-y divide-slate-800/80 border border-slate-800 overflow-hidden">
            <button
              type="button"
              onClick={() => setActiveModal('privacy')}
              className="w-full flex items-center justify-between p-3.5 text-right hover:bg-slate-800/60 transition-colors cursor-pointer"
            >
              <div className="flex items-center gap-3 text-xs text-slate-200 font-medium">
                <Lock className="w-4 h-4 text-sky-400" />
                <span>سياسة الخصوصية</span>
              </div>
              <ChevronLeft className="w-4 h-4 text-slate-400" />
            </button>

            <button
              type="button"
              onClick={() => setActiveModal('data')}
              className="w-full flex items-center justify-between p-3.5 text-right hover:bg-slate-800/60 transition-colors cursor-pointer"
            >
              <div className="flex items-center gap-3 text-xs text-slate-200 font-medium">
                <Database className="w-4 h-4 text-sky-400" />
                <span>البيانات والمحادثات</span>
              </div>
              <ChevronLeft className="w-4 h-4 text-slate-400" />
            </button>
          </Surface>
        </div>

        {/* 4. About & Methodology */}
        <div className="flex flex-col gap-2">
          <span className="text-[11px] font-bold text-slate-400 px-1 uppercase tracking-wider">
            عن التطبيق
          </span>
          <Surface variant="card" padding="none" rounded="xl" className="divide-y divide-slate-800/80 border border-slate-800 overflow-hidden">
            <button
              type="button"
              onClick={() => setActiveModal('about')}
              className="w-full flex items-center justify-between p-3.5 text-right hover:bg-slate-800/60 transition-colors cursor-pointer"
            >
              <div className="flex items-center gap-3 text-xs text-slate-200 font-medium">
                <Info className="w-4 h-4 text-sky-400" />
                <span>عن Oxygen Medical RAG</span>
              </div>
              <ChevronLeft className="w-4 h-4 text-slate-400" />
            </button>

            <button
              type="button"
              onClick={() => setActiveModal('sources')}
              className="w-full flex items-center justify-between p-3.5 text-right hover:bg-slate-800/60 transition-colors cursor-pointer"
            >
              <div className="flex items-center gap-3 text-xs text-slate-200 font-medium">
                <ShieldCheck className="w-4 h-4 text-sky-400" />
                <span>المصادر والمنهجية الطبية</span>
              </div>
              <ChevronLeft className="w-4 h-4 text-slate-400" />
            </button>
          </Surface>
        </div>

        {/* 5. Account Actions */}
        <div className="flex flex-col gap-2 pt-2">
          <Surface variant="card" padding="none" rounded="xl" className="border border-rose-900/40 overflow-hidden">
            <button
              type="button"
              onClick={onOpenLogoutDialog}
              className="w-full flex items-center justify-between p-3.5 text-rose-400 hover:bg-rose-500/10 transition-colors cursor-pointer"
            >
              <div className="flex items-center gap-3 text-xs font-semibold">
                <LogOut className="w-4 h-4" />
                <span>تسجيل الخروج</span>
              </div>
              <ChevronLeft className="w-4 h-4 text-rose-400/60" />
            </button>
          </Surface>
        </div>

        {/* Footer info */}
        <div className="text-center py-4 text-[11px] text-slate-400 font-arabic">
          أوكسجين · الإصدار 1.0.0 (WHO 2024 Edition)
        </div>
      </div>

      {/* Info Modals */}
      {activeModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-xs animate-in fade-in duration-200" dir="rtl">
          <Surface variant="elevated" padding="lg" rounded="2xl" className="w-full max-w-sm max-h-[80vh] flex flex-col bg-slate-900 border border-slate-700 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-sm font-bold text-white font-arabic">
                {activeModal === 'privacy' && 'سياسة الخصوصية'}
                {activeModal === 'data' && 'البيانات والمحادثات'}
                {activeModal === 'about' && 'عن Oxygen Medical RAG'}
                {activeModal === 'sources' && 'المصادر والمنهجية'}
              </h3>
              <IconButton ariaLabel="إغلاق" onClick={() => setActiveModal(null)} variant="ghost" size="sm">
                <X className="w-4 h-4" />
              </IconButton>
            </div>

            <div className="flex-1 overflow-y-auto py-4 text-xs font-arabic text-slate-300 leading-relaxed flex flex-col gap-3">
              {activeModal === 'privacy' && (
                <>
                  <p>نستخدم بيانات الحساب والمحادثات لتقديم تجربة المساعد الطبي وحفظ استفساراتك وفق إعدادات الخدمة.</p>
                  <p>لا نقوم بمشاركة أي بيانات صحية شخصية مع أطراف دعائية أو غير مصرح لها.</p>
                </>
              )}
              {activeModal === 'data' && (
                <>
                  <p>ترتبط المحادثات بحسابك لتسهيل استرجاع خطة الإقلاع ومتابعة التطورات السلوكية.</p>
                  <p>يمكنك بدء محادثة جديدة أو إدارة الجلسات في أي وقت.</p>
                </>
              )}
              {activeModal === 'about' && (
                <>
                  <p>أوكسجين هو مساعد صحي وسلوكي متقدم مبني على تقنيات استرجاع وتأصيل الإجابات (RAG).</p>
                  <p>تم تدريب وتوجيه د. سالم لتقديم نصائح مبسطة ودافئة بالعامية المصرية مع الالتزام الصارم بالأدلة الطبية.</p>
                </>
              )}
              {activeModal === 'sources' && (
                <>
                  <p><strong>المصدر الطبي المعتمد:</strong></p>
                  <p>دليل منظمة الصحة العالمية الإكلينيكي للإقلاع عن التبغ لدى البالغين (WHO Clinical Treatment Guideline for Tobacco Cessation in Adults, 2024).</p>
                  <p>تخضع جميع الإجابات لتدقيق رقمي وسريري لضمان سلامة التوصيات.</p>
                </>
              )}
            </div>
          </Surface>
        </div>
      )}
    </div>
  );
};
''',

'src/components/chat/ChatScreen.tsx': '''import { useState, useRef, useEffect } from 'react';
import type { ChatMessage, ConversationSession } from '../../types/chat';
import { UserMessage } from './UserMessage';
import { AssistantMessage } from './AssistantMessage';
import { TypingIndicator } from './TypingIndicator';
import { EmptyChatState } from './EmptyChatState';
import { MobileComposer } from './MobileComposer';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { Surface } from '../ui/Surface';

export interface ChatScreenProps {
  activeConversation?: ConversationSession | null;
}

export const ChatScreen = ({
  activeConversation,
}: ChatScreenProps) => {
  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    return activeConversation ? activeConversation.messages : [];
  });
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [composerValue, setComposerValue] = useState<string>('');
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (activeConversation) {
      setMessages(activeConversation.messages);
    } else {
      setMessages([]);
    }
  }, [activeConversation]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSelectSuggestion = (promptText: string) => {
    setComposerValue(promptText);
  };

  const handleSendMessage = async (text: string) => {
    setErrorMessage(null);
    setComposerValue('');

    const userMsg: ChatMessage = {
      id: `msg_user_${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    setTimeout(() => {
      setIsLoading(false);

      const assistantMsg: ChatMessage = {
        id: `msg_assistant_${Date.now()}`,
        role: 'assistant',
        content: '',
        structured: {
          paragraphs: [
            'أهلاً بيك، خطوة ممتازة إنك بتسأل وتبدأ تفكر في صحتك. في أول 3 أيام بعد التوقف، جسمك بيبدأ يتخلص من النيكوتين تماماً، وطبيعي تحس ببعض الصداع والتوتر الخفيف.',
            'عشان تتعامل مع الصداع والتوتر بطريقة آمنة وفعالة، منظمة الصحة العالمية (WHO 2024) بتوصي بالخطوات التالية:',
          ],
          bulletPoints: [
            'شرب كميات وفيرة من المياه على مدار اليوم لتقليل الصداع ومساعدة الجسم.',
            'ممارسة تمارين التنفس العميق لمدة 3 دقائق عند الشعور بأي رغبة مفاجئة أو عصبية.',
            'إذا كنت تشرب أكثر من 20 سيجارة يومياً، يمكنك الاستفادة من بدائل النيكوتين (مثل اللصقات 21 مجم أو علكة النيكوتين 2-4 مجم) لتخفيف حدة الأعراض.',
          ],
          keyTakeaway: 'الأعراض دي ذروتها بتكون في أول 48 إلى 72 ساعة، وبعدها بتقل تدريجياً وبشكل ملحوظ.',
          safetyNote: 'إذا كان لديك تاريخ مع أمراض القلب الحادة أو قرحة المعدة، يرجى استشارة الطبيب قبل استخدام بدائل النيكوتين.',
        },
        evidence: [
          {
            id: 'ev_who_2024_nrt',
            title: 'توصيات بدائل النيكوتين (NRT) وجرعات البدء',
            sourceDoc: 'WHO Clinical Treatment Guideline 2024',
            section: 'Section 4.1: Pharmacotherapy Recommendations',
            excerpt: 'Nicotine replacement therapies (patches, gum) are strongly recommended as first-line treatment for tobacco cessation in adults.',
          },
          {
            id: 'ev_who_2024_behavioral',
            title: 'الدعم السلوكي وإدارة المحفزات اليومية',
            sourceDoc: 'WHO Clinical Treatment Guideline 2024',
            section: 'Section 3.2: Brief Behavioral Interventions',
            excerpt: 'Structured behavioral interventions combined with pharmacotherapy yield significantly higher cessation rates than unassisted quit attempts.',
          },
        ],
        timestamp: Date.now(),
      };

      setMessages((prev) => [...prev, assistantMsg]);
    }, 1200);
  };

  const handleRetry = () => {
    if (messages.length > 0) {
      const lastUserMsg = [...messages].reverse().find((m) => m.role === 'user');
      if (lastUserMsg) {
        handleSendMessage(lastUserMsg.content);
      }
    }
  };

  return (
    <div className="w-full h-full flex flex-col justify-between overflow-hidden bg-slate-950 text-slate-100 font-arabic">
      <div className="flex-1 w-full overflow-y-auto px-3.5 py-3 flex flex-col justify-start">
        {messages.length === 0 ? (
          <div className="my-auto">
            <EmptyChatState onSelectSuggestion={handleSelectSuggestion} />
          </div>
        ) : (
          <div className="w-full max-w-2xl mx-auto flex flex-col gap-1 pb-4">
            {messages.map((msg, idx) => {
              if (msg.role === 'user') {
                return <UserMessage key={msg.id} message={msg} />;
              }
              const prevMsg = messages[idx - 1];
              const showAvatar = !prevMsg || prevMsg.role !== 'assistant';
              return (
                <AssistantMessage
                  key={msg.id}
                  message={msg}
                  showAvatar={showAvatar}
                />
              );
            })}

            {isLoading && <TypingIndicator className="my-2" />}

            {errorMessage && (
              <Surface
                variant="card"
                padding="sm"
                rounded="lg"
                className="my-3 bg-rose-950/30 border-rose-800/40 text-rose-300 text-xs flex items-center justify-between"
                dir="rtl"
              >
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
                  <span>{errorMessage}</span>
                </div>
                <button
                  type="button"
                  onClick={handleRetry}
                  className="flex items-center gap-1 text-sky-400 hover:text-sky-300 px-2 py-1 rounded bg-slate-900 border border-slate-700"
                >
                  <RefreshCw className="w-3 h-3" />
                  <span>إعادة المحاولة</span>
                </button>
              </Surface>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <MobileComposer
        onSendMessage={handleSendMessage}
        initialValue={composerValue}
        disabled={isLoading}
        placeholder="اسأل د. سالم عن الإقلاع، الأدوية، أو الأعراض..."
      />
    </div>
  );
};
''',

'src/App.tsx': '''import { useState } from 'react';
import { useAuth } from './context/AuthContext';
import { SplashScreen } from './components/entry/SplashScreen';
import { OnboardingScreen } from './components/entry/OnboardingScreen';
import { LoginScreen } from './components/entry/LoginScreen';
import { AppShell } from './components/layout/AppShell';
import { ChatScreen } from './components/chat/ChatScreen';
import { SidebarDrawer } from './components/drawer/SidebarDrawer';
import { LogoutDialog } from './components/drawer/LogoutDialog';
import { SettingsScreen } from './components/settings/SettingsScreen';
import type { EntryStep } from './types/auth';
import type { ConversationSession } from './types/chat';

export function App() {
  const { user, hasSeenOnboarding, markOnboardingComplete, signOut } = useAuth();
  const [currentStep, setCurrentStep] = useState<EntryStep>('splash');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isLogoutDialogOpen, setIsLogoutDialogOpen] = useState(false);

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
          content: 'أهلاً بيك يا بطل! التوقف التدريجي مع وضع تاريخ محدد للهدف (Quit Date) يعتبر من أنجح الطرق المعتمدة في دليل WHO 2024.',
          timestamp: Date.now() - 3500000,
        }
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
        }
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

  const handleLoginSuccess = () => {
    setCurrentStep('chat_ready');
  };

  const handleMenuToggle = () => {
    setIsSidebarOpen((prev) => !prev);
  };

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

  // 1. Splash Screen
  if (currentStep === 'splash') {
    return <SplashScreen onComplete={handleSplashComplete} />;
  }

  // 2. Onboarding Screen
  if (currentStep === 'onboarding') {
    return <OnboardingScreen onComplete={handleOnboardingComplete} />;
  }

  // 3. Login Screen
  if (currentStep === 'login') {
    return <LoginScreen onSuccess={handleLoginSuccess} />;
  }

  // 4. Settings Screen
  if (currentStep === 'settings') {
    return (
      <>
        <AppShell showHeader={false}>
          <SettingsScreen
            onBack={() => setCurrentStep('chat_ready')}
            onOpenLogoutDialog={handleOpenLogout}
          />
        </AppShell>
        <LogoutDialog
          isOpen={isLogoutDialogOpen}
          onConfirm={handleConfirmLogout}
          onCancel={() => setIsLogoutDialogOpen(false)}
        />
      </>
    );
  }

  // 5. Primary Product Screen: Chat Screen + Sidebar Drawer
  return (
    <>
      <AppShell
        isMenuOpen={isSidebarOpen}
        onMenuClick={handleMenuToggle}
      >
        <ChatScreen
          activeConversation={activeConversation}
        />
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
''',

'public/manifest.json': '''{
  "name": "Oxygen Medical RAG",
  "short_name": "أوكسجين",
  "description": "المساعد الطبي السلوكي للإقلاع عن التدخين المستند لأدلة منظمة الصحة العالمية 2024 - د. سالم",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0b1329",
  "theme_color": "#0d47a1",
  "orientation": "portrait",
  "dir": "rtl",
  "lang": "ar",
  "icons": [
    {
      "src": "/icon-192.svg",
      "sizes": "192x192",
      "type": "image/svg+xml",
      "purpose": "any maskable"
    },
    {
      "src": "/icon-512.svg",
      "sizes": "512x512",
      "type": "image/svg+xml",
      "purpose": "any maskable"
    }
  ]
}
''',

'public/icon-192.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 192 192" width="192" height="192">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0284c7" />
      <stop offset="50%" stop-color="#1e40af" />
      <stop offset="100%" stop-color="#0b1329" />
    </linearGradient>
  </defs>
  <rect width="192" height="192" rx="40" fill="url(#bg)" />
  <circle cx="96" cy="96" r="70" fill="#0f172a" opacity="0.6" />
  <path d="M56 140 C56 108 74 85 96 85 C118 85 136 108 136 140" fill="#1e293b" />
  <path d="M78 115 L96 140 L114 115" stroke="#38bdf8" stroke-width="6" stroke-linecap="round" />
  <circle cx="96" cy="65" r="24" fill="#cbd5e1" />
  <path d="M72 58 C72 45 83 35 96 35 C109 35 120 45 120 58 C120 62 118 64 114 63 C110 61 105 57 96 57 C87 57 82 61 78 63 C74 64 72 62 72 58 Z" fill="#334155" />
  <circle cx="96" cy="122" r="6" fill="#38bdf8" />
</svg>
''',

'public/icon-512.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <linearGradient id="bg512" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0284c7" />
      <stop offset="50%" stop-color="#1e40af" />
      <stop offset="100%" stop-color="#0b1329" />
    </linearGradient>
  </defs>
  <rect width="512" height="512" rx="110" fill="url(#bg512)" />
  <circle cx="256" cy="256" r="185" fill="#0f172a" opacity="0.6" />
  <path d="M150 370 C150 290 198 230 256 230 C314 230 362 290 362 370" fill="#1e293b" />
  <path d="M208 305 L256 370 L304 305" stroke="#38bdf8" stroke-width="16" stroke-linecap="round" />
  <circle cx="256" cy="175" r="64" fill="#cbd5e1" />
  <path d="M192 155 C192 120 220 95 256 95 C292 95 320 120 320 155 C320 165 315 170 304 168 C294 162 280 152 256 152 C232 152 218 162 208 168 C197 170 192 165 192 155 Z" fill="#334155" />
  <circle cx="256" cy="325" r="16" fill="#38bdf8" />
</svg>
''',

'public/sw.js': '''// Oxygen Medical RAG — Progressive Web App Service Worker (Static Shell Cache)
const CACHE_NAME = 'oxygen-medical-rag-static-v1';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/icon-192.svg',
  '/icon-512.svg'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      )
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET' || event.request.url.includes('/api/')) {
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }
      return fetch(event.request).then((networkResponse) => {
        if (
          networkResponse &&
          networkResponse.status === 200 &&
          (event.request.url.endsWith('.js') ||
           event.request.url.endsWith('.css') ||
           event.request.url.endsWith('.svg') ||
           event.request.url.endsWith('.woff2'))
        ) {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
        }
        return networkResponse;
      }).catch(() => {
        if (event.request.mode === 'navigate') {
          return caches.match('/index.html');
        }
      });
    })
  );
});
''',

'src/components/pwa/NetworkBanner.tsx': '''import { useState, useEffect } from 'react';
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
''',

'src/components/pwa/InstallPromptModal.tsx': '''import { useState, useEffect } from 'react';
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
'''
}

for rel_path, code in files.items():
    os.makedirs(os.path.dirname(rel_path), exist_ok=True)
    with open(rel_path, 'w', encoding='utf-8') as f:
        f.write(code)
    print('Written:', rel_path)

print('Done!')


