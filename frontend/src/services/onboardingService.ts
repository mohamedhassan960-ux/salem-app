import type { OnboardingAnswers } from '../types/onboarding';
import type { SmokingProfile, TobaccoType } from '../types/userState';
import { profileService } from './profileService';

const DRAFT_STORAGE_KEY_PREFIX = 'salem_onboarding_draft_';

export const onboardingService = {
  /**
   * Saves partial in-progress answers to localStorage so user doesn't lose draft.
   */
  saveDraft(userId: string, answers: Partial<OnboardingAnswers>): void {
    try {
      localStorage.setItem(`${DRAFT_STORAGE_KEY_PREFIX}${userId}`, JSON.stringify(answers));
    } catch {
      // ignore
    }
  },

  /**
   * Retrieves saved draft answers.
   */
  getDraft(userId: string): Partial<OnboardingAnswers> | null {
    try {
      const saved = localStorage.getItem(`${DRAFT_STORAGE_KEY_PREFIX}${userId}`);
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  },

  /**
   * Clears saved draft after completion.
   */
  clearDraft(userId: string): void {
    try {
      localStorage.removeItem(`${DRAFT_STORAGE_KEY_PREFIX}${userId}`);
    } catch {
      // ignore
    }
  },

  /**
   * Submits completed onboarding answers: converts to SmokingProfile and saves to profileService.
   */
  async submitOnboarding(userId: string, answers: OnboardingAnswers): Promise<{ success: boolean; profile: SmokingProfile }> {
    // Map main primary tobacco type
    const primaryTobacco: TobaccoType =
      answers.tobaccoTypes.length > 0 && ['cigarettes', 'shisha', 'vape', 'heated_tobacco', 'other'].includes(answers.tobaccoTypes[0])
        ? (answers.tobaccoTypes[0] as TobaccoType)
        : 'cigarettes';

    const dailyCount = typeof answers.dailyCount === 'number' ? answers.dailyCount : 15;

    const profile: SmokingProfile = {
      tobaccoType: primaryTobacco,
      dailyCigarettes: dailyCount,
      packPriceEGP: 60,
      lastSmokedAt: answers.lastSmokedAt || Date.now(),
      primaryTriggers: answers.primaryTriggers.length > 0 ? answers.primaryTriggers : ['التوتر وضغط العمل'],
      quitGoal: answers.goal === 'quit_completely'
        ? 'التوقف النهائي عن التدخين واستعادة صحتي'
        : answers.goal === 'reduce'
        ? 'التقليل التدريجي تمهيداً للإقلاع'
        : 'فهم أسباب رغبتي وتحديد الخطة المناسبة',
      onboardingCompletedAt: Date.now(),
    };

    // Save profile authoritative
    const success = await profileService.saveSmokingProfile(userId, profile);

    // Clear draft on finish
    onboardingService.clearDraft(userId);

    return { success, profile };
  },
};
