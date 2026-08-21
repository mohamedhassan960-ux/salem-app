import { useState, useEffect } from 'react';
import { useUserState } from '../../state/UserStateContext';
import { useAuth } from '../../context/AuthContext';
import { planService } from '../../services/planService';
import { PlanHero } from './PlanHero';
import { NextActionCard } from './NextActionCard';
import { DailyPlanCard } from './DailyPlanCard';
import { MilestoneTimeline } from './MilestoneTimeline';
import { HealthInsightCard } from './HealthInsightCard';
import { TriggerInsightCard } from './TriggerInsightCard';
import { RecommendationCard } from './RecommendationCard';
import type { UserQuitPlan } from '../../types/plan';
import { ShieldCheck, RefreshCw } from 'lucide-react';

export interface PlanScreenProps {
  onOpenCravingModal: () => void;
  onOpenRelapseModal: () => void;
  onNavigateToChat?: (initialMessage?: string) => void;
}

export const PlanScreen = ({
  onOpenCravingModal,
  onOpenRelapseModal,
  onNavigateToChat,
}: PlanScreenProps) => {
  const { user } = useAuth();
  const { stats, smokingProfile } = useUserState();
  const userId = user?.id || 'guest_user';

  const [plan, setPlan] = useState<UserQuitPlan | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadPlan = async () => {
    setIsLoading(true);
    try {
      const quitDate = smokingProfile?.lastSmokedAt || Date.now();
      const dailyCount = smokingProfile?.dailyCigarettes || 15;
      const loaded = await planService.getPlan(userId, quitDate, dailyCount);
      setPlan(loaded);
    } catch (err) {
      console.error('[PlanScreen] Error loading plan:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadPlan();
  }, [userId, smokingProfile]);

  const handleToggleTask = async (taskId: string) => {
    const updated = await planService.toggleTaskStatus(userId, taskId);
    if (updated) {
      setPlan(updated);
    }
  };

  const healthInsights = planService.getHealthInsights(stats.smokeFreeDays);

  return (
    <div className="w-full h-full overflow-y-auto p-4 sm:p-6 font-arabic select-none bg-[#F7F9FC]" dir="rtl">
      <div className="max-w-3xl mx-auto flex flex-col gap-6 pb-12">
        {/* Header Title */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl sm:text-2xl font-black text-[#061A3A] tracking-tight">
              خطتك الشخصية للإقلاع
            </h1>
            <p className="text-xs sm:text-sm text-[#5F708C] mt-0.5">
              متابعة يومية دقيقة مبنية على إرشادات منظمة الصحة العالمية
            </p>
          </div>

          <button
            type="button"
            onClick={loadPlan}
            disabled={isLoading}
            aria-label="تحديث الخطة"
            className="p-2.5 rounded-xl bg-white border border-[#D9E2F0] text-[#5F708C] hover:text-[#061A3A] hover:bg-[#F4F7FB] transition-colors cursor-pointer disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-[#2D8BFF]' : ''}`} />
          </button>
        </div>

        {/* 1. Journey Hero (Where am I? & Start date) */}
        <PlanHero
          smokeFreeDays={stats.smokeFreeDays}
          smokeFreeHours={stats.smokeFreeHours}
          cigarettesAvoided={stats.cigarettesAvoided}
          moneySavedEGP={stats.moneySavedEGP}
          quitStartDate={smokingProfile?.lastSmokedAt || Date.now()}
          status={plan?.status || 'active'}
          onOpenCravingModal={onOpenCravingModal}
        />

        {/* 2. Next Action Card (What is the next step?) */}
        <NextActionCard
          title="تمرين التنفس وتجديد العزيمة"
          description="تمرين هادئ لمدة دقيقة يساعد على خفض التوتر واستقرار الجهاز العصبي."
          actionLabel="ابدأ التمرين الآن"
          actionType="breathing"
          onActionClick={onOpenCravingModal}
        />

        {/* 3. Daily Plan Tasks */}
        {plan && (
          <DailyPlanCard
            tasks={plan.tasks}
            onToggleTask={handleToggleTask}
          />
        )}

        {/* 4. Milestones Timeline */}
        {plan && (
          <MilestoneTimeline milestones={plan.milestones} />
        )}

        {/* 5. Trigger & Behavioral Insights */}
        <TriggerInsightCard
          primaryTriggers={smokingProfile?.primaryTriggers || ['التوتر', 'القهوة']}
          cravingsManagedCount={stats.cravingsManagedCount}
          onOpenRelapseModal={onOpenRelapseModal}
        />

        {/* 6. Health Physiological Insights (What is improving?) */}
        <HealthInsightCard insights={healthInsights} />

        {/* 7. Recommendation Card (Salem suggests...) */}
        <RecommendationCard
          title="التعامل مع محفزات القهوة والروتين الصباحي"
          rationale="إذا كانت القهوة مرتبطة بالسيجارة، فإن تغيير مكان الجلوس أو استبدالها بمشروب بديل لبضعة أيام يكسر هذا الرابط العصبي."
          actionLabel="استشر سالم عن كسر الروابط الشرطية"
          onActionClick={() => onNavigateToChat?.('عايز نصيحة لكسر الرابط بين القهوة والتدخين')}
        />

        {/* Clinical Footnote */}
        <div className="p-4 rounded-2xl bg-[#FFFFFF] border border-[#D9E2F0] flex items-center gap-3 text-xs text-[#5F708C]">
          <ShieldCheck className="w-5 h-5 text-[#34D399] shrink-0" />
          <span>
            جميع الحسابات والمراحل الإكلينيكية مستندة إلى إرشادات علاج الإقلاع عن التبغ الصادرة عن منظمة الصحة العالمية (WHO 2024).
          </span>
        </div>
      </div>
    </div>
  );
};
