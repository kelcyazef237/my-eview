import { useEffect, useState } from 'react'

/**
 * Reads the live CSS-variable color values from :root so that Recharts
 * (which needs concrete color strings, not `var(--...)`) stays in sync with
 * the active light/dark theme.
 *
 * Returns a stable object that updates whenever the `dark` class on <html>
 * flips (and on first mount / storage / matchmedia changes).
 */
export interface ThemeColors {
  cyan: string
  violet: string
  magenta: string
  green: string
  amber: string
  red: string
  textPrimary: string
  textSecondary: string
  textMuted: string
  border: string
  bgElevated: string
  bgPrimary: string
}

function readColors(): ThemeColors {
  if (typeof window === 'undefined') {
    return {
      cyan: '#0e9bb4', violet: '#7c3aed', magenta: '#db2777',
      green: '#059669', amber: '#d97706', red: '#dc2626',
      textPrimary: '#0f172a', textSecondary: '#475569', textMuted: '#94a3b8',
      border: '#e2e8f0', bgElevated: '#ffffff', bgPrimary: '#ffffff',
    }
  }
  const cs = getComputedStyle(document.documentElement)
  const v = (name: string, fallback: string) =>
    cs.getPropertyValue(name).trim() || fallback
  return {
    cyan:    v('--neon-cyan',    '#0e9bb4'),
    violet:  v('--neon-violet',  '#7c3aed'),
    magenta: v('--neon-magenta', '#db2777'),
    green:   v('--neon-green',   '#059669'),
    amber:   v('--neon-amber',   '#d97706'),
    red:     v('--neon-red',     '#dc2626'),
    textPrimary:   v('--text-primary',   '#0f172a'),
    textSecondary: v('--text-secondary', '#475569'),
    textMuted:     v('--text-muted',     '#94a3b8'),
    border:  v('--border-color', '#e2e8f0'),
    bgElevated: v('--bg-elevated', '#ffffff'),
    bgPrimary:  v('--bg-primary',  '#ffffff'),
  }
}

export function useThemeColors(): ThemeColors {
  const [colors, setColors] = useState<ThemeColors>(readColors)

  useEffect(() => {
    setColors(readColors())
    const root = document.documentElement

    const observer = new MutationObserver(() => setColors(readColors()))
    observer.observe(root, { attributes: true, attributeFilter: ['class'] })

    const onStorage = (e: StorageEvent) => {
      if (e.key === 'myeview_theme') setColors(readColors())
    }
    window.addEventListener('storage', onStorage)

    return () => {
      observer.disconnect()
      window.removeEventListener('storage', onStorage)
    }
  }, [])

  return colors
}