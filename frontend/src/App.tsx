import { useState, useEffect } from 'react';
import { useAuth } from './context/AuthContext';
import { useUserState } from './state/UserStateContext';
import { SplashScreen } from './components/entry/SplashScreen';
import { LoginScreen } from './components/entry/LoginScreen';
import { SignupScreen } from './components/entry/SignupScreen';
import { ForgotPasswordScreen } from './components/entry/ForgotPasswordScreen';
import { EmailConfirmationScreen } from './components/entry/EmailConfirmationScreen';
import { OnboardingScreen } from './components/entry/OnboardingScreen';

import { AppShell } from './components/layout/AppShell';
import { ChatScreen } from './components/chat/ChatScreen';
import { PlanScreen } from './components/plan/PlanScreen';
import { HistoryScreen } from './components/history/HistoryScreen';
import { ProfileScreen } from './components/profile/ProfileScreen';
import { SettingsScreen } from './components/settings/SettingsScreen';
import { MarketingPage } from './components/marketing/MarketingPage';

import { CravingModal } from './components/intervention/CravingModal';
import { RelapseModal } from './components/intervention/RelapseModal';
import { LogoutDialog } from './components/drawer/LogoutDialog';
import { NetworkBanner } from './components/pwa/NetworkBanner';

import type { ConversationSession, ChatMessage } from './types/chat';

type Tab = 'chat' | 'plan' | 'history' | 'profile' | 'settings' | 'marketing';

const INITIAL_CONVERSATIONS: ConversationSession[] = [
  {
    id: 'conv_1',
    title: 'كيفية البدء في خطة الإقلاع',
    group: 'اليوم',
    createdAt: Date.now() - 3600000,
    updatedAt: Date.now() - 3600000,
    messages: [
      {
        id: 'm1',
        role: 'user',
        content: 'عايز أبدأ خطة إقلاع تدريجية بدون توتر كبير.',
        timestamp: Date.now() - 3600000,
      },
      {
        id: 'm2',
        role: 'assistant',
        content: 'أهلاً بيك يا بطل! التوقف مع تحديد هدف واضح خطوة بخطوة من أنجح الطرق المعتمدة في دليل منظمة الصحة العالمية (WHO 2024). خلينا نحدد أهم المحفزات اللي بتواجهك ونبدأ خطوة صغيرة اليوم.',
        timestamp: Date.now() - 3500000,
      },
    ],
  },
  {
    id: 'conv_2',
    title: 'التعامل مع أعراض الانسحاب والصداع',
    group: 'اليوم',
    createdAt: Date.now() - 7200000,
    updatedAt: Date.now() - 7200000,
    messages: [],
  },
  {
    id: 'conv_3',
    title: 'بدائل النيكوتين (NRT) واللصقات',
    group: 'أمس',
    createdAt: Date.now() - 86400000,
    updatedAt: Date.now() - 86400000,
    messages: [],
  },
];

export function App() {
  const { authStep, setAuthStep, signOut } = useAuth();
  const { activeIntervention, setActiveIntervention } = useUserState();

  const [currentTab, setCurrentTab] = useState<Tab>('chat');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isLogoutDialogOpen, setIsLogoutDialogOpen] = useState(false);

  // Conversations State
  const [conversations, setConversations] = useState<ConversationSession[]>(() => {
    try {
      const saved = localStorage.getItem('salem_conversations_v2');
      if (saved) return JSON.parse(saved);
    } catch {
      // ignore
    }
    return INITIAL_CONVERSATIONS;
  });

  const [activeConversationId, setActiveConversationId] = useState<string | null>('conv_1');

  useEffect(() => {
    try {
      localStorage.setItem('salem_conversations_v2', JSON.stringify(conversations));
    } catch {
      // ignore
    }
  }, [conversations]);

  const activeConversation = conversations.find((c) => c.id === activeConversationId) || null;

  // Handlers
  const handleSelectConversation = (conv: ConversationSession) => {
    setActiveConversationId(conv.id);
    setCurrentTab('chat');
    setIsSidebarOpen(false);
  };

  const handleNewConversation = () => {
    const newId = `conv_${Date.now()}`;
    const newConv: ConversationSession = {
      id: newId,
      title: 'استشارة جديدة',
      group: 'اليوم',
      createdAt: Date.now(),
      updatedAt: Date.now(),
      messages: [],
    };
    setConversations((prev) => [newConv, ...prev]);
    setActiveConversationId(newId);
    setCurrentTab('chat');
    setIsSidebarOpen(false);
  };

  const handleDeleteConversation = (id: string) => {
    setConversations((prev) => prev.filter((c) => c.id !== id));
    if (activeConversationId === id) {
      setActiveConversationId(null);
    }
  };

  const handleUpdateMessages = (msgs: ChatMessage[]) => {
    if (!activeConversationId) {
      // Create new conversation automatically on first message
      const newId = `conv_${Date.now()}`;
      const firstUserMsg = msgs.find((m) => m.role === 'user');
      const title = firstUserMsg ? firstUserMsg.content.slice(0, 30) + '...' : 'محادثة مع سالم';
      const newConv: ConversationSession = {
        id: newId,
        title,
        group: 'اليوم',
        createdAt: Date.now(),
        updatedAt: Date.now(),
        messages: msgs,
      };
      setConversations((prev) => [newConv, ...prev]);
      setActiveConversationId(newId);
      return;
    }

    setConversations((prev) =>
      prev.map((c) => {
        if (c.id === activeConversationId) {
          const firstUserMsg = msgs.find((m) => m.role === 'user');
          const title =
            c.title === 'استشارة جديدة' && firstUserMsg
              ? firstUserMsg.content.slice(0, 30) + '...'
              : c.title;

          return {
            ...c,
            title,
            updatedAt: Date.now(),
            messages: msgs,
          };
        }
        return c;
      })
    );
  };

  const handleConfirmLogout = async () => {
    setIsLogoutDialogOpen(false);
    await signOut();
  };

  // ── 1. Full-Screen Entry Flows ──
  if (authStep === 'splash') {
    return <SplashScreen />;
  }
  if (authStep === 'login') {
    return <LoginScreen />;
  }
  if (authStep === 'signup') {
    return <SignupScreen />;
  }
  if (authStep === 'forgot_password') {
    return <ForgotPasswordScreen />;
  }
  if (authStep === 'email_confirmation') {
    return <EmailConfirmationScreen />;
  }
  if (authStep === 'onboarding') {
    return <OnboardingScreen onComplete={() => setAuthStep('chat_ready')} />;
  }

  // ── 2. Marketing Page Preview Mode ──
  if (currentTab === 'marketing') {
    return (
      <MarketingPage onStartApp={() => setCurrentTab('chat')} />
    );
  }

  // ── 3. Authenticated App Experience ──
  return (
    <>
      <AppShell
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        isSidebarOpen={isSidebarOpen}
        onSidebarToggle={() => setIsSidebarOpen((prev) => !prev)}
        onSidebarClose={() => setIsSidebarOpen(false)}
        onNewConversation={handleNewConversation}
        onOpenLogout={() => setIsLogoutDialogOpen(true)}
        onOpenCravingModal={() => setActiveIntervention('craving')}
      >
        {currentTab === 'chat' && (
          <ChatScreen
            activeConversation={activeConversation}
            onOpenCravingModal={() => setActiveIntervention('craving')}
            onOpenRelapseModal={() => setActiveIntervention('relapse')}
            onUpdateConversationMessages={handleUpdateMessages}
          />
        )}

        {currentTab === 'plan' && (
          <PlanScreen
            onOpenCravingModal={() => setActiveIntervention('craving')}
            onOpenRelapseModal={() => setActiveIntervention('relapse')}
          />
        )}

        {currentTab === 'history' && (
          <HistoryScreen
            conversations={conversations}
            activeConversationId={activeConversationId}
            onSelectConversation={handleSelectConversation}
            onNewConversation={handleNewConversation}
            onDeleteConversation={handleDeleteConversation}
          />
        )}

        {currentTab === 'profile' && (
          <ProfileScreen onOpenSettings={() => setCurrentTab('settings')} />
        )}

        {currentTab === 'settings' && (
          <SettingsScreen
            onBack={() => setCurrentTab('chat')}
            onOpenLogoutDialog={() => setIsLogoutDialogOpen(true)}
          />
        )}
      </AppShell>

      {/* Global Craving Intervention Modal */}
      <CravingModal
        isOpen={activeIntervention === 'craving'}
        onClose={() => setActiveIntervention(null)}
      />

      {/* Global Relapse Management Modal */}
      <RelapseModal
        isOpen={activeIntervention === 'relapse'}
        onClose={() => setActiveIntervention(null)}
      />

      {/* Logout Confirmation Dialog */}
      <LogoutDialog
        isOpen={isLogoutDialogOpen}
        onConfirm={handleConfirmLogout}
        onCancel={() => setIsLogoutDialogOpen(false)}
      />

      {/* PWA Network Banner */}
      <NetworkBanner />
    </>
  );
}

export default App;
