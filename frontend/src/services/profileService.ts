import { supabase, isSupabaseConfigured } from './supabaseClient';
import type { SmokingProfile } from '../types/userState';

const LOCAL_SMOKING_PROFILE_PREFIX = 'salem_smoking_profile_';
const LOCAL_ONBOARDING_COMPLETED_PREFIX = 'salem_onboarding_done_';
const LOCAL_USER_NAME_PREFIX = 'salem_user_name_';

export const profileService = {
  /**
   * Checks if the user has completed onboarding.
   */
  async hasCompletedOnboarding(userId: string): Promise<boolean> {
    // 1. Check local storage cache first for instant response
    try {
      const isDone = localStorage.getItem(`${LOCAL_ONBOARDING_COMPLETED_PREFIX}${userId}`);
      if (isDone === 'true') return true;
    } catch {
      // ignore
    }

    // 2. Query Supabase if configured
    if (isSupabaseConfigured && supabase) {
      try {
        const { data, error } = await supabase
          .from('smoking_profiles')
          .select('user_id')
          .eq('user_id', userId)
          .maybeSingle();

        if (error && error.code !== 'PGRST116') {
          console.warn('[profileService] Supabase check error:', error);
        }

        const completed = Boolean(data);
        if (completed) {
          localStorage.setItem(`${LOCAL_ONBOARDING_COMPLETED_PREFIX}${userId}`, 'true');
        }
        return completed;
      } catch (err) {
        console.error('[profileService] Error querying smoking profile:', err);
      }
    }

    return false;
  },

  /**
   * Fetches the user's smoking profile.
   */
  async getSmokingProfile(userId: string): Promise<SmokingProfile | null> {
    if (isSupabaseConfigured && supabase) {
      try {
        const { data, error } = await supabase
          .from('smoking_profiles')
          .select('*')
          .eq('user_id', userId)
          .maybeSingle();

        if (!error && data) {
          const profile: SmokingProfile = {
            tobaccoType: data.tobacco_type || 'cigarettes',
            tobaccoTypeCustom: data.tobacco_type_custom || undefined,
            dailyCigarettes: data.daily_cigarettes || 15,
            packPriceEGP: data.pack_price_egp || 60,
            lastSmokedAt: data.last_smoked_at ? new Date(data.last_smoked_at).getTime() : Date.now(),
            primaryTriggers: data.primary_triggers || [],
            quitGoal: data.quit_goal || 'تحسين صحتي واستعادة لياقتي',
            onboardingCompletedAt: data.created_at ? new Date(data.created_at).getTime() : Date.now(),
          };
          // Sync to local storage
          localStorage.setItem(`${LOCAL_SMOKING_PROFILE_PREFIX}${userId}`, JSON.stringify(profile));
          return profile;
        }
      } catch (err) {
        console.error('[profileService] Error getting smoking profile from Supabase:', err);
      }
    }

    // Fallback to local storage
    try {
      const saved = localStorage.getItem(`${LOCAL_SMOKING_PROFILE_PREFIX}${userId}`);
      if (saved) return JSON.parse(saved);
    } catch {
      // ignore
    }

    return null;
  },

  /**
   * Saves or updates the user's smoking profile and marks onboarding completed.
   */
  async saveSmokingProfile(userId: string, profile: SmokingProfile): Promise<boolean> {
    // 1. Always save locally immediately
    try {
      localStorage.setItem(`${LOCAL_SMOKING_PROFILE_PREFIX}${userId}`, JSON.stringify(profile));
      localStorage.setItem(`${LOCAL_ONBOARDING_COMPLETED_PREFIX}${userId}`, 'true');
    } catch {
      // ignore
    }

    // 2. Persist to Supabase if configured
    if (isSupabaseConfigured && supabase) {
      try {
        const payload = {
          user_id: userId,
          tobacco_type: profile.tobaccoType,
          tobacco_type_custom: profile.tobaccoTypeCustom || null,
          daily_cigarettes: profile.dailyCigarettes,
          pack_price_egp: profile.packPriceEGP || 60,
          last_smoked_at: new Date(profile.lastSmokedAt).toISOString(),
          primary_triggers: profile.primaryTriggers,
          quit_goal: profile.quitGoal,
          updated_at: new Date().toISOString(),
        };

        const { error } = await supabase
          .from('smoking_profiles')
          .upsert(payload, { onConflict: 'user_id' });

        if (error) {
          console.warn('[profileService] Supabase upsert error (saved locally):', error);
          return false;
        }
        return true;
      } catch (err) {
        console.error('[profileService] Exception saving smoking profile to Supabase:', err);
        return false;
      }
    }

    return true;
  },

  /**
   * Updates the user's display name in metadata and local cache.
   */
  async updateUserName(userId: string, newName: string): Promise<boolean> {
    try {
      localStorage.setItem(`${LOCAL_USER_NAME_PREFIX}${userId}`, newName);
    } catch {
      // ignore
    }

    if (isSupabaseConfigured && supabase) {
      try {
        const { error } = await supabase.auth.updateUser({
          data: { name: newName, full_name: newName },
        });
        if (error) {
          console.warn('[profileService] Supabase updateUser error:', error);
          return false;
        }
      } catch (err) {
        console.error('[profileService] Error updating user name in Supabase:', err);
        return false;
      }
    }

    return true;
  },

  /**
   * Performs complete account deletion and purges local data.
   */
  async deleteAccount(userId: string): Promise<boolean> {
    // Purge local storage entries
    try {
      localStorage.removeItem(`${LOCAL_SMOKING_PROFILE_PREFIX}${userId}`);
      localStorage.removeItem(`${LOCAL_ONBOARDING_COMPLETED_PREFIX}${userId}`);
      localStorage.removeItem(`${LOCAL_USER_NAME_PREFIX}${userId}`);
      localStorage.removeItem('salem_conversations_v3');
      localStorage.removeItem('salem_conversations_v2');
      localStorage.removeItem(`salem_quit_plan_${userId}`);
      localStorage.removeItem(`salem_active_intervention_${userId}`);
      localStorage.removeItem(`salem_intervention_history_${userId}`);
      localStorage.removeItem(`salem_user_settings_${userId}`);
    } catch {
      // ignore
    }

    if (isSupabaseConfigured && supabase && userId !== 'guest_user') {
      try {
        // Delete user related records in Supabase tables
        await supabase.from('messages').delete().eq('conversation_id', userId);
        await supabase.from('conversations').delete().eq('user_id', userId);
        await supabase.from('smoking_profiles').delete().eq('user_id', userId);
        await supabase.from('quit_plans').delete().eq('user_id', userId);
        await supabase.from('intervention_outcomes').delete().eq('user_id', userId);
      } catch (err) {
        console.warn('[profileService] Error deleting user records in Supabase:', err);
      }
    }

    return true;
  },
};
