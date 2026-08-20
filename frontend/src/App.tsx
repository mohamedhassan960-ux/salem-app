import { useState, useEffect } from 'react';
import { useAuth } from './context/AuthContext';
import { SplashScreen } from './components/entry/SplashScreen';
import { OnboardingScreen } from './components/entry/OnboardingScreen';
import { LoginScreen } from './components/entry/LoginScreen';
import { AppShell } from './components/layout/AppShell';
import { ChatScreen } from './components/chat/ChatScreen';
import { SidebarDrawer } from './components/drawer/SidebarDrawer';
import { LogoutDialog } from './components/drawer/LogoutDialog';
import { SettingsScreen } from './components/settings/SettingsScreen';
import { NetworkBanner } from './components/pwa/NetworkBanner';
import { InstallPromptModal } from './components/pwa/InstallPromptModal';
import type { EntryStep } from './types/auth';
import type { ConversationSession } from './types/chat';

export function App() {
  const { user, hasSeenOnboarding, markOnboardingComplete, signOut } = useAuth();
  const [currentStep, setCurrentStep] = useState<EntryStep>('splash');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isLogoutDialogOpen, setIsLogoutDialogOpen] = useState(false);

  // Lock body scroll when sidebar is open
  useEffect(() => {
    if (isSidebarOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => { document.body.style.overflow = ''; };
  }, [isSidebarOpen]);

  const [conversations] = useState<ConversationSession[]>([
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
          content: 'أهلاً بيك! التوقف التدريجي مع وضع تاريخ محدد للهدف (Quit Date) من أنجح الطرق المعتمدة في دليل WHO 2024.',
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
      messages: [
        {
          id: 'm3',
          role: 'user',
          content: 'الصداع والعصبية بيزيدوا معايا بالليل، إيه الحل؟',
          timestamp: Date.now() - 7200000,
        },
      ],
    },
    {
      id: 'conv_3',
      title: 'بدائل النيكوتين (NRT) واللصقات',
      group: 'أمس',
      createdAt: Date.now() - 86400000,
      updatedAt: Date.now() - 86400000,
      messages: [],
    },
    {
      id: 'conv_4',
      title: 'خطة التوقف التدريجي خلال أسبوعين',
      group: 'هذا الأسبوع',
      createdAt: Date.now() - 259200000,
      updatedAt: Date.now() - 259200000,
      messages: [],
    },
  ]);

  const [activeConversationId, setActiveConversationId] = useState<string | null>('conv_1');
  const activeConversation = conversations.find((c) => c.id === activeConversationId) || null;

  const handleSplashComplete = () => {
    if (user) {
      setCurrentStep('chat_ready');
    } else if (!hasSeenOnboarding) {
      setCurrentStep('onboarding');
    } else {
      setCurrentStep('login');
    }
  };

  const handleOnboardingComplete = () => {
    markOnboardingComplete();
    setCurrentStep('login');
  };

  const handleLoginSuccess = () => setCurrentStep('chat_ready');
  const handleMenuToggle = () => setIsSidebarOpen((prev) => !prev);

  const handleSelectConversation = (conv: ConversationSession) => {
    setActiveConversationId(conv.id);
    setIsSidebarOpen(false);
  };

  const handleNewConversation = () => {
    setActiveConversationId(null);
    setIsSidebarOpen(false);
  };

  const handleOpenSettings = () => {
    setIsSidebarOpen(false);
    setCurrentStep('settings');
  };

  const handleOpenLogout = () => {
    setIsSidebarOpen(false);
    setIsLogoutDialogOpen(true);
  };

  const handleConfirmLogout = () => {
    setIsLogoutDialogOpen(false);
    signOut();
    setCurrentStep('login');
  };

  // ── Full-screen entry flows (no AppShell chrome) ──
  if (currentStep === 'splash') {
    return <SplashScreen onComplete={handleSplashComplete} />;
  }
  if (currentStep === 'onboarding') {
    return <OnboardingScreen onComplete={handleOnboardingComplete} />;
  }
  if (currentStep === 'login') {
    return <LoginScreen onSuccess={handleLoginSuccess} />;
  }

  // ── Settings ──
  if (currentStep === 'settings') {
    return (
      <>
        <div className="w-full h-[100dvh] flex justify-center bg-slate-950 overflow-hidden">
          <div className="w-full max-w-[440px] h-full flex flex-col bg-slate-900 shadow-2xl border-x border-slate-800/80 overflow-hidden">
            <SettingsScreen
              onBack={() => setCurrentStep('chat_ready')}
              onOpenLogoutDialog={handleOpenLogout}
            />
          </div>
        </div>
        <LogoutDialog
          isOpen={isLogoutDialogOpen}
          onConfirm={handleConfirmLogout}
          onCancel={() => setIsLogoutDialogOpen(false)}
        />
        <NetworkBanner />
      </>
    );
  }

  // ── Primary: Chat + Drawer ──
  return (
    <>
      <AppShell isMenuOpen={isSidebarOpen} onMenuClick={handleMenuToggle}>
        <ChatScreen activeConversation={activeConversation} />
      </AppShell>

      <SidebarDrawer
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
        onOpenSettings={handleOpenSettings}
        onOpenLogoutDialog={handleOpenLogout}
      />

      <LogoutDialog
        isOpen={isLogoutDialogOpen}
        onConfirm={handleConfirmLogout}
        onCancel={() => setIsLogoutDialogOpen(false)}
      />

      <NetworkBanner />
      <InstallPromptModal />
    </>
  );
}

export default App;
