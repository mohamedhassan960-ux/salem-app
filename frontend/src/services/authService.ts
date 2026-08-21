import { supabase, isSupabaseConfigured } from './supabaseClient';
import type { UserProfile } from '../types/auth';

const LOCAL_USER_KEY = 'salem_auth_user_v2';
const LOCAL_SESSION_KEY = 'salem_auth_session_v2';

/**
 * Maps technical errors into clear, friendly Arabic error messages without technical jargon.
 */
export function mapAuthErrorToArabic(error: unknown): string {
  if (!error) return 'حصلت مشكلة أثناء تسجيل الدخول. جرّب تاني.';

  const message = (typeof error === 'object' && error !== null && 'message' in error)
    ? String((error as { message: unknown }).message).toLowerCase()
    : String(error).toLowerCase();

  if (message.includes('invalid login credentials') || message.includes('invalid credentials')) {
    return 'البريد الإلكتروني أو كلمة المرور غير صحيحة.';
  }
  if (message.includes('email not confirmed') || message.includes('confirm your email')) {
    return 'يرجى مراجعة بريدك الإلكتروني لتأكيد الحساب قبل تسجيل الدخول.';
  }
  if (message.includes('user already registered') || message.includes('already registered')) {
    return 'هذا البريد مسجل مسبقاً. يمكنك تسجيل الدخول مباشرة.';
  }
  if (message.includes('password') && (message.includes('weak') || message.includes('short') || message.includes('least 6') || message.includes('least 8'))) {
    return 'كلمة المرور يجب أن تكون 8 أحرف على الأقل.';
  }
  if (message.includes('too many requests') || message.includes('rate limit') || message.includes('over_email_send_rate_limit')) {
    return 'حاول تاني بعد شوية.';
  }
  if (message.includes('network') || message.includes('failed to fetch') || message.includes('timeout')) {
    return 'مش قادرين نتصل بالخدمة دلوقتي. جرّب تاني.';
  }

  return 'حصلت مشكلة أثناء المعالجة. جرّب تاني.';
}

export const authService = {
  /**
   * Retrieves the current user session from Supabase or local storage.
   */
  async getCurrentSession(): Promise<UserProfile | null> {
    if (isSupabaseConfigured && supabase) {
      try {
        const { data, error } = await supabase.auth.getSession();
        if (error || !data.session?.user) return null;

        const u = data.session.user;
        const profile: UserProfile = {
          id: u.id,
          name: u.user_metadata?.full_name || u.user_metadata?.name || u.email?.split('@')[0] || 'مستخدم سالم',
          email: u.email || '',
          avatarUrl: u.user_metadata?.avatar_url || undefined,
          provider: u.app_metadata?.provider || 'email',
          createdAt: new Date(u.created_at).getTime(),
          lastLoginAt: Date.now(),
          emailVerified: Boolean(u.email_confirmed_at),
        };
        return profile;
      } catch (err) {
        console.error('[authService] Error getting Supabase session:', err);
        return null;
      }
    }

    // Local fallback
    try {
      const saved = localStorage.getItem(LOCAL_USER_KEY);
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  },

  /**
   * Triggers Google OAuth sign in.
   */
  async signInWithGoogle(): Promise<{ user: UserProfile | null; error: string | null }> {
    if (isSupabaseConfigured && supabase) {
      try {
        const { error } = await supabase.auth.signInWithOAuth({
          provider: 'google',
          options: {
            redirectTo: window.location.origin,
          },
        });
        if (error) throw error;
        return { user: null, error: null }; // Redirects user to Google
      } catch (err) {
        return { user: null, error: mapAuthErrorToArabic(err) };
      }
    }

    // Fallback simulation for local development
    try {
      await new Promise((resolve) => setTimeout(resolve, 800));
      const mockUser: UserProfile = {
        id: `usr_${Date.now()}`,
        name: 'مستخدم سالم',
        email: 'user@salem.app',
        provider: 'google',
        createdAt: Date.now(),
        lastLoginAt: Date.now(),
        emailVerified: true,
      };
      localStorage.setItem(LOCAL_USER_KEY, JSON.stringify(mockUser));
      return { user: mockUser, error: null };
    } catch (err) {
      return { user: null, error: mapAuthErrorToArabic(err) };
    }
  },

  /**
   * Signs in with email and password.
   */
  async signInWithEmail(email: string, password: string): Promise<{ user: UserProfile | null; error: string | null }> {
    if (isSupabaseConfigured && supabase) {
      try {
        const { data, error } = await supabase.auth.signInWithPassword({
          email: email.trim(),
          password,
        });
        if (error) throw error;
        if (!data.user) throw new Error('No user returned');

        const u = data.user;
        const profile: UserProfile = {
          id: u.id,
          name: u.user_metadata?.full_name || u.user_metadata?.name || u.email?.split('@')[0] || 'مستخدم سالم',
          email: u.email || email.trim(),
          provider: 'email',
          createdAt: new Date(u.created_at).getTime(),
          lastLoginAt: Date.now(),
          emailVerified: Boolean(u.email_confirmed_at),
        };
        return { user: profile, error: null };
      } catch (err) {
        return { user: null, error: mapAuthErrorToArabic(err) };
      }
    }

    // Fallback simulation
    try {
      await new Promise((resolve) => setTimeout(resolve, 600));
      const mockUser: UserProfile = {
        id: `usr_${Date.now()}`,
        name: email.split('@')[0] || 'مستخدم سالم',
        email: email.trim(),
        provider: 'email',
        createdAt: Date.now(),
        lastLoginAt: Date.now(),
        emailVerified: true,
      };
      localStorage.setItem(LOCAL_USER_KEY, JSON.stringify(mockUser));
      return { user: mockUser, error: null };
    } catch (err) {
      return { user: null, error: mapAuthErrorToArabic(err) };
    }
  },

  /**
   * Signs up a new account with email and password.
   */
  async signUpWithEmail(
    email: string,
    password: string,
    name: string
  ): Promise<{ user: UserProfile | null; requiresEmailVerification: boolean; error: string | null }> {
    if (isSupabaseConfigured && supabase) {
      try {
        const { data, error } = await supabase.auth.signUp({
          email: email.trim(),
          password,
          options: {
            data: {
              full_name: name.trim(),
            },
          },
        });
        if (error) throw error;

        const requiresEmailVerification = Boolean(data.user && !data.session);
        let profile: UserProfile | null = null;
        if (data.user) {
          profile = {
            id: data.user.id,
            name: name.trim() || data.user.email?.split('@')[0] || 'مستخدم سالم',
            email: data.user.email || email.trim(),
            provider: 'email',
            createdAt: new Date(data.user.created_at).getTime(),
            lastLoginAt: Date.now(),
            emailVerified: Boolean(data.user.email_confirmed_at),
          };
        }

        return { user: profile, requiresEmailVerification, error: null };
      } catch (err) {
        return { user: null, requiresEmailVerification: false, error: mapAuthErrorToArabic(err) };
      }
    }

    // Fallback simulation
    try {
      await new Promise((resolve) => setTimeout(resolve, 600));
      const mockUser: UserProfile = {
        id: `usr_${Date.now()}`,
        name: name.trim() || 'مستخدم سالم',
        email: email.trim(),
        provider: 'email',
        createdAt: Date.now(),
        lastLoginAt: Date.now(),
        emailVerified: true,
      };
      localStorage.setItem(LOCAL_USER_KEY, JSON.stringify(mockUser));
      return { user: mockUser, requiresEmailVerification: false, error: null };
    } catch (err) {
      return { user: null, requiresEmailVerification: false, error: mapAuthErrorToArabic(err) };
    }
  },

  /**
   * Sends password reset email.
   */
  async resetPassword(email: string): Promise<{ success: boolean; error: string | null }> {
    if (isSupabaseConfigured && supabase) {
      try {
        const { error } = await supabase.auth.resetPasswordForEmail(email.trim(), {
          redirectTo: `${window.location.origin}/reset-password`,
        });
        if (error) throw error;
        return { success: true, error: null };
      } catch (err) {
        return { success: false, error: mapAuthErrorToArabic(err) };
      }
    }

    // Fallback simulation
    await new Promise((resolve) => setTimeout(resolve, 500));
    return { success: true, error: null };
  },

  /**
   * Signs out the current user session.
   */
  async signOut(): Promise<void> {
    if (isSupabaseConfigured && supabase) {
      try {
        await supabase.auth.signOut();
      } catch (err) {
        console.error('[authService] Error signing out:', err);
      }
    }
    try {
      localStorage.removeItem(LOCAL_USER_KEY);
      localStorage.removeItem(LOCAL_SESSION_KEY);
    } catch {
      // ignore
    }
  },

  /**
   * Subscribes to auth state changes.
   */
  onAuthStateChange(callback: (user: UserProfile | null) => void): () => void {
    if (isSupabaseConfigured && supabase) {
      const { data: { subscription } } = supabase.auth.onAuthStateChange(async (_event, session) => {
        if (!session?.user) {
          callback(null);
          return;
        }
        const u = session.user;
        const profile: UserProfile = {
          id: u.id,
          name: u.user_metadata?.full_name || u.user_metadata?.name || u.email?.split('@')[0] || 'مستخدم سالم',
          email: u.email || '',
          avatarUrl: u.user_metadata?.avatar_url || undefined,
          provider: u.app_metadata?.provider || 'email',
          createdAt: new Date(u.created_at).getTime(),
          lastLoginAt: Date.now(),
          emailVerified: Boolean(u.email_confirmed_at),
        };
        callback(profile);
      });

      return () => {
        subscription.unsubscribe();
      };
    }

    return () => {};
  },
};
