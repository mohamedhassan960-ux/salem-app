import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import type { AuthContextType, AuthStatus, AuthStep, UserProfile } from '../types/auth';
import { authService } from '../services/authService';
import { profileService } from '../services/profileService';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [authStep, setAuthStep] = useState<AuthStep>('splash');
  const [status, setStatus] = useState<AuthStatus>('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [hasSeenOnboarding, setHasSeenOnboarding] = useState<boolean>(false);

  // Initialize auth session on launch
  useEffect(() => {
    let isMounted = true;

    async function initSession() {
      try {
        const sessionUser = await authService.getCurrentSession();
        if (!isMounted) return;

        if (sessionUser) {
          setUser(sessionUser);
          const isDone = await profileService.hasCompletedOnboarding(sessionUser.id);
          if (!isMounted) return;

          setHasSeenOnboarding(isDone);
          // Transition from splash happens after Splash timer
        } else {
          setUser(null);
          setHasSeenOnboarding(false);
        }
      } catch (err) {
        console.error('[AuthContext] Session init error:', err);
      }
    }

    initSession();

    // Subscribe to auth changes
    const unsubscribe = authService.onAuthStateChange(async (updatedUser) => {
      if (!isMounted) return;
      setUser(updatedUser);
      if (updatedUser) {
        const isDone = await profileService.hasCompletedOnboarding(updatedUser.id);
        if (!isMounted) return;
        setHasSeenOnboarding(isDone);
        if (authStep !== 'splash') {
          setAuthStep(isDone ? 'chat_ready' : 'onboarding');
        }
      } else {
        setHasSeenOnboarding(false);
      }
    });

    return () => {
      isMounted = false;
      unsubscribe();
    };
  }, []);

  const clearError = () => setErrorMessage(null);

  const signInWithGoogle = async (): Promise<boolean> => {
    setStatus('loading');
    setErrorMessage(null);
    try {
      const { user: authedUser, error } = await authService.signInWithGoogle();
      if (error) {
        setStatus('error');
        setErrorMessage(error);
        return false;
      }

      if (authedUser) {
        setUser(authedUser);
        const isDone = await profileService.hasCompletedOnboarding(authedUser.id);
        setHasSeenOnboarding(isDone);
        setStatus('success');
        setAuthStep(isDone ? 'chat_ready' : 'onboarding');
        return true;
      }
      return true; // OAuth redirect
    } catch {
      setStatus('error');
      setErrorMessage('تعذر تسجيل الدخول باستخدام Google. حاول مرة أخرى.');
      return false;
    }
  };

  const signInWithEmail = async (email: string, password: string): Promise<boolean> => {
    setStatus('loading');
    setErrorMessage(null);
    try {
      const { user: authedUser, error } = await authService.signInWithEmail(email, password);
      if (error || !authedUser) {
        setStatus('error');
        setErrorMessage(error || 'تعذر تسجيل الدخول. يرجى التحقق من البيانات.');
        return false;
      }

      setUser(authedUser);
      const isDone = await profileService.hasCompletedOnboarding(authedUser.id);
      setHasSeenOnboarding(isDone);
      setStatus('success');
      setAuthStep(isDone ? 'chat_ready' : 'onboarding');
      return true;
    } catch {
      setStatus('error');
      setErrorMessage('حصلت مشكلة أثناء تسجيل الدخول. جرّب تاني.');
      return false;
    }
  };

  const signUpWithEmail = async (
    email: string,
    password: string,
    name: string
  ): Promise<{ success: boolean; requiresEmailVerification: boolean }> => {
    setStatus('loading');
    setErrorMessage(null);
    try {
      const { user: newUser, requiresEmailVerification, error } = await authService.signUpWithEmail(
        email,
        password,
        name
      );

      if (error) {
        setStatus('error');
        setErrorMessage(error);
        return { success: false, requiresEmailVerification: false };
      }

      if (requiresEmailVerification) {
        setStatus('success');
        setAuthStep('email_confirmation');
        return { success: true, requiresEmailVerification: true };
      }

      if (newUser) {
        setUser(newUser);
        setHasSeenOnboarding(false);
        setStatus('success');
        setAuthStep('onboarding');
        return { success: true, requiresEmailVerification: false };
      }

      return { success: true, requiresEmailVerification: false };
    } catch {
      setStatus('error');
      setErrorMessage('حصلت مشكلة أثناء إنشاء الحساب. جرّب تاني.');
      return { success: false, requiresEmailVerification: false };
    }
  };

  const resetPasswordForEmail = async (email: string): Promise<boolean> => {
    setStatus('loading');
    setErrorMessage(null);
    try {
      const { success, error } = await authService.resetPassword(email);
      if (error) {
        setStatus('error');
        setErrorMessage(error);
        return false;
      }
      setStatus('success');
      return success;
    } catch {
      setStatus('error');
      setErrorMessage('تعذر إرسال رابط إعادة التعيين. جرّب تاني.');
      return false;
    }
  };

  const signOut = async () => {
    setStatus('loading');
    try {
      await authService.signOut();
      setUser(null);
      setHasSeenOnboarding(false);
      setStatus('idle');
      setAuthStep('login');
    } catch {
      setStatus('idle');
    }
  };

  const markOnboardingComplete = () => {
    setHasSeenOnboarding(true);
    setAuthStep('chat_ready');
  };

  const resetOnboarding = () => {
    setHasSeenOnboarding(false);
    setAuthStep('onboarding');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        status,
        errorMessage,
        authStep,
        hasSeenOnboarding,
        setAuthStep,
        signInWithGoogle,
        signInWithEmail,
        signUpWithEmail,
        resetPasswordForEmail,
        signOut,
        markOnboardingComplete,
        resetOnboarding,
        clearError,
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
