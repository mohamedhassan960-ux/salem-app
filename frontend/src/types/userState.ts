/**
 * SALEM — User State & Clinical Intervention Data Models
 * Supports real state tracking: Smoking Profile, Quit Journey, Cravings, Relapses, Daily Tasks, and Behavioral Insights.
 */

export type TobaccoType = 'cigarettes' | 'shisha' | 'vape' | 'heated_tobacco' | 'other';

export type UserStateEnum =
  | 'before_quit'
  | 'quit_day'
  | 'early_quit'
  | 'stable_progress'
  | 'craving_period'
  | 'relapse'
  | 'restart';

export interface SmokingProfile {
  tobaccoType: TobaccoType;
  tobaccoTypeCustom?: string;
  dailyCigarettes: number; // estimated average
  packPriceEGP?: number;   // cost calculation
  lastSmokedAt: number;    // timestamp in ms
  primaryTriggers: string[];
  quitGoal: string;
  onboardingCompletedAt: number;
}

export interface CravingEvent {
  id: string;
  timestamp: number;
  intensityBefore: number; // 1 to 10
  intensityAfter?: number;  // 1 to 10
  trigger?: string;
  interventionType: 'breathing_478' | 'delay_distract' | 'water_walk' | 'chat_coach';
  completed: boolean;
  notes?: string;
}

export interface RelapseEvent {
  id: string;
  timestamp: number;
  trigger: string;
  context: string;
  cigarettesCount: number;
  cravingIntensity: number; // 1 to 10
  reflectionNotes?: string;
  actionPlan: string;
}

export interface DailyPlanStep {
  id: string;
  title: string;
  description: string;
  category: 'behavioral' | 'cognitive' | 'mindfulness' | 'review';
  completed: boolean;
  completedAt?: number;
  stateTarget?: UserStateEnum[];
}

export interface BehavioralInsight {
  id: string;
  title: string;
  description: string;
  highlight: string;
  category: 'trigger' | 'timing' | 'resilience';
  confidence: number;
}

export interface UserStats {
  smokeFreeDays: number;
  smokeFreeHours: number;
  smokeFreeFormatted: string;
  cigarettesAvoided: number;
  moneySavedEGP: number;
  cravingsManagedCount: number;
  relapseCount: number;
  dailyTasksCompletedCount: number;
  dailyTasksTotalCount: number;
}
