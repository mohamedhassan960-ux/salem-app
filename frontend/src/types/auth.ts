export type EntryStep = 'splash' | 'onboarding' | 'login' | 'chat_ready' | 'settings';

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
