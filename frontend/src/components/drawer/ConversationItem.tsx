import type { ConversationSession } from '../../types/chat';
import { MessageSquare } from 'lucide-react';

export interface ConversationItemProps {
  conversation: ConversationSession;
  isActive: boolean;
  onClick: (conversation: ConversationSession) => void;
}

export const ConversationItem = ({
  conversation,
  isActive,
  onClick,
}: ConversationItemProps) => {
  return (
    <button
      type="button"
      onClick={() => onClick(conversation)}
      className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-right transition-all duration-200 cursor-pointer active:scale-[0.99] group ${
        isActive
          ? 'bg-sky-500/15 border border-sky-500/40 text-white font-semibold'
          : 'hover:bg-slate-800/70 active:bg-slate-800 text-slate-300 hover:text-white border border-transparent'
      }`}
      dir="rtl"
    >
      <MessageSquare
        className={`w-4 h-4 shrink-0 transition-colors ${
          isActive ? 'text-sky-400' : 'text-slate-400 group-hover:text-slate-300'
        }`}
      />
      <span className="text-xs font-arabic truncate flex-1">
        {conversation.title}
      </span>
    </button>
  );
};
