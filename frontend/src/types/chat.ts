export type MessageRole = 'user' | 'assistant';

export interface EvidenceSource {
  id: string;
  title: string;
  sourceDoc: string;
  section?: string;
  excerpt?: string;
  chunkId?: string;
  pageStart?: number;
}

export interface StructuredContent {
  paragraphs: string[];
  bulletPoints?: string[];
  keyTakeaway?: string;
  safetyNote?: string;
}

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  structured?: StructuredContent;
  evidence?: EvidenceSource[];
  contractState?: string;
  grounded?: boolean;
  safetyStatus?: string;
  latencyMs?: number;
  timestamp: number;
}

export interface ConversationSession {
  id: string;
  title: string;
  group: 'اليوم' | 'أمس' | 'هذا الأسبوع';
  createdAt: number;
  updatedAt: number;
  messages: ChatMessage[];
}

