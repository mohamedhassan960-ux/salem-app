export const tokens = {
  colors: {
    primary: {
      50: '#eff6ff',
      100: '#dbeafe',
      200: '#bfdbfe',
      300: '#93c5fd',
      400: '#60a5fa',
      500: '#3b82f6',
      600: '#2563eb',
      700: '#1d4ed8',
      800: '#1e40af',
      900: '#1e3a8a',
      navy: '#0a192f',
    },
    medical: {
      teal: '#0d9488',
      cyan: '#0284c7',
      emerald: '#059669',
      slate: '#0f172a',
      darkSurface: '#0b1329',
      cardSurface: '#131f3d',
      borderSubtle: '#1e293b',
    },
    text: {
      primary: '#f8fafc',
      secondary: '#94a3b8',
      muted: '#64748b',
      accent: '#38bdf8',
    }
  },
  typography: {
    fontFamily: {
      arabic: "'Cairo', system-ui, -apple-system, sans-serif",
      latin: "'Plus Jakarta Sans', system-ui, sans-serif",
    },
    sizes: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
    }
  },
  spacing: {
    touchTarget: '48px',
    headerHeight: '64px',
    composerHeight: '76px',
    maxAppWidth: '440px',
  },
  radius: {
    sm: '0.375rem',
    md: '0.75rem',
    lg: '1rem',
    xl: '1.25rem',
    full: '9999px',
  },
  shadows: {
    glow: '0 0 20px -5px rgba(56, 189, 248, 0.25)',
    header: '0 4px 20px -2px rgba(0, 0, 0, 0.3)',
    card: '0 8px 24px -4px rgba(0, 0, 0, 0.4)',
    composer: '0 -4px 24px -2px rgba(0, 0, 0, 0.35)',
  }
} as const;

export type DesignTokens = typeof tokens;
