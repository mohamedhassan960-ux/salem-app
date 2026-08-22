export type MessageRole = 'user' | 'assistant';

export interface EvidenceSource {
  id: string;
  title: string;
  sectionTitle?: string;
  organization: string; // e.g. "منظمة الصحة العالمية (WHO)"
  year: string;         // e.g. "2024"
  sourceType: string;   // e.g. "دليل إكلينيكي معتمد"
  section?: string;
  whyRelevant?: string;
  excerpt?: string;
  pageStart?: number;
  pageEnd?: number;
  externalUrl?: string;
  originalText?: string;
  highlightText?: string;
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
  group: 'اليوم' | 'أمس' | 'هذا الأسبوع' | 'سابقًا';
  createdAt: number;
  updatedAt: number;
  messages: ChatMessage[];
}
