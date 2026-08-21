export type AuthStep =
  | 'splash'
  | 'login'
  | 'signup'
  | 'forgot_password'
  | 'email_confirmation'
  | 'onboarding'
  | 'chat_ready';

export type AuthStatus = 'idle' | 'loading' | 'success' | 'error';

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  avatarUrl?: string;
  provider?: string;
  createdAt?: number;
  lastLoginAt?: number;
  emailVerified?: boolean;
}

export interface AuthContextType {
  user: UserProfile | null;
  status: AuthStatus;
  errorMessage: string | null;
  authStep: AuthStep;
  hasSeenOnboarding: boolean;
  setAuthStep: (step: AuthStep) => void;
  signInWithGoogle: () => Promise<boolean>;
  signInWithEmail: (email: string, password: string) => Promise<boolean>;
  signUpWithEmail: (email: string, password: string, name: string) => Promise<{ success: boolean; requiresEmailVerification: boolean }>;
  resetPasswordForEmail: (email: string) => Promise<boolean>;
  signOut: () => Promise<void>;
  markOnboardingComplete: () => void;
  resetOnboarding: () => void;
  clearError: () => void;
}
