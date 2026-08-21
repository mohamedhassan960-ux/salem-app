import { createContext, useContext, useState, useEffect, useMemo, type ReactNode } from 'react';
import type {
  SmokingProfile,
  UserStateEnum,
  CravingEvent,
  RelapseEvent,
  DailyPlanStep,
  BehavioralInsight,
  UserStats,
  TobaccoType,
} from '../types/userState';

interface UserStateContextType {
  smokingProfile: SmokingProfile | null;
  userState: UserStateEnum;
  stats: UserStats;
  dailyTasks: DailyPlanStep[];
  cravings: CravingEvent[];
  relapses: RelapseEvent[];
  insights: BehavioralInsight[];
  activeIntervention: 'craving' | 'relapse' | null;
  setActiveIntervention: (val: 'craving' | 'relapse' | null) => void;
  updateSmokingProfile: (profile: Partial<SmokingProfile>) => void;
  toggleTaskCompletion: (taskId: string) => void;
  recordCravingStart: (intensity: number, trigger?: string, interventionType?: CravingEvent['interventionType']) => string;
  completeCraving: (id: string, intensityAfter: number, notes?: string) => void;
  recordRelapse: (event: Omit<RelapseEvent, 'id' | 'timestamp'>) => void;
  resetJourney: (newQuitDate?: number) => void;
}

const STORAGE_KEY_PROFILE = 'salem_user_smoking_profile_v2';
const STORAGE_KEY_CRAVINGS = 'salem_cravings_log_v2';
const STORAGE_KEY_RELAPSES = 'salem_relapses_log_v2';
const STORAGE_KEY_TASKS = 'salem_daily_tasks_v2';

const DEFAULT_DAILY_TASKS: DailyPlanStep[] = [
  {
    id: 'task_1',
    title: 'مراقبة وتسجيل أول محفز للرغبة اليوم',
    description: 'لاحظ الموقف أو التوقيت اللي بيثير رغبتك بالتدخين بدون استسلام.',
    category: 'behavioral',
    completed: false,
  },
  {
    id: 'task_2',
    title: 'تطبيق تمرين التنفس العميق (4-7-8) عند الشعور بالتوتر',
    description: 'يساعد في تهدئة الجهاز العصبي وتقليل حدة الرغبة خلال دقائق.',
    category: 'mindfulness',
    completed: false,
  },
  {
    id: 'task_3',
    title: 'شرب كوب ماء بارد وتأجيل الرغبة لمدة 5 دقائق',
    description: 'الرغبة في النيكوتين موجة قصيرة بتنخفض تدريجيًا بعد مرور 3-5 دقائق.',
    category: 'cognitive',
    completed: false,
  },
  {
    id: 'task_4',
    title: 'مراجعة التقدم اليومي ومشاركة المشاعر مع سالم',
    description: 'خصص دقيقة في نهاية اليوم لتقييم يومك وتثبيت إنجازك.',
    category: 'review',
    completed: false,
  },
];

const UserStateContext = createContext<UserStateContextType | undefined>(undefined);

export const UserStateProvider = ({ children }: { children: ReactNode }) => {
  // 1. Smoking Profile
  const [smokingProfile, setSmokingProfile] = useState<SmokingProfile | null>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY_PROFILE);
      if (saved) return JSON.parse(saved);
    } catch {
      // ignore
    }
    return null;
  });

  // 2. Cravings Log
  const [cravings, setCravings] = useState<CravingEvent[]>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY_CRAVINGS);
      if (saved) return JSON.parse(saved);
    } catch {
      // ignore
    }
    return [];
  });

  // 3. Relapses Log
  const [relapses, setRelapses] = useState<RelapseEvent[]>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY_RELAPSES);
      if (saved) return JSON.parse(saved);
    } catch {
      // ignore
    }
    return [];
  });

  // 4. Daily Tasks
  const [dailyTasks, setDailyTasks] = useState<DailyPlanStep[]>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY_TASKS);
      if (saved) return JSON.parse(saved);
    } catch {
      // ignore
    }
    return DEFAULT_DAILY_TASKS;
  });

  // 5. Active Intervention Modal trigger
  const [activeIntervention, setActiveIntervention] = useState<'craving' | 'relapse' | null>(null);

  // Persistence effects
  useEffect(() => {
    try {
      if (smokingProfile) {
        localStorage.setItem(STORAGE_KEY_PROFILE, JSON.stringify(smokingProfile));
      }
    } catch {
      // ignore
    }
  }, [smokingProfile]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY_CRAVINGS, JSON.stringify(cravings));
    } catch {
      // ignore
    }
  }, [cravings]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY_RELAPSES, JSON.stringify(relapses));
    } catch {
      // ignore
    }
  }, [relapses]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY_TASKS, JSON.stringify(dailyTasks));
    } catch {
      // ignore
    }
  }, [dailyTasks]);

  // Derived user state
  const userState: UserStateEnum = useMemo(() => {
    if (!smokingProfile) return 'before_quit';
    const now = Date.now();
    const diffHours = (now - smokingProfile.lastSmokedAt) / (1000 * 60 * 60);

    if (diffHours < 0) return 'before_quit';
    if (diffHours < 24) return 'quit_day';
    if (diffHours < 72) return 'early_quit';
    return 'stable_progress';
  }, [smokingProfile]);

  // Dynamically derived stats from real timestamps & logs
  const stats: UserStats = useMemo(() => {
    if (!smokingProfile || !smokingProfile.lastSmokedAt) {
      return {
        smokeFreeDays: 0,
        smokeFreeHours: 0,
        smokeFreeFormatted: 'رحلتك تبدأ الآن',
        cigarettesAvoided: 0,
        moneySavedEGP: 0,
        cravingsManagedCount: cravings.filter((c) => c.completed).length,
        relapseCount: relapses.length,
        dailyTasksCompletedCount: dailyTasks.filter((t) => t.completed).length,
        dailyTasksTotalCount: dailyTasks.length,
      };
    }

    const now = Date.now();
    const totalMs = Math.max(0, now - smokingProfile.lastSmokedAt);
    const totalHours = Math.floor(totalMs / (1000 * 60 * 60));
    const totalDays = Math.floor(totalHours / 24);
    const remainingHours = totalHours % 24;

    const daysFraction = totalMs / (1000 * 60 * 60 * 24);
    const dailyRate = smokingProfile.dailyCigarettes || 15;
    const cigarettesAvoided = Math.round(daysFraction * dailyRate);

    // Assuming average 20 cigarettes per pack, default 60 EGP per pack
    const packPrice = smokingProfile.packPriceEGP || 60;
    const costPerCig = packPrice / 20;
    const moneySavedEGP = Math.round(cigarettesAvoided * costPerCig);

    let formatted = '';
    if (totalDays === 0) {
      formatted = `${totalHours} ساعة بدون تدخين`;
    } else if (totalDays === 1) {
      formatted = `يوم و ${remainingHours} ساعة`;
    } else {
      formatted = `${totalDays} يوم بدون تدخين`;
    }

    return {
      smokeFreeDays: totalDays,
      smokeFreeHours: totalHours,
      smokeFreeFormatted: formatted,
      cigarettesAvoided,
      moneySavedEGP,
      cravingsManagedCount: cravings.filter((c) => c.completed).length,
      relapseCount: relapses.length,
      dailyTasksCompletedCount: dailyTasks.filter((t) => t.completed).length,
      dailyTasksTotalCount: dailyTasks.length,
    };
  }, [smokingProfile, cravings, relapses, dailyTasks]);

  // Behavioral Insights — ONLY generated when there is enough real data
  const insights: BehavioralInsight[] = useMemo(() => {
    const list: BehavioralInsight[] = [];
    if (cravings.length >= 2) {
      // Find most frequent trigger
      const triggerCounts: Record<string, number> = {};
      cravings.forEach((c) => {
        if (c.trigger) {
          triggerCounts[c.trigger] = (triggerCounts[c.trigger] || 0) + 1;
        }
      });
      const entries = Object.entries(triggerCounts);
      if (entries.length > 0) {
        entries.sort((a, b) => b[1] - a[1]);
        const [topTrigger, count] = entries[0];
        list.push({
          id: 'insight_top_trigger',
          title: 'أكثر محفز تم رصده',
          description: `المحفز الأكثر تكراراً في رغباتك هو "${topTrigger}".`,
          highlight: topTrigger,
          category: 'trigger',
          confidence: Math.min(1, count / cravings.length),
        });
      }

      // Success rate
      const completedCount = cravings.filter((c) => c.completed).length;
      if (completedCount > 0) {
        const rate = Math.round((completedCount / cravings.length) * 100);
        list.push({
          id: 'insight_resilience',
          title: 'نسبة تجاوز نوبات الرغبة',
          description: `نجحت في تجاوز ${completedCount} من أصل ${cravings.length} نوبة رغبة مسجلة.`,
          highlight: `${rate}% نجاح`,
          category: 'resilience',
          confidence: 0.9,
        });
      }
    }

    return list;
  }, [cravings]);

  // Actions
  const updateSmokingProfile = (partial: Partial<SmokingProfile>) => {
    setSmokingProfile((prev) => {
      const updated: SmokingProfile = {
        tobaccoType: 'cigarettes' as TobaccoType,
        dailyCigarettes: 15,
        lastSmokedAt: Date.now(),
        primaryTriggers: ['التوتر وضغط العمل', 'بعد شرب القهوة'],
        quitGoal: 'تحسين صحتي واستعادة لياقتي',
        onboardingCompletedAt: Date.now(),
        ...prev,
        ...partial,
      };
      return updated;
    });
  };

  const toggleTaskCompletion = (taskId: string) => {
    setDailyTasks((prev) =>
      prev.map((t) =>
        t.id === taskId
          ? { ...t, completed: !t.completed, completedAt: !t.completed ? Date.now() : undefined }
          : t
      )
    );
  };

  const recordCravingStart = (
    intensity: number,
    trigger?: string,
    interventionType: CravingEvent['interventionType'] = 'breathing_478'
  ): string => {
    const newId = `crav_${Date.now()}`;
    const newCraving: CravingEvent = {
      id: newId,
      timestamp: Date.now(),
      intensityBefore: intensity,
      trigger,
      interventionType,
      completed: false,
    };
    setCravings((prev) => [newCraving, ...prev]);
    return newId;
  };

  const completeCraving = (id: string, intensityAfter: number, notes?: string) => {
    setCravings((prev) =>
      prev.map((c) =>
        c.id === id
          ? {
              ...c,
              intensityAfter,
              completed: true,
              notes,
            }
          : c
      )
    );
  };

  const recordRelapse = (eventData: Omit<RelapseEvent, 'id' | 'timestamp'>) => {
    const newRelapse: RelapseEvent = {
      ...eventData,
      id: `rel_${Date.now()}`,
      timestamp: Date.now(),
    };
    setRelapses((prev) => [newRelapse, ...prev]);

    // Update lastSmokedAt timestamp without resetting history or judgment
    setSmokingProfile((prev) => {
      if (!prev) return null;
      return {
        ...prev,
        lastSmokedAt: Date.now(),
      };
    });
  };

  const resetJourney = (newQuitDate: number = Date.now()) => {
    setSmokingProfile((prev) => {
      if (!prev) return null;
      return {
        ...prev,
        lastSmokedAt: newQuitDate,
      };
    });
    setDailyTasks(DEFAULT_DAILY_TASKS);
  };

  return (
    <UserStateContext.Provider
      value={{
        smokingProfile,
        userState,
        stats,
        dailyTasks,
        cravings,
        relapses,
        insights,
        activeIntervention,
        setActiveIntervention,
        updateSmokingProfile,
        toggleTaskCompletion,
        recordCravingStart,
        completeCraving,
        recordRelapse,
        resetJourney,
      }}
    >
      {children}
    </UserStateContext.Provider>
  );
};

export const useUserState = (): UserStateContextType => {
  const context = useContext(UserStateContext);
  if (!context) {
    throw new Error('useUserState must be used within a UserStateProvider');
  }
  return context;
};
