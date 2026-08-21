import { MessageSquare, Plus } from 'lucide-react';
import { Button } from '../ui/Button';

export interface HistoryEmptyStateProps {
  onNewConversation: () => void;
}

export const HistoryEmptyState = ({ onNewConversation }: HistoryEmptyStateProps) => {
  return (
    <div className="bg-[#FFFFFF] border border-[#D9E2F0] rounded-3xl p-8 sm:p-12 text-center flex flex-col items-center justify-center gap-4 font-arabic select-none shadow-xs" dir="rtl">
      <div className="w-16 h-16 rounded-3xl bg-[#2D8BFF]/10 text-[#2D8BFF] flex items-center justify-center">
        <MessageSquare className="w-8 h-8" />
      </div>

      <div className="flex flex-col gap-1 max-w-sm">
        <h3 className="text-base sm:text-lg font-extrabold text-[#061A3A]">
          لسه مفيش محادثات محفوظة.
        </h3>
        <p className="text-xs text-[#5F708C] leading-relaxed">
          تقدر تبدأ أول محادثة مع سالم دلوقتي وتستشيره في أي وقت بدون أي تردد.
        </p>
      </div>

      <div className="pt-2">
        <Button
          variant="primary"
          size="md"
          onClick={onNewConversation}
          leftIcon={<Plus className="w-4 h-4" />}
        >
          ابدأ محادثة جديدة
        </Button>
      </div>
    </div>
  );
};
