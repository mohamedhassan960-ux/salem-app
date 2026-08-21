import type { EvidenceSource } from './chat';

export type InterventionState =
  | 'idle'
  | 'starting'
  | 'active'
  | 'waiting_for_input'
  | 'next_step'
  | 'check_in'
  | 'completed'
  | 'skipped'
  | 'cancelled'
  | 'error'
  | 'safety';

export type InterventionActionType =
  | 'breathing_478'
  | 'timer'
  | 'delay_distract'
  | 'water_walk'
  | 'reflect'
  | 'urge_surfing'
  | 'contact_support';

export interface InterventionStep {
  stepNumber: number;
  totalSteps: number;
  title: string;
  explanation: string;
  actionType: InterventionActionType;
  durationSeconds?: number;
  primaryActionLabel: string;
  secondaryActionLabel?: string;
  allowSkip?: boolean;
}

export interface InterventionSession {
  id: string;
  userId: string;
  state: InterventionState;
  interventionType: 'craving' | 'relapse' | 'stress' | 'routine';
  startedAt: number;
  completedAt?: number;
  currentStepIndex: number;
  steps: InterventionStep[];
  trigger?: string;
  intensityBefore?: number; // 1 to 10 or 1 to 5
  intensityAfter?: number;
  outcome?: 'lower' | 'same' | 'higher';
  citations?: EvidenceSource[];
  isInterrupted?: boolean;
}
