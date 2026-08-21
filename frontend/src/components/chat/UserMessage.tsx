import type { ChatMessage } from '../../types/chat';

export interface UserMessageProps {
  message: ChatMessage;
}

export const UserMessage = ({ message }: UserMessageProps) => {
  return (
    <div className="w-full flex justify-start my-1.5 font-arabic" dir="rtl">
      <div
        className="
          max-w-[82%] sm:max-w-[75%] rounded-2xl rounded-tr-xs bg-[#1E3A8A] text-white p-3.5 sm:p-4
          shadow-xs text-sm leading-relaxed whitespace-pre-wrap break-words
        "
      >
        {message.content}
      </div>
    </div>
  );
};
