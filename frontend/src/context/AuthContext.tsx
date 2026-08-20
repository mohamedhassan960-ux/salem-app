import { createContext, useContext, useState, useEffect } from 'react';
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
