import { InterventionProgress } from './InterventionProgress';
import { InterventionTimer } from './InterventionTimer';
import { BreathingExercise } from './BreathingExercise';
import { Button } from '../ui/Button';
import type { InterventionStep } from '../../types/intervention';
import { GlassWater, Check } from 'lucide-react';

export interface InterventionCardProps {
  step: InterventionStep;
  onStepComplete: () => void;
  onSkip?: () => void;
}

export const InterventionCard = ({
  step,
  onStepComplete,
  onSkip,
}: InterventionCardProps) => {
  return (
    <div className="bg-[#FFFFFF] border border-[#D9E2F0] rounded-3xl p-5 sm:p-6 shadow-sm flex flex-col gap-5 font-arabic select-none" dir="rtl">
      {/* Top Step Progress Bar */}
      <div className="flex items-center justify-between pb-3 border-b border-[#D9E2F0]">
        <InterventionProgress currentStep={step.stepNumber} totalSteps={step.totalSteps} />
        <span className="text-[11px] font-semibold text-[#1E3A8A] bg-[#2D8BFF]/10 px-2.5 py-0.5 rounded-full border border-[#2D8BFF]/20">
          تدخل سلوكي
        </span>
      </div>

      {/* Action Content Dispatcher */}
      {step.actionType === 'timer' && (
        <InterventionTimer
          totalSeconds={step.durationSeconds || 60}
          label={step.title}
          supportingText={step.explanation}
          onComplete={onStepComplete}
        />
      )}

      {step.actionType === 'breathing_478' && (
        <div className="flex flex-col gap-3">
          <div className="flex flex-col gap-1">
            <h4 className="text-base font-bold text-[#061A3A]">{step.title}</h4>
            <p className="text-xs text-[#5F708C] leading-relaxed">{step.explanation}</p>
          </div>
          <BreathingExercise onComplete={onStepComplete} />
        </div>
      )}

      {step.actionType === 'water_walk' && (
        <div className="flex flex-col items-center text-center gap-5 py-3">
          <div className="w-16 h-16 rounded-3xl bg-[#2D8BFF]/10 text-[#2D8BFF] flex items-center justify-center">
            <GlassWater className="w-8 h-8" />
          </div>

          <div className="flex flex-col gap-1.5 max-w-sm">
            <h4 className="text-base font-bold text-[#061A3A]">{step.title}</h4>
            <p className="text-xs text-[#5F708C] leading-relaxed">{step.explanation}</p>
          </div>

          <Button
            variant="primary"
            size="lg"
            fullWidth
            onClick={onStepComplete}
            leftIcon={<Check className="w-4 h-4" />}
          >
            {step.primaryActionLabel}
          </Button>
        </div>
      )}

      {/* Skip button if allowed */}
      {step.allowSkip && onSkip && step.actionType !== 'water_walk' && (
        <div className="flex justify-center pt-1">
          <button
            type="button"
            onClick={onSkip}
            className="text-xs font-semibold text-[#5F708C] hover:text-[#061A3A] transition-colors cursor-pointer"
          >
            {step.secondaryActionLabel || 'تخطي للخطوة التالية'}
          </button>
        </div>
      )}
    </div>
  );
};
