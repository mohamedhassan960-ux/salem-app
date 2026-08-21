import { useState } from 'react';
import type { ConversationSession } from '../../types/chat';
import { MessageSquare, Plus, Trash2, Search, ChevronLeft } from 'lucide-react';

export interface HistoryScreenProps {
  conversations: ConversationSession[];
  activeConversationId: string | null;
  onSelectConversation: (c: ConversationSession) => void;
  onNewConversation: () => void;
  onDeleteConversation?: (id: string) => void;
}

export const HistoryScreen = ({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
}: HistoryScreenProps) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filtered = conversations.filter((c) =>
    c.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.messages.some((m) => m.content.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const groups = [
    { label: 'اليوم', items: filtered.filter((c) => c.group === 'اليوم') },
    { label: 'أمس', items: filtered.filter((c) => c.group === 'أمس') },
    { label: 'هذا الأسبوع', items: filtered.filter((c) => c.group === 'هذا الأسبوع') },
    { label: 'سابقًا', items: filtered.filter((c) => c.group === 'سابقًا') },
  ].filter((g) => g.items.length > 0);

  return (
    <div className="w-full h-full overflow-y-auto p-4 sm:p-6 font-arabic select-none bg-[#F7F9FC]" dir="rtl">
      <div className="max-w-3xl mx-auto flex flex-col gap-6 pb-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h1 className="text-xl sm:text-2xl font-black text-[#061A3A] tracking-tight">
              سجل المحادثات
            </h1>
            <p className="text-xs sm:text-sm text-[#5F708C] mt-0.5">
              محادثاتك واستشاراتك السابقة مع سالم للرجوع إليها في أي وقت
            </p>
          </div>

          <button
            type="button"
            onClick={onNewConversation}
            className="px-4 py-2.5 rounded-xl bg-[#2D8BFF] hover:bg-[#1E7AE6] active:bg-[#1569CC] text-white text-xs font-bold flex items-center justify-center gap-2 shadow-xs transition-all duration-150 active:scale-95 cursor-pointer self-start sm:self-auto"
          >
            <Plus className="w-4 h-4" />
            <span>محادثة جديدة</span>
          </button>
        </div>

        {/* Search Bar */}
        <div className="relative flex items-center">
          <div className="absolute right-3.5 flex items-center pointer-events-none text-[#8291A8]">
            <Search className="w-4 h-4" />
          </div>
          <input
            type="text"
            placeholder="البحث في المحادثات السابقة..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full h-11 pr-10 pl-4 bg-[#FFFFFF] border border-[#D9E2F0] rounded-2xl text-xs sm:text-sm text-[#061A3A] placeholder:text-[#8291A8] focus:border-[#2D8BFF] focus:ring-2 focus:ring-[#2D8BFF]/20 outline-none transition-all"
          />
        </div>

        {/* Conversation List */}
        {groups.length === 0 ? (
          <div className="p-8 rounded-3xl bg-[#FFFFFF] border border-[#D9E2F0] text-center flex flex-col items-center justify-center gap-3 text-[#8291A8]">
            <MessageSquare className="w-8 h-8 text-[#C4D1E3]" />
            <p className="text-sm font-semibold text-[#061A3A]">لا توجد محادثات مطابقة</p>
            <p className="text-xs text-[#5F708C]">ابدأ محادثة جديدة مع سالم لطرح أي استفسار.</p>
          </div>
        ) : (
          groups.map((group) => (
            <div key={group.label} className="flex flex-col gap-2">
              <span className="text-xs font-bold text-[#8291A8] px-1">{group.label}</span>
              <div className="flex flex-col gap-2">
                {group.items.map((conv) => {
                  const isActive = conv.id === activeConversationId;
                  const lastMessage = conv.messages[conv.messages.length - 1];

                  return (
                    <div
                      key={conv.id}
                      onClick={() => onSelectConversation(conv)}
                      className={`
                        p-4 rounded-2xl border transition-all duration-150 cursor-pointer flex items-center justify-between gap-3 shadow-xs
                        ${
                          isActive
                            ? 'bg-[#2D8BFF]/5 border-[#2D8BFF] ring-1 ring-[#2D8BFF]/20'
                            : 'bg-[#FFFFFF] border-[#D9E2F0] hover:border-[#C4D1E3] hover:bg-[#F4F7FB]'
                        }
                      `}
                    >
                      <div className="flex items-center gap-3 min-w-0">
                        <div
                          className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
                            isActive ? 'bg-[#2D8BFF]/15 text-[#2D8BFF]' : 'bg-[#F1F5FA] text-[#5F708C]'
                          }`}
                        >
                          <MessageSquare className="w-4 h-4" />
                        </div>
                        <div className="flex flex-col min-w-0">
                          <h4 className="text-sm font-bold text-[#061A3A] truncate">{conv.title}</h4>
                          <span className="text-xs text-[#5F708C] truncate mt-0.5">
                            {lastMessage ? lastMessage.content : 'محادثة فارغة'}
                          </span>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 shrink-0">
                        {onDeleteConversation && (
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              onDeleteConversation(conv.id);
                            }}
                            aria-label="حذف المحادثة"
                            className="w-8 h-8 flex items-center justify-center rounded-lg text-[#8291A8] hover:text-[#F87171] hover:bg-[#F87171]/10 transition-colors cursor-pointer"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                        <ChevronLeft className="w-4 h-4 text-[#8291A8]" />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
