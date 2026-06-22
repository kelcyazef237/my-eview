import { Link, useLocation } from 'react-router-dom'
import { Moon, Sun, Shield, Menu, X } from 'lucide-react'
import { useState } from 'react'
import { useTheme } from '@/hooks/useTheme'

interface LayoutProps {
  children: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
  const { theme, toggle } = useTheme()
  const [mobileOpen, setMobileOpen] = useState(false)
  const location = useLocation()
  const token = localStorage.getItem('myeview_token')
  const isPublic = !token

  const navItems = isPublic
    ? [{ label: 'Public Lookup', path: '/' }]
    : [
        { label: 'Dashboard', path: '/dashboard' },
        { label: 'Verify', path: '/verify' },
        { label: 'Report', path: '/report' },
        { label: 'Settings', path: '/settings' },
      ]

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-50 border-b border-[var(--border-color)] bg-[var(--bg-elevated)]/80 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
          <Link to="/" className="flex items-center gap-2">
            <Shield className="h-6 w-6 text-[var(--accent)]" />
            <span className="text-xl font-bold tracking-tight">MYEVIEW</span>
          </Link>

          <nav className="hidden items-center gap-6 md:flex">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`text-sm font-medium transition-colors ${
                  location.pathname === item.path
                    ? 'text-[var(--accent)]'
                    : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                }`}
              >
                {item.label}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-2">
            <button
              onClick={toggle}
              className="rounded-lg p-2 text-[var(--text-secondary)] hover:bg-[var(--bg-secondary)]"
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
            </button>
            <button
              className="rounded-lg p-2 text-[var(--text-secondary)] hover:bg-[var(--bg-secondary)] md:hidden"
              onClick={() => setMobileOpen(!mobileOpen)}
              aria-label="Toggle menu"
            >
              {mobileOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>

        {mobileOpen && (
          <nav className="border-t border-[var(--border-color)] px-4 py-3 md:hidden">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setMobileOpen(false)}
                className="block py-2 text-sm font-medium text-[var(--text-secondary)]"
              >
                {item.label}
              </Link>
            ))}
          </nav>
        )}
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8">{children}</main>

      <footer className="border-t border-[var(--border-color)] py-6 text-center text-xs text-[var(--text-muted)]">
        MYEVIEW — Cameroon external digital-trust scoring platform · Deterministic · Non-intrusive · Locally cached
      </footer>
    </div>
  )
}
