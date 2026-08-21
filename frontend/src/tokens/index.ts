/**
 * SALEM Design Tokens — Single Source of Truth
 * 
 * Target Visual Balance:
 * - 70% Neutral/Light surfaces (#F7F9FC, #FFFFFF)
 * - 20% Navy brand identity (#061A3A, #0B2454, #1E3A8A)
 * - 10% Blue accent & CTA (#2D8BFF, #4D9BFF)
 */

export const tokens = {
  colors: {
    // Brand Navy & Blues
    brand: {
      darkestNavy: '#061A3A',
      deepNavy: '#0B2454',
      navy: '#0F2D5E',
      primaryBlue: '#1E3A8A',
      brightBlue: '#2D8BFF',
      electricBlue: '#4D9BFF',
      softBlue: '#7FAFFF',
      veryLightBlue: '#A5C1FF',
    },
    // Light Product Surfaces (Main App Experience)
    light: {
      background: '#F7F9FC',
      surface: '#FFFFFF',
      surfaceSecondary: '#F4F7FB',
      input: '#F1F5FA',
      border: '#D9E2F0',
      borderStrong: '#C4D1E3',
      primaryText: '#061A3A',
      secondaryText: '#5F708C',
      mutedText: '#8291A8',
      primary: '#1E3A8A',
      cta: '#2D8BFF',
    },
    // Semantic Status Colors
    semantic: {
      success: '#34D399',
      warning: '#FBBF24',
      error: '#F87171',
      info: '#4D9BFF',
    },
  },

  typography: {
    fontFamily: {
      arabic: "'Cairo', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    },
    // Strict scale: fontSize / lineHeight
    scale: {
      screenTitle: { size: '1.5rem', lineHeight: '2.375rem', weight: 700 }, // 24 / 38
      sectionTitle: { size: '1.25rem', lineHeight: '2rem', weight: 600 },    // 20 / 32
      body: { size: '1rem', lineHeight: '1.625rem', weight: 400 },           // 16 / 26
      bodyMedium: { size: '1rem', lineHeight: '1.625rem', weight: 500 },     // 16 / 26
      secondary: { size: '0.875rem', lineHeight: '1.375rem', weight: 400 },  // 14 / 22
      metadata: { size: '0.8125rem', lineHeight: '1.25rem', weight: 500 },   // 13 / 20
      small: { size: '0.75rem', lineHeight: '1.125rem', weight: 400 },       // 12 / 18
      button: { size: '1rem', lineHeight: '1.625rem', weight: 600 },         // 16 / 26
      buttonSmall: { size: '0.875rem', lineHeight: '1.375rem', weight: 600 },// 14 / 22
    },
  },

  // Allowed Spacing: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64
  spacing: {
    1: '4px',
    2: '8px',
    3: '12px',
    4: '16px',
    5: '20px',
    6: '24px',
    8: '32px',
    10: '40px',
    12: '48px',
    16: '64px',
    touchTargetMin: '44px',
  },

  // Allowed Radius: 8, 12, 16, 20, 24, 9999
  radius: {
    sm: '8px',
    md: '12px',
    lg: '16px',
    xl: '20px',
    '2xl': '24px',
    full: '9999px',
  },

  // Motion timings
  motion: {
    micro: '150ms ease-out',
    component: '250ms ease-out',
    screen: '350ms ease-out',
  },

  // Elevation shadows (calm and subtle)
  shadows: {
    sm: '0 1px 3px 0 rgba(6, 26, 58, 0.04), 0 1px 2px 0 rgba(6, 26, 58, 0.02)',
    md: '0 4px 6px -1px rgba(6, 26, 58, 0.06), 0 2px 4px -1px rgba(6, 26, 58, 0.03)',
    lg: '0 10px 15px -3px rgba(6, 26, 58, 0.08), 0 4px 6px -2px rgba(6, 26, 58, 0.04)',
    drawer: '0 20px 25px -5px rgba(6, 26, 58, 0.15), 0 10px 10px -5px rgba(6, 26, 58, 0.04)',
  },
} as const;

export type DesignTokens = typeof tokens;
