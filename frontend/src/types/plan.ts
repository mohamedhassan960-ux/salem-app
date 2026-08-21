import type { EvidenceSource } from './chat';

export type JourneyStatus = 'active' | 'slipped' | 'relapsed' | 'paused' | 'completed';

export type TaskStatus = 'not_started' | 'in_progress' | 'completed' | 'skipped' | 'locked';

export interface PlanTask {
  id: string;
  title: string;
  description: string;
  category: 'behavioral' | 'mindset' | 'physical' | 'environment';
  status: TaskStatus;
  estimatedMinutes?: number;
  completedAt?: number;
}

export interface Milestone {
  id: string;
  title: string;
  targetDurationDays: number;
  description: string;
  achieved: boolean;
  achievedAt?: number;
  clinicalNote?: string;
  source?: EvidenceSource;
}

export interface HealthRecoveryInsight {
  id: string;
  timeframeLabel: string;
  title: string;
  explanation: string;
  isUnlocked: boolean;
  category: 'circulation' | 'lungs' | 'sensory' | 'cellular';
  source?: EvidenceSource;
}

export interface PlanRecommendation {
  id: string;
  title: string;
  rationale: string;
  actionLabel: string;
  actionType: 'craving' | 'chat' | 'task' | 'breathing';
}

export interface UserQuitPlan {
  id: string;
  userId: string;
  status: JourneyStatus;
  quitStartDate: number;
  dailyCigarettesBaseline: number;
  packPriceEGP: number;
  tasks: PlanTask[];
  milestones: Milestone[];
  recommendations: PlanRecommendation[];
  updatedAt: number;
}
