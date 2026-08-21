import { supabase, isSupabaseConfigured } from './supabaseClient';
import type { InterventionSession, InterventionStep } from '../types/intervention';

const ACTIVE_INTERVENTION_KEY_PREFIX = 'salem_active_intervention_';
const INTERVENTION_HISTORY_KEY_PREFIX = 'salem_intervention_history_';

const DEFAULT_CRAVING_STEPS: InterventionStep[] = [
  {
    stepNumber: 1,
    totalSteps: 3,
    title: 'تأجيل الاستجابة (دقيقة واحدة)',
    explanation: 'الرغبة في النيكوتين موجة قصيرة بتوصل لقمتها وتنخفض تدريجيًا. خلينا ننتظر دقيقة واحدة مع بعض قبل أي تصرف.',
    actionType: 'timer',
    durationSeconds: 60,
    primaryActionLabel: 'ابدأ الدقيقة الآن',
    secondaryActionLabel: 'تخطي للخطوة التالية',
    allowSkip: true,
  },
  {
    stepNumber: 2,
    totalSteps: 3,
    title: 'تمرين التنفس العميق (4-7-8)',
    explanation: 'تنفس بطيء وعميق يساعد في تهدئة الجهاز العصبي وخفض إفراز هرمونات التوتر.',
    actionType: 'breathing_478',
    durationSeconds: 90,
    primaryActionLabel: 'ابدأ تمرين التنفس',
    secondaryActionLabel: 'تخطي',
    allowSkip: true,
  },
  {
    stepNumber: 3,
    totalSteps: 3,
    title: 'شرب ماء بارد وكسر الروتين',
    explanation: 'اشرب نصف كوب ماء بارد ببطء وغيّر مكان جلوسك لكسر المحفز الحركي للتدخين.',
    actionType: 'water_walk',
    primaryActionLabel: 'أتممت الخطوة',
    secondaryActionLabel: 'تم',
    allowSkip: false,
  },
];

export const interventionService = {
  /**
   * Creates a new structured craving intervention session.
   */
  createCravingSession(
    userId: string,
    trigger: string = 'التوتر وضغط العمل',
    intensityBefore: number = 7
  ): InterventionSession {
    const session: InterventionSession = {
      id: `interv_${Date.now()}`,
      userId,
      state: 'active',
      interventionType: 'craving',
      startedAt: Date.now(),
      currentStepIndex: 0,
      steps: DEFAULT_CRAVING_STEPS,
      trigger,
      intensityBefore,
      citations: [
        {
          id: 'who_beh_2024',
          title: 'دليل WHO 2024: التدخلات السلوكية الموجزة (Brief Behavioral Interventions)',
          organization: 'منظمة الصحة العالمية (WHO)',
          year: '2024',
          sourceType: 'دليل إكلينيكي معتمد',
          whyRelevant: 'تأجيل الاستجابة وتقنيات التنفس السلوكي تزيد من معدل الصمود وتجاوز الرغبة الحادة بنسبة تتجاوز 70%.',
        },
      ],
    };

    this.saveActiveSession(session);
    return session;
  },

  /**
   * Saves active in-progress session to local storage for recovery.
   */
  saveActiveSession(session: InterventionSession): void {
    try {
      localStorage.setItem(
        `${ACTIVE_INTERVENTION_KEY_PREFIX}${session.userId}`,
        JSON.stringify(session)
      );
    } catch {
      // ignore
    }
  },

  /**
   * Retrieves active in-progress session if any.
   */
  getActiveSession(userId: string): InterventionSession | null {
    try {
      const saved = localStorage.getItem(`${ACTIVE_INTERVENTION_KEY_PREFIX}${userId}`);
      if (saved) {
        const session: InterventionSession = JSON.parse(saved);
        // Exclude sessions older than 2 hours to avoid stale popups
        if (Date.now() - session.startedAt < 2 * 60 * 60 * 1000 && session.state !== 'completed') {
          return session;
        }
      }
    } catch {
      // ignore
    }
    return null;
  },

  /**
   * Clears active in-progress session.
   */
  clearActiveSession(userId: string): void {
    try {
      localStorage.removeItem(`${ACTIVE_INTERVENTION_KEY_PREFIX}${userId}`);
    } catch {
      // ignore
    }
  },

  /**
   * Completes an intervention and persists to history and Supabase.
   */
  async completeSession(
    session: InterventionSession,
    intensityAfter: number,
    outcome: 'lower' | 'same' | 'higher'
  ): Promise<InterventionSession> {
    const completedSession: InterventionSession = {
      ...session,
      state: 'completed',
      completedAt: Date.now(),
      intensityAfter,
      outcome,
    };

    // 1. Remove active session draft
    this.clearActiveSession(session.userId);

    // 2. Save to local history
    try {
      const savedHistory = localStorage.getItem(`${INTERVENTION_HISTORY_KEY_PREFIX}${session.userId}`);
      const history: InterventionSession[] = savedHistory ? JSON.parse(savedHistory) : [];
      localStorage.setItem(
        `${INTERVENTION_HISTORY_KEY_PREFIX}${session.userId}`,
        JSON.stringify([completedSession, ...history])
      );
    } catch {
      // ignore
    }

    // 3. Persist to Supabase if configured
    if (isSupabaseConfigured && supabase && session.userId !== 'guest_user') {
      try {
        await supabase.from('intervention_outcomes').insert({
          id: completedSession.id,
          user_id: completedSession.userId,
          intervention_type: completedSession.interventionType,
          trigger: completedSession.trigger,
          intensity_before: completedSession.intensityBefore,
          intensity_after: completedSession.intensityAfter,
          outcome: completedSession.outcome,
          started_at: new Date(completedSession.startedAt).toISOString(),
          completed_at: new Date(completedSession.completedAt!).toISOString(),
        });
      } catch (err) {
        console.warn('[interventionService] Error saving intervention outcome to Supabase:', err);
      }
    }

    return completedSession;
  },
};
