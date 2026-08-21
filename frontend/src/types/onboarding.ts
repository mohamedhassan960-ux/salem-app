export type TobaccoTypeOption = 'cigarettes' | 'shisha' | 'vape' | 'heated_tobacco' | 'other';

export type GoalOption = 'quit_completely' | 'reduce' | 'undecided';

export interface OnboardingAnswers {
  tobaccoTypes: string[];
  dailyCount: number | 'unsure';
  lastSmokedAt: number;
  lastSmokedOption: 'today' | 'yesterday' | 'days_ago' | 'not_yet';
  primaryTriggers: string[];
  goal: GoalOption;
  readiness: number; // 1 to 5
  startedAt?: number;
  completedAt?: number;
}

export type OnboardingStepIndex = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7;
