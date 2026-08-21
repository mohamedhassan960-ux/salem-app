import type { PlanTask } from '../../types/plan';
import { Clock, Check, ListChecks } from 'lucide-react';

export interface DailyPlanCardProps {
  tasks: PlanTask[];
  onToggleTask: (taskId: string) => void;
}

export const DailyPlanCard = ({ tasks, onToggleTask }: DailyPlanCardProps) => {
  const completedCount = tasks.filter((t) => t.status === 'completed').length;

  return (
    <div className="bg-[#FFFFFF] border border-[#D9E2F0] rounded-3xl p-5 sm:p-6 shadow-xs flex flex-col gap-4 font-arabic select-none" dir="rtl">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-[#D9E2F0]">
        <div className="flex items-center gap-2">
          <ListChecks className="w-5 h-5 text-[#2D8BFF]" />
          <h3 className="text-base font-bold text-[#061A3A]">مهام اليوم السلوكية</h3>
        </div>

        <span className="text-xs font-bold text-[#5F708C] bg-[#F4F7FB] px-3 py-1 rounded-full border border-[#D9E2F0]">
          {completedCount} من {tasks.length} مكتملة
        </span>
      </div>

      {/* Task List */}
      <div className="flex flex-col gap-2.5">
        {tasks.map((task) => {
          const isCompleted = task.status === 'completed';
          return (
            <div
              key={task.id}
              onClick={() => onToggleTask(task.id)}
              className={`
                p-4 rounded-2xl border transition-all duration-150 cursor-pointer flex items-start gap-3.5
                ${
                  isCompleted
                    ? 'bg-[#34D399]/5 border-[#34D399]/30'
                    : 'bg-[#F4F7FB] border-[#D9E2F0] hover:border-[#C4D1E3]'
                }
              `}
            >
              <button
                type="button"
                className={`
                  w-6 h-6 rounded-lg flex items-center justify-center shrink-0 mt-0.5 transition-colors
                  ${
                    isCompleted
                      ? 'bg-[#34D399] text-white'
                      : 'border-2 border-[#8291A8] text-transparent hover:border-[#2D8BFF]'
                  }
                `}
                aria-label={isCompleted ? 'إلغاء إتمام المهمة' : 'تحديد المهمة كمكتملة'}
              >
                <Check className="w-4 h-4 stroke-[3]" />
              </button>

              <div className="flex flex-col min-w-0 flex-1">
                <div className="flex items-center justify-between gap-2">
                  <h4
                    className={`text-xs sm:text-sm font-bold transition-all ${
                      isCompleted ? 'line-through text-[#8291A8]' : 'text-[#061A3A]'
                    }`}
                  >
                    {task.title}
                  </h4>
                  {task.estimatedMinutes && (
                    <span className="text-[11px] text-[#8291A8] flex items-center gap-1 shrink-0">
                      <Clock className="w-3 h-3" />
                      <span>{task.estimatedMinutes} د</span>
                    </span>
                  )}
                </div>
                <p
                  className={`text-xs mt-1 leading-relaxed ${
                    isCompleted ? 'text-[#8291A8]' : 'text-[#5F708C]'
                  }`}
                >
                  {task.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
