import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.tsx';
import { AuthProvider } from './context/AuthContext.tsx';
import { UserStateProvider } from './state/UserStateContext.tsx';

// Build and version diagnostics for runtime verification
const APP_VERSION = '3.2.0';
const BUILD_ID = `build_${Date.now()}`;
const SW_CACHE_VERSION = 'salem-medical-rag-v6';

(window as unknown as { __SALEM_DIAGNOSTICS__: Record<string, string> }).__SALEM_DIAGNOSTICS__ = {
  APP_VERSION,
  BUILD_ID,
  SW_CACHE_VERSION,
};

console.info(`[Oxygen App] Initialized v${APP_VERSION} (${BUILD_ID}) | Cache: ${SW_CACHE_VERSION}`);

// Register PWA Service Worker in production with safe background update lifecycle
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/sw.js')
      .then((reg) => {
        reg.update().catch(() => {});
      })
      .catch((err) => {
        console.warn('[SW] Registration failed:', err);
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
