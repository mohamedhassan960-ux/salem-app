import { useUserState } from '../../state/UserStateContext';
import { CheckCircle2, Circle, ListChecks } from 'lucide-react';

export const DailyTasksList = () => {
  const { dailyTasks, toggleTaskCompletion, stats } = useUserState();

  const getCategoryLabel = (category: string) => {
    switch (category) {
      case 'behavioral':
        return 'سلوكي';
      case 'mindfulness':
        return 'تنفس واسترخاء';
      case 'cognitive':
        return 'معرفي وتأجيل';
      case 'review':
        return 'مراجعة يومية';
      default:
        return 'إرشادي';
    }
  };

  return (
    <div className="bg-[#FFFFFF] border border-[#D9E2F0] rounded-3xl p-6 shadow-xs font-arabic flex flex-col gap-4" dir="rtl">
      <div className="flex items-center justify-between pb-3 border-b border-[#D9E2F0]">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-[#2D8BFF]/10 text-[#2D8BFF] flex items-center justify-center">
            <ListChecks className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-base font-bold text-[#061A3A]">مهام اليوم السلوكية</h3>
            <p className="text-xs text-[#5F708C]">خطوات صغيرة ومباشرة لتثبيت إنجازك اليومي</p>
          </div>
        </div>

        <span className="text-xs font-bold text-[#1E3A8A] bg-[#2D8BFF]/10 px-3 py-1 rounded-full border border-[#2D8BFF]/20">
          {stats.dailyTasksCompletedCount} / {stats.dailyTasksTotalCount} مكتمل
        </span>
      </div>

      <div className="flex flex-col gap-3">
        {dailyTasks.map((task) => (
          <div
            key={task.id}
            onClick={() => toggleTaskCompletion(task.id)}
            className={`
              p-4 rounded-2xl border transition-all duration-150 cursor-pointer flex items-start gap-3.5 select-none
              ${
                task.completed
                  ? 'bg-[#34D399]/5 border-[#34D399]/30 text-[#061A3A]'
                  : 'bg-[#F4F7FB] border-[#D9E2F0] hover:border-[#C4D1E3]'
              }
            `}
          >
            <button
              type="button"
              className="mt-0.5 shrink-0 text-[#2D8BFF] hover:scale-110 transition-transform cursor-pointer"
            >
              {task.completed ? (
                <CheckCircle2 className="w-5 h-5 text-[#34D399]" />
              ) : (
                <Circle className="w-5 h-5 text-[#8291A8]" />
              )}
            </button>

            <div className="flex-1 flex flex-col gap-1">
              <div className="flex items-center justify-between gap-2">
                <span
                  className={`text-sm font-bold ${
                    task.completed ? 'line-through text-[#5F708C]' : 'text-[#061A3A]'
                  }`}
                >
                  {task.title}
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#FFFFFF] border border-[#D9E2F0] text-[#5F708C] shrink-0">
                  {getCategoryLabel(task.category)}
                </span>
              </div>
              <p className="text-xs text-[#5F708C] leading-relaxed">{task.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
