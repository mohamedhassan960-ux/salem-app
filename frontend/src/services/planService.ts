import { supabase, isSupabaseConfigured } from './supabaseClient';
import type { UserQuitPlan, PlanTask, Milestone, HealthRecoveryInsight, PlanRecommendation } from '../types/plan';

const LOCAL_PLAN_KEY_PREFIX = 'salem_quit_plan_';

const DEFAULT_MILESTONES: Milestone[] = [
  {
    id: 'm_24h',
    title: 'أول 24 ساعة بدون تدخين',
    targetDurationDays: 1,
    description: 'انخفاض أول أكسيد الكربون في الدم وعودة الأكسجين لمستواه الطبيعي.',
    achieved: false,
    clinicalNote: 'تنخفض مستويات النيكوتين وأول أكسيد الكربون بسرعة، وتبدأ خلايا الدم الحمراء في نقل الأكسجين بكفاءة أعلى.',
  },
  {
    id: 'm_48h',
    title: '48 ساعة: عودة حاسة الشم والتذوق',
    targetDurationDays: 2,
    description: 'تجدد النهايات العصبية وبدء استعادة القدرة على تمييز النكهات والروائح.',
    achieved: false,
    clinicalNote: 'تبدأ النهايات العصبية التالفة بالتعافي مما يحسن الحواس بشكل ملحوظ.',
  },
  {
    id: 'm_7d',
    title: 'أسبوع كامل: التغلب على قمة الانسحاب',
    targetDurationDays: 7,
    description: 'تجاوز المرحلة الأصعب من الأعراض الجسدية واستقرار النبض وضغط الدم.',
    achieved: false,
    clinicalNote: 'تتخلص معظم أنسجة الجسم من النيكوتين تمامًا وتبدأ المرحلة السلوكية للتعافي المستدام.',
  },
  {
    id: 'm_30d',
    title: 'شهر كامل: تجدد طاقة الرئتين',
    targetDurationDays: 30,
    description: 'انخفاض ملحوظ في السعال وضيق التنفس وزيادة القدرة على بذل مجهود بدني.',
    achieved: false,
    clinicalNote: 'تتعافى الأهداب التنفسية في القصبة الهوائية وتبدأ في تنظيف الرئتين بفاعلية.',
  },
];

const DEFAULT_HEALTH_INSIGHTS: HealthRecoveryInsight[] = [
  {
    id: 'h_circ',
    timeframeLabel: 'خلال 20 دقيقة',
    title: 'انتظام ضغط الدم والنبض',
    explanation: 'يعود معدل ضربات القلب وضغط الدم لمستواهما الطبيعي تدريجيًا بعد التوقف.',
    isUnlocked: true,
    category: 'circulation',
  },
  {
    id: 'h_sensory',
    timeframeLabel: 'بعد 48 ساعة',
    title: 'تحسن حاسة التذوق والشم',
    explanation: 'تتعافى النهايات العصبية في الأنف واللسان وتصبح النكهات أغنى وأوضح.',
    isUnlocked: false,
    category: 'sensory',
  },
  {
    id: 'h_lungs',
    timeframeLabel: 'خلال أسبوعين إلى 3 أشهر',
    title: 'زيادة سعة الرئتين والدورة الدموية',
    explanation: 'يتحسن تدفق الدم في الأطراف وتزيد كفاءة الرئة بنسبة تصل إلى 30%.',
    isUnlocked: false,
    category: 'lungs',
  },
];

export const planService = {
  /**
   * Generates or loads user quit plan.
   */
  async getPlan(userId: string, quitStartDate: number = Date.now(), dailyCigarettes: number = 15): Promise<UserQuitPlan> {
    // 1. Try local storage first
    try {
      const saved = localStorage.getItem(`${LOCAL_PLAN_KEY_PREFIX}${userId}`);
      if (saved) {
        const plan: UserQuitPlan = JSON.parse(saved);
        // Refresh milestone achievement based on current elapsed days
        const daysElapsed = Math.floor((Date.now() - plan.quitStartDate) / (1000 * 60 * 60 * 24));
        plan.milestones = plan.milestones.map((m) => ({
          ...m,
          achieved: daysElapsed >= m.targetDurationDays,
          achievedAt: daysElapsed >= m.targetDurationDays ? plan.quitStartDate + m.targetDurationDays * 86400000 : undefined,
        }));
        return plan;
      }
    } catch {
      // ignore
    }

    // 2. Default Initial Plan
    const initialTasks: PlanTask[] = [
      {
        id: 't_morning_water',
        title: 'شرب كوب ماء كبير فور الاستيقاظ',
        description: 'يساعد في تنشيط الجسم وترطيب الحلق وكسر الرغبة الصباحية المعتادة.',
        category: 'physical',
        status: 'not_started',
        estimatedMinutes: 2,
      },
      {
        id: 't_breathing_session',
        title: 'تمرين التنفس العميق 4-7-8',
        description: 'جلسة هادئة لتهدئة ضربات القلب وخفض هرمونات التوتر في بداية اليوم.',
        category: 'mindset',
        status: 'not_started',
        estimatedMinutes: 3,
      },
      {
        id: 't_environment_clean',
        title: 'تطهير المكان من محفزات التدخين',
        description: 'التخلص من الولاعات والطفايات وتغيير مكان الجلوس المعتاد.',
        category: 'environment',
        status: 'not_started',
        estimatedMinutes: 5,
      },
    ];

    const initialRecommendations: PlanRecommendation[] = [
      {
        id: 'rec_coffee',
        title: 'التعامل مع قهوة الصباح',
        rationale: 'لو القهوة مرتبطة بالسيجارة، جرب تشربها في مكان مختلف أو تستبدلها بشاي أخضر أو عصير.',
        actionLabel: 'استشر سالم عن محفزات القهوة',
        actionType: 'chat',
      },
    ];

    const daysElapsed = Math.floor((Date.now() - quitStartDate) / (1000 * 60 * 60 * 24));
    const milestones = DEFAULT_MILESTONES.map((m) => ({
      ...m,
      achieved: daysElapsed >= m.targetDurationDays,
      achievedAt: daysElapsed >= m.targetDurationDays ? quitStartDate + m.targetDurationDays * 86400000 : undefined,
    }));

    const newPlan: UserQuitPlan = {
      id: `plan_${userId}`,
      userId,
      status: 'active',
      quitStartDate,
      dailyCigarettesBaseline: dailyCigarettes,
      packPriceEGP: 65,
      tasks: initialTasks,
      milestones,
      recommendations: initialRecommendations,
      updatedAt: Date.now(),
    };

    this.savePlan(newPlan);
    return newPlan;
  },

  /**
   * Persists updated plan to local storage and Supabase.
   */
  async savePlan(plan: UserQuitPlan): Promise<void> {
    try {
      localStorage.setItem(`${LOCAL_PLAN_KEY_PREFIX}${plan.userId}`, JSON.stringify(plan));
    } catch {
      // ignore
    }

    if (isSupabaseConfigured && supabase && plan.userId !== 'guest_user') {
      try {
        await supabase.from('quit_plans').upsert({
          id: plan.id,
          user_id: plan.userId,
          status: plan.status,
          quit_start_date: new Date(plan.quitStartDate).toISOString(),
          daily_cigarettes_baseline: plan.dailyCigarettesBaseline,
          pack_price_egp: plan.packPriceEGP,
          tasks: plan.tasks,
          milestones: plan.milestones,
          updated_at: new Date().toISOString(),
        });
      } catch (err) {
        console.warn('[planService] Error saving plan to Supabase:', err);
      }
    }
  },

  /**
   * Toggles task completion state.
   */
  async toggleTaskStatus(userId: string, taskId: string): Promise<UserQuitPlan | null> {
    const plan = await this.getPlan(userId);
    if (!plan) return null;

    plan.tasks = plan.tasks.map((task) => {
      if (task.id === taskId) {
        const nextStatus = task.status === 'completed' ? 'not_started' : 'completed';
        return {
          ...task,
          status: nextStatus,
          completedAt: nextStatus === 'completed' ? Date.now() : undefined,
        };
      }
      return task;
    });

    plan.updatedAt = Date.now();
    await this.savePlan(plan);
    return plan;
  },

  /**
   * Retrieves evidence-grounded health insights.
   */
  getHealthInsights(smokeFreeDays: number): HealthRecoveryInsight[] {
    return DEFAULT_HEALTH_INSIGHTS.map((h, i) => {
      let isUnlocked = false;
      if (i === 0) isUnlocked = true;
      if (i === 1 && smokeFreeDays >= 2) isUnlocked = true;
      if (i === 2 && smokeFreeDays >= 14) isUnlocked = true;
      return {
        ...h,
        isUnlocked,
      };
    });
  },
};
