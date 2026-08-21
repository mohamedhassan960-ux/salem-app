import { supabase, isSupabaseConfigured } from './supabaseClient';
import type { ConversationSession, ChatMessage } from '../types/chat';

const LOCAL_CONVERSATIONS_KEY = 'salem_conversations_v3';

export const conversationService = {
  /**
   * Loads all conversation sessions for the user.
   */
  async getConversations(userId: string): Promise<ConversationSession[]> {
    // 1. Try Supabase if configured
    if (isSupabaseConfigured && supabase && userId !== 'guest_user') {
      try {
        const { data: convData, error: convError } = await supabase
          .from('conversations')
          .select('*')
          .eq('user_id', userId)
          .order('updated_at', { ascending: false });

        const client = supabase;
        if (!convError && convData && convData.length > 0 && client) {
          const sessions: ConversationSession[] = await Promise.all(
            convData.map(async (row) => {
              const { data: msgData } = await client
                .from('messages')
                .select('*')
                .eq('conversation_id', row.id)
                .order('created_at', { ascending: true });

              const messages: ChatMessage[] = (msgData || []).map((m) => ({
                id: m.id,
                role: m.role as 'user' | 'assistant',
                content: m.content,
                evidence: m.evidence || undefined,
                contractState: m.contract_state || undefined,
                grounded: Boolean(m.grounded),
                safetyStatus: m.safety_status || undefined,
                timestamp: new Date(m.created_at).getTime(),
              }));

              const createdAt = new Date(row.created_at).getTime();
              const diffDays = (Date.now() - createdAt) / (1000 * 60 * 60 * 24);
              const group: ConversationSession['group'] =
                diffDays < 1 ? 'اليوم' : diffDays < 2 ? 'أمس' : diffDays < 7 ? 'هذا الأسبوع' : 'سابقًا';

              return {
                id: row.id,
                title: row.title || 'محادثة مع سالم',
                group,
                createdAt,
                updatedAt: new Date(row.updated_at).getTime(),
                messages,
              };
            })
          );

          localStorage.setItem(LOCAL_CONVERSATIONS_KEY, JSON.stringify(sessions));
          return sessions;
        }
      } catch (err) {
        console.warn('[conversationService] Supabase load error, falling back to local:', err);
      }
    }

    // 2. Fallback to LocalStorage
    try {
      const saved = localStorage.getItem(LOCAL_CONVERSATIONS_KEY);
      if (saved) {
        return JSON.parse(saved);
      }
    } catch {
      // ignore
    }

    return [];
  },

  /**
   * Saves or updates a conversation session.
   */
  async saveConversation(userId: string, session: ConversationSession): Promise<void> {
    // 1. Always update local storage
    try {
      const saved = localStorage.getItem(LOCAL_CONVERSATIONS_KEY);
      const existing: ConversationSession[] = saved ? JSON.parse(saved) : [];
      const idx = existing.findIndex((c) => c.id === session.id);
      let updated: ConversationSession[];
      if (idx >= 0) {
        updated = existing.map((c) => (c.id === session.id ? session : c));
      } else {
        updated = [session, ...existing];
      }
      localStorage.setItem(LOCAL_CONVERSATIONS_KEY, JSON.stringify(updated));
    } catch {
      // ignore
    }

    // 2. Upsert to Supabase if configured
    if (isSupabaseConfigured && supabase && userId !== 'guest_user') {
      try {
        await supabase.from('conversations').upsert({
          id: session.id,
          user_id: userId,
          title: session.title,
          updated_at: new Date(session.updatedAt).toISOString(),
        });
      } catch (err) {
        console.error('[conversationService] Error saving conversation to Supabase:', err);
      }
    }
  },

  /**
   * Persists a message to a conversation.
   */
  async saveMessage(userId: string, conversationId: string, message: ChatMessage): Promise<void> {
    if (isSupabaseConfigured && supabase && userId !== 'guest_user') {
      try {
        await supabase.from('messages').upsert({
          id: message.id,
          conversation_id: conversationId,
          role: message.role,
          content: message.content,
          evidence: message.evidence || null,
          contract_state: message.contractState || null,
          grounded: message.grounded || false,
          safety_status: message.safetyStatus || null,
          created_at: new Date(message.timestamp).toISOString(),
        });
      } catch (err) {
        console.error('[conversationService] Error saving message to Supabase:', err);
      }
    }
  },

  /**
   * Deletes a conversation session.
   */
  async deleteConversation(userId: string, conversationId: string): Promise<void> {
    try {
      const saved = localStorage.getItem(LOCAL_CONVERSATIONS_KEY);
      if (saved) {
        const list: ConversationSession[] = JSON.parse(saved);
        const filtered = list.filter((c) => c.id !== conversationId);
        localStorage.setItem(LOCAL_CONVERSATIONS_KEY, JSON.stringify(filtered));
      }
    } catch {
      // ignore
    }

    if (isSupabaseConfigured && supabase && userId !== 'guest_user') {
      try {
        await supabase.from('messages').delete().eq('conversation_id', conversationId);
        await supabase.from('conversations').delete().eq('id', conversationId);
      } catch (err) {
        console.error('[conversationService] Error deleting conversation from Supabase:', err);
      }
    }
  },
};
