import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Moon, Sun, Shield, Menu, X, LogIn, LogOut, UserPlus } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useTheme } from '@/hooks/useTheme'
import { api } from '@/api/client'
import type { User } from '@/types'

interface LayoutProps {
  children: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
  const { theme, toggle } = useTheme()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [user, setUser] = useState<User | null>(null)
  const location = useLocation()
  const navigate = useNavigate()
  const token = localStorage.getItem('myeview_token')
  const isPublic = !token

  useEffect(() => {
    if (token) {
      api.me()
        .then(setUser)
        .catch(() => {
          localStorage.removeItem('myeview_token')
          setUser(null)
        })
    } else {
      setUser(null)
    }
  }, [token, location.pathname])

  const isAdmin = user?.role === 'global_admin'

  const navItems = isPublic
    ? [{ label: 'Public Lookup', path: '/' }]
    : [
        ...(isAdmin ? [{ label: 'Admin', path: '/admin' }] : []),
        { label: 'Dashboard', path: '/dashboard' },
        { label: 'Verify', path: '/verify' },
        { label: 'Report', path: '/report' },
        { label: 'Settings', path: '/settings' },
      ]

  const handleLogout = () => {
    localStorage.removeItem('myeview_token')
    navigate('/')
    window.location.reload()
  }

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-50 border-b border-[var(--glass-border)] bg-[var(--glass-bg)] backdrop-blur-xl">
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
            {isPublic ? (
              <>
                <Link
                  to="/register"
                  className="hidden items-center gap-1.5 rounded-lg border border-[var(--glass-border)] px-3 py-1.5 text-sm font-medium transition-colors hover:bg-[var(--glass-bg)] md:flex"
                >
                  <UserPlus size={16} /> Register
                </Link>
                <Link
                  to="/login"
                  className="hidden items-center gap-1.5 rounded-lg border border-[var(--accent)] bg-[var(--accent)] px-3 py-1.5 text-sm font-medium text-white transition-opacity hover:opacity-90 md:flex"
                >
                  <LogIn size={16} /> Login
                </Link>
              </>
            ) : (
              <button
                onClick={handleLogout}
                className="hidden items-center gap-1.5 rounded-lg border border-[var(--glass-border)] px-3 py-1.5 text-sm font-medium transition-colors hover:bg-[var(--glass-bg)] md:flex"
              >
                <LogOut size={16} /> Logout
              </button>
            )}
            <button
              onClick={toggle}
              className="rounded-lg p-2 text-[var(--text-secondary)] transition-colors hover:bg-[var(--glass-bg)]"
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
            </button>
            <button
              className="rounded-lg p-2 text-[var(--text-secondary)] transition-colors hover:bg-[var(--glass-bg)] md:hidden"
              onClick={() => setMobileOpen(!mobileOpen)}
              aria-label="Toggle menu"
            >
              {mobileOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>

        {mobileOpen && (
          <nav className="border-t border-[var(--glass-border)] px-4 py-3 md:hidden">
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
            {isPublic ? (
              <>
                <Link
                  to="/register"
                  onClick={() => setMobileOpen(false)}
                  className="block py-2 text-sm font-medium text-[var(--text-secondary)]"
                >
                  Register
                </Link>
                <Link
                  to="/login"
                  onClick={() => setMobileOpen(false)}
                  className="block py-2 text-sm font-medium text-[var(--text-secondary)]"
                >
                  Login
                </Link>
              </>
            ) : (
              <button
                onClick={() => { handleLogout(); setMobileOpen(false) }}
                className="block py-2 text-sm font-medium text-[var(--text-secondary)]"
              >
                Logout
              </button>
            )}
          </nav>
        )}
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8">{children}</main>

      <footer className="border-t border-[var(--glass-border)] py-6 text-center text-xs text-[var(--text-muted)]">
        MYEVIEW — Cameroon external digital-trust scoring platform · Deterministic · Non-intrusive · Locally cached
      </footer>
    </div>
  )
}