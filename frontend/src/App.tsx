import { useState, useEffect, useMemo, useCallback } from 'react';
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

const INITIAL_CONVERSATIONS: ConversationSession[] = [];

export function App() {
  const { authStep, setAuthStep, signOut } = useAuth();
  const { activeIntervention, setActiveIntervention } = useUserState();

  const [currentTab, setCurrentTab] = useState<Tab>('chat');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isLogoutDialogOpen, setIsLogoutDialogOpen] = useState(false);

  // Conversations State
  const [conversations, setConversations] = useState<ConversationSession[]>(() => {
    try {
      const saved = localStorage.getItem('salem_conversations_v3');
      if (saved) return JSON.parse(saved);
    } catch {
      // ignore
    }
    return INITIAL_CONVERSATIONS;
  });

  // Always start with a stable, persistent chat session ID
  const [activeConversationId, setActiveConversationId] = useState<string>(() => `conv_${Date.now()}`);

  useEffect(() => {
    try {
      localStorage.setItem('salem_conversations_v3', JSON.stringify(conversations));
    } catch {
      // ignore
    }
  }, [conversations]);

  // Reset to fresh clean chat if user leaves app idle for > 30 minutes
  useEffect(() => {
    let lastActive = Date.now();
    const updateActivity = () => {
      lastActive = Date.now();
    };

    const checkInactivity = () => {
      const now = Date.now();
      if (now - lastActive > 30 * 60 * 1000) {
        setActiveConversationId(`conv_${now}`);
      }
      lastActive = now;
    };

    window.addEventListener('focus', checkInactivity);
    window.addEventListener('pointerdown', updateActivity, { passive: true });
    window.addEventListener('keydown', updateActivity, { passive: true });
    window.addEventListener('touchstart', updateActivity, { passive: true });

    const onVisibility = () => {
      if (document.visibilityState === 'visible') {
        checkInactivity();
      }
    };
    document.addEventListener('visibilitychange', onVisibility);

    return () => {
      window.removeEventListener('focus', checkInactivity);
      window.removeEventListener('pointerdown', updateActivity);
      window.removeEventListener('keydown', updateActivity);
      window.removeEventListener('touchstart', updateActivity);
      document.removeEventListener('visibilitychange', onVisibility);
    };
  }, []);

  const activeConversation: ConversationSession = useMemo(() => {
    const found = conversations.find((c) => c.id === activeConversationId);
    if (found) return found;
    return {
      id: activeConversationId,
      title: 'محادثة جديدة',
      group: 'اليوم',
      createdAt: Date.now(),
      updatedAt: Date.now(),
      messages: [],
    };
  }, [conversations, activeConversationId]);

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
      setActiveConversationId(`conv_${Date.now()}`);
    }
  };

  const handleUpdateMessages = useCallback((msgs: ChatMessage[]) => {
    setActiveConversationId((currentActiveId) => {
      const currentId = currentActiveId || `conv_${Date.now()}`;
      const firstUserMsg = msgs.find((m) => m.role === 'user');
      const autoTitle = firstUserMsg ? firstUserMsg.content.slice(0, 30) + '...' : 'محادثة مع سالم';

      setConversations((prev) => {
        const idx = prev.findIndex((c) => c.id === currentId);
        if (idx >= 0) {
          return prev.map((c, i) =>
            i === idx
              ? {
                  ...c,
                  title:
                    (c.title === 'استشارة جديدة' || c.title === 'محادثة جديدة') && firstUserMsg
                      ? autoTitle
                      : c.title,
                  updatedAt: Date.now(),
                  messages: msgs,
                }
              : c
          );
        } else {
          const newConv: ConversationSession = {
            id: currentId,
            title: autoTitle,
            group: 'اليوم',
            createdAt: Date.now(),
            updatedAt: Date.now(),
            messages: msgs,
          };
          return [newConv, ...prev];
        }
      });

      return currentId;
    });
  }, []);

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
            key={activeConversation.id}
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
