import { supabase, isSupabaseConfigured } from './supabaseClient';

export interface UserSettings {
  dailyReminders: boolean;
  cravingCheckins: boolean;
  evidenceDetails: boolean;
  hapticFeedback: boolean;
  language: 'ar';
}

const DEFAULT_SETTINGS: UserSettings = {
  dailyReminders: true,
  cravingCheckins: true,
  evidenceDetails: true,
  hapticFeedback: true,
  language: 'ar',
};

const SETTINGS_KEY_PREFIX = 'salem_user_settings_';

export const settingsService = {
  /**
   * Loads user settings from local storage or Supabase.
   */
  async getSettings(userId: string): Promise<UserSettings> {
    try {
      const saved = localStorage.getItem(`${SETTINGS_KEY_PREFIX}${userId}`);
      if (saved) {
        return { ...DEFAULT_SETTINGS, ...JSON.parse(saved) };
      }
    } catch {
      // ignore
    }

    if (isSupabaseConfigured && supabase && userId !== 'guest_user') {
      try {
        const { data } = await supabase
          .from('user_settings')
          .select('*')
          .eq('user_id', userId)
          .maybeSingle();

        if (data) {
          const settings: UserSettings = {
            dailyReminders: data.daily_reminders ?? true,
            cravingCheckins: data.craving_checkins ?? true,
            evidenceDetails: data.evidence_details ?? true,
            hapticFeedback: data.haptic_feedback ?? true,
            language: 'ar',
          };
          localStorage.setItem(`${SETTINGS_KEY_PREFIX}${userId}`, JSON.stringify(settings));
          return settings;
        }
      } catch (err) {
        console.warn('[settingsService] Supabase load error:', err);
      }
    }

    return DEFAULT_SETTINGS;
  },

  /**
   * Saves user settings locally and to Supabase.
   */
  async saveSettings(userId: string, settings: UserSettings): Promise<boolean> {
    try {
      localStorage.setItem(`${SETTINGS_KEY_PREFIX}${userId}`, JSON.stringify(settings));
    } catch {
      // ignore
    }

    if (isSupabaseConfigured && supabase && userId !== 'guest_user') {
      try {
        await supabase.from('user_settings').upsert({
          user_id: userId,
          daily_reminders: settings.dailyReminders,
          craving_checkins: settings.cravingCheckins,
          evidence_details: settings.evidenceDetails,
          haptic_feedback: settings.hapticFeedback,
          updated_at: new Date().toISOString(),
        });
      } catch (err) {
        console.warn('[settingsService] Supabase save error:', err);
      }
    }

    return true;
  },
};
