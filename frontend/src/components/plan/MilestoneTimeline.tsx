import type { Milestone } from '../../types/plan';
import { Award, CheckCircle2, Circle, ShieldCheck } from 'lucide-react';

export interface MilestoneTimelineProps {
  milestones: Milestone[];
}

export const MilestoneTimeline = ({ milestones }: MilestoneTimelineProps) => {
  return (
    <div className="bg-[#FFFFFF] border border-[#D9E2F0] rounded-3xl p-5 sm:p-6 shadow-xs flex flex-col gap-4 font-arabic select-none" dir="rtl">
      <div className="flex items-center gap-2 pb-3 border-b border-[#D9E2F0]">
        <Award className="w-5 h-5 text-[#2D8BFF]" />
        <h3 className="text-base font-bold text-[#061A3A]">محطات الرحلة الإكلينيكية</h3>
      </div>

      <div className="relative flex flex-col gap-5 pr-2 pt-2">
        {/* Continuous Timeline Track */}
        <div className="absolute top-4 bottom-4 right-5 w-0.5 bg-[#D9E2F0]" />

        {milestones.map((m) => (
          <div key={m.id} className="relative flex items-start gap-4 z-10">
            {/* Pip Status */}
            <div
              className={`
                w-6 h-6 rounded-full flex items-center justify-center shrink-0 border-2 bg-white transition-colors
                ${
                  m.achieved
                    ? 'border-[#34D399] text-[#34D399] ring-4 ring-[#34D399]/10'
                    : 'border-[#8291A8] text-[#8291A8]'
                }
              `}
            >
              {m.achieved ? (
                <CheckCircle2 className="w-4 h-4 fill-[#34D399] text-white" />
              ) : (
                <Circle className="w-2.5 h-2.5 fill-current" />
              )}
            </div>

            <div className="flex flex-col flex-1 p-4 rounded-2xl bg-[#F4F7FB] border border-[#D9E2F0]">
              <div className="flex items-center justify-between">
                <h4 className="text-xs sm:text-sm font-bold text-[#061A3A]">{m.title}</h4>
                {m.achieved && (
                  <span className="text-[10px] font-bold text-[#047857] bg-[#34D399]/15 px-2.5 py-0.5 rounded-full border border-[#34D399]/30">
                    تم الإنجاز
                  </span>
                )}
              </div>
              <p className="text-xs text-[#5F708C] mt-1 leading-relaxed">{m.description}</p>
              {m.clinicalNote && (
                <div className="mt-2.5 pt-2 border-t border-[#D9E2F0]/60 flex items-start gap-1.5 text-[11px] text-[#1E3A8A]">
                  <ShieldCheck className="w-3.5 h-3.5 shrink-0 text-[#2D8BFF] mt-0.5" />
                  <span>{m.clinicalNote}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
