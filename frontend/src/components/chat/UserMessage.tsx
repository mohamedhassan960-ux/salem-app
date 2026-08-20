import type { ChatMessage } from '../../types/chat';

export interface UserMessageProps {
  message: ChatMessage;
}

export const UserMessage = ({ message }: UserMessageProps) => {
  return (
    <div className="w-full flex justify-start my-2 animate-in fade-in slide-in-from-bottom-2 duration-200" dir="rtl">
      <div className="max-w-[85%] sm:max-w-[75%] rounded-2xl rounded-tr-sm bg-gradient-to-br from-sky-600 to-blue-700 text-white px-4 py-3 shadow-md shadow-sky-950/40 border border-sky-500/40">
        <p className="text-sm font-arabic font-medium leading-relaxed whitespace-pre-wrap">
          {message.content}
        </p>
      </div>
    </div>
  );
};
