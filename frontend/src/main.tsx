import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.tsx';
import { AuthProvider } from './context/AuthContext.tsx';
import { UserStateProvider } from './state/UserStateContext.tsx';

// Register PWA Service Worker only in production, and clear stale caches
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').then((reg) => {
      // Force update check on each page load
      reg.update().catch(() => {});
    }).catch(() => {
      // Silently ignore SW registration failures
    });
  });
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider>
      <UserStateProvider>
        <App />
      </UserStateProvider>
    </AuthProvider>
  </StrictMode>,
);
