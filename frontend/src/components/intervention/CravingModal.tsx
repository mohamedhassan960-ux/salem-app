import { useState, useEffect } from 'react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { IntensitySelector } from './IntensitySelector';
import { InterventionCard } from './InterventionCard';
import { InterventionCheckIn } from './InterventionCheckIn';
import { InterventionCompletion } from './InterventionCompletion';
import { interventionService } from '../../services/interventionService';
import { useUserState } from '../../state/UserStateContext';
import { useAuth } from '../../context/AuthContext';
import type { InterventionSession } from '../../types/intervention';
import { Check } from 'lucide-react';

export interface CravingModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type ModalView = 'setup' | 'step' | 'check_in' | 'completion';

export const CravingModal = ({ isOpen, onClose }: CravingModalProps) => {
  const { user } = useAuth();
  const { completeCraving } = useUserState();
  const userId = user?.id || 'guest_user';

  const [view, setView] = useState<ModalView>('setup');
  const [session, setSession] = useState<InterventionSession | null>(null);
  const [intensityBefore, setIntensityBefore] = useState<number>(7);
  const [selectedTrigger, setSelectedTrigger] = useState<string>('التوتر وضغط العمل');

  // Check for any active in-progress session on mount/open
  useEffect(() => {
    if (isOpen) {
      const active = interventionService.getActiveSession(userId);
      if (active) {
        setSession(active);
        setView('step');
      } else {
        setView('setup');
      }
    }
  }, [isOpen, userId]);

  const triggers = [
    'التوتر وضغط العمل',
    'بعد شرب القهوة',
    'بعد تناول وجبة',
    'الملل أو الفراغ',
    'رؤية شخص يدخن',
    'سبب آخر',
  ];

  const handleStartSession = () => {
    const newSession = interventionService.createCravingSession(
      userId,
      selectedTrigger,
      intensityBefore
    );
    setSession(newSession);
    setView('step');
  };

  const handleStepComplete = () => {
    if (!session) return;
    const nextIndex = session.currentStepIndex + 1;
    if (nextIndex < session.steps.length) {
      const updated: InterventionSession = {
        ...session,
        currentStepIndex: nextIndex,
      };
      setSession(updated);
      interventionService.saveActiveSession(updated);
    } else {
      setView('check_in');
    }
  };

  const handleCheckInSubmit = async (intensityAfter: number, outcome: 'lower' | 'same' | 'higher') => {
    if (!session) return;
    const completed = await interventionService.completeSession(session, intensityAfter, outcome);
    setSession(completed);
    // Update global state store
    completeCraving(completed.id, intensityAfter);
    setView('completion');
  };

  const handleClose = () => {
    if (session && view !== 'completion' && view !== 'setup') {
      // User is exiting early — preserve session in storage
      interventionService.saveActiveSession(session);
    }
    setView('setup');
    setSession(null);
    onClose();
  };

  const currentStep = session ? session.steps[session.currentStepIndex] : null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title={
        view === 'completion'
          ? 'إنجاز رائع!'
          : view === 'check_in'
          ? 'تقييم شدة الرغبة'
          : 'التعامل مع الرغبة الملحة'
      }
      subtitle={
        view === 'completion'
          ? 'كل نوبة تتجاوزها تقربك من التحرر الكامل'
          : 'خطوات بسيطة وفعالة لتجاوز لحظة الرغبة خطوة بخطوة'
      }
      maxWidth="md"
    >
      <div className="flex flex-col gap-4 font-arabic" dir="rtl">
        {/* ── View 1: Setup (Recognize Intensity & Trigger) ── */}
        {view === 'setup' && (
          <div className="flex flex-col gap-5 py-2">
            <IntensitySelector
              value={intensityBefore}
              onChange={setIntensityBefore}
              label="ما هي شدة الرغبة التي تشعر بها الآن؟"
            />

            <div className="flex flex-col gap-2">
              <label className="text-xs font-bold text-[#061A3A]">إيه اللي حفز الرغبة دي؟</label>
              <div className="grid grid-cols-2 gap-2">
                {triggers.map((trig) => (
                  <button
                    key={trig}
                    type="button"
                    onClick={() => setSelectedTrigger(trig)}
                    className={`
                      min-h-[44px] p-3 rounded-2xl border text-right text-xs transition-all duration-150 cursor-pointer flex items-center justify-between
                      ${
                        selectedTrigger === trig
                          ? 'border-[#2D8BFF] bg-[#2D8BFF]/5 font-bold text-[#1E3A8A] ring-1 ring-[#2D8BFF]/30'
                          : 'border-[#D9E2F0] bg-[#F4F7FB] text-[#061A3A] hover:border-[#C4D1E3]'
                      }
                    `}
                  >
                    <span>{trig}</span>
                    {selectedTrigger === trig && <Check className="w-3.5 h-3.5 text-[#2D8BFF]" />}
                  </button>
                ))}
              </div>
            </div>

            <div className="pt-2">
              <Button
                variant="primary"
                size="lg"
                fullWidth
                onClick={handleStartSession}
              >
                ابدأ التعامل مع الرغبة
              </Button>
            </div>
          </div>
        )}

        {/* ── View 2: Step-by-Step Intervention Execution ── */}
        {view === 'step' && currentStep && (
          <InterventionCard
            step={currentStep}
            onStepComplete={handleStepComplete}
            onSkip={handleStepComplete}
          />
        )}

        {/* ── View 3: Check-In ── */}
        {view === 'check_in' && (
          <InterventionCheckIn
            intensityBefore={session?.intensityBefore || intensityBefore}
            onSubmit={handleCheckInSubmit}
          />
        )}

        {/* ── View 4: Completion ── */}
        {view === 'completion' && session && (
          <InterventionCompletion
            intensityBefore={session.intensityBefore || intensityBefore}
            intensityAfter={session.intensityAfter || 2}
            onFinish={handleClose}
          />
        )}
      </div>
    </Modal>
  );
};
