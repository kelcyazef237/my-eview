import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Moon, Sun, Shield, Menu, X, LogIn, LogOut, UserPlus, Power } from 'lucide-react'
import { useEffect, useState } from 'react'
import { api } from '@/api/client'
import type { User } from '@/types'
import { ParticleBackground } from './ParticleBackground'
import { useTheme } from '@/hooks/useTheme'

interface LayoutProps {
  children: React.ReactNode
}

function useClock() {
  const [time, setTime] = useState(() => new Date())
  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(t)
  }, [])
  return time
}

export function Layout({ children }: LayoutProps) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const [user, setUser] = useState<User | null>(null)
  const location = useLocation()
  const navigate = useNavigate()
  const token = localStorage.getItem('myeview_token')
  const isPublic = !token
  const clock = useClock()
  const { theme, toggle } = useTheme()

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
    ? [
        { label: 'Public_Lookup', path: '/' },
      ]
    : [
        ...(isAdmin ? [{ label: 'Admin', path: '/admin' }, { label: 'New_Scan', path: '/admin/scan' }] : []),
        { label: 'Dashboard', path: '/dashboard' },
        { label: 'Technical', path: '/technical' },
        { label: 'Report', path: '/report' },
        { label: 'Settings', path: '/settings' },
      ]

  const handleLogout = () => {
    localStorage.removeItem('myeview_token')
    navigate('/')
    window.location.reload()
  }

  return (
    <div className="hack-canvas relative min-h-screen flex flex-col text-[var(--text-primary)]">
      <ParticleBackground />

      {/* ===== TOP BAR ===== */}
      <header className="sticky top-0 z-50">
        <div
          className="relative border-b border-[var(--glass-border)] backdrop-blur-xl"
          style={{
            background:
              'var(--glass-bg-strong)',
          }}
        >
          <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3">
            {/* Brand */}
            <Link to="/" className="group flex items-center gap-3">
              <div
                className="flex h-9 w-9 items-center justify-center rounded-sm"
                style={{
                  background:
                    'linear-gradient(135deg, rgba(var(--neon-cyan-rgb),0.2), rgba(var(--neon-violet-rgb),0.2))',
                  border: '1px solid var(--neon-cyan)',
                  boxShadow: '0 0 16px rgba(var(--neon-cyan-rgb),0.4)',
                }}
              >
                <Shield className="h-5 w-5 text-[var(--neon-cyan)]" />
              </div>
              <div className="flex flex-col leading-tight">
                <span
                  className="display-title text-base text-[var(--text-primary)] glitch"
                  data-text="MYEVIEW"
                >
                  MYEVIEW
                </span>
                <span className="num text-[10px] uppercase tracking-[0.18em] text-[var(--text-muted)]">
                  trust.os / v1.0
                </span>
              </div>
            </Link>

            {/* Nav */}
            <nav className="hidden items-center gap-1 md:flex">
              {navItems.map((item) => {
                const active = location.pathname === item.path
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`relative rounded-sm px-3 py-1.5 font-[var(--font-display)] text-[12px] uppercase tracking-[0.14em] transition-all ${
                      active
                        ? 'border border-[var(--neon-cyan)] bg-[rgba(var(--neon-cyan-rgb),0.08)] text-[var(--neon-cyan)] shadow-[0_0_16px_rgba(var(--neon-cyan-rgb),0.25)]'
                        : 'text-[var(--text-secondary)] hover:bg-[rgba(var(--neon-cyan-rgb),0.06)] hover:text-[var(--text-primary)]'
                    }`}
                  >
                    {active && (
                      <span className="absolute -left-1 top-1/2 h-3 w-[2px] -translate-y-1/2 bg-[var(--neon-magenta)]" />
                    )}
                    ▸ {item.label}
                  </Link>
                )
              })}
            </nav>

            {/* Right cluster */}
            <div className="flex items-center gap-2">
              {/* Clock (decorative, builds the "console" feel) */}
              <span className="num hidden text-[11px] text-[var(--text-muted)] md:inline">
                {clock.toUTCString().slice(17, 25)} UTC
              </span>

              {isPublic ? (
                <>
                  <Link
                    to="/register"
                    className="hidden items-center gap-1.5 rounded-sm border border-[var(--glass-border)] px-3 py-1.5 text-[12px] font-medium uppercase tracking-[0.12em] text-[var(--text-secondary)] transition-colors hover:bg-[rgba(var(--neon-cyan-rgb),0.08)] hover:text-[var(--text-primary)] md:flex"
                  >
                    <UserPlus size={14} /> Register
                  </Link>
                  <Link
                    to="/login"
                    className="hidden items-center gap-1.5 rounded-sm px-3 py-1.5 text-[12px] font-semibold uppercase tracking-[0.12em] text-black transition-all md:flex"
                    style={{ background: 'var(--gradient-neon)', boxShadow: '0 0 18px rgba(var(--neon-cyan-rgb),0.35)' }}
                  >
                    <LogIn size={14} /> Login
                  </Link>
                </>
              ) : (
                <button
                  onClick={handleLogout}
                  className="hidden items-center gap-1.5 rounded-sm border border-[var(--glass-border)] px-3 py-1.5 text-[12px] font-medium uppercase tracking-[0.12em] text-[var(--text-secondary)] transition-colors hover:bg-[rgba(var(--neon-cyan-rgb),0.08)] hover:text-[var(--text-primary)] md:flex"
                >
                  <LogOut size={14} /> Logout
                </button>
              )}
              <button
                onClick={toggle}
                className="rounded-sm border border-[var(--glass-border)] p-2 text-[var(--text-secondary)] transition-colors hover:bg-[rgba(var(--neon-cyan-rgb),0.08)] hover:text-[var(--neon-cyan)]"
                aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
                title={`Theme: ${theme}`}
              >
                {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
              </button>
              <button
                className="rounded-sm border border-[var(--glass-border)] p-2 text-[var(--text-secondary)] md:hidden"
                onClick={() => setMobileOpen(!mobileOpen)}
                aria-label="Toggle menu"
              >
                {mobileOpen ? <X size={18} /> : <Menu size={18} />}
              </button>
            </div>
          </div>

          {/* Mobile menu */}
          {mobileOpen && (
            <nav
              className="border-t border-[var(--glass-border)] px-4 py-3 md:hidden"
              style={{ background: 'var(--glass-bg-strong)' }}
            >
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setMobileOpen(false)}
                  className="block py-2 font-[var(--font-display)] text-[13px] uppercase tracking-[0.14em] text-[var(--text-secondary)]"
                >
                  ▸ {item.label}
                </Link>
              ))}
              {isPublic ? (
                <>
                  <Link
                    to="/register"
                    onClick={() => setMobileOpen(false)}
                    className="block py-2 font-[var(--font-display)] text-[13px] uppercase tracking-[0.14em] text-[var(--text-secondary)]"
                  >
                    ▸ Register
                  </Link>
                  <Link
                    to="/login"
                    onClick={() => setMobileOpen(false)}
                    className="block py-2 font-[var(--font-display)] text-[13px] uppercase tracking-[0.14em] text-[var(--neon-cyan)]"
                  >
                    ▸ Login
                  </Link>
                </>
              ) : (
                <button
                  onClick={() => { handleLogout(); setMobileOpen(false) }}
                  className="block py-2 font-[var(--font-display)] text-[13px] uppercase tracking-[0.14em] text-[var(--text-secondary)]"
                >
                  ▸ Logout
                </button>
              )}
            </nav>
          )}

          {/* Thin animated neon line at the very bottom */}
          <div
            className="h-px w-full"
            style={{
              background:
                'linear-gradient(90deg, transparent, var(--neon-cyan) 30%, var(--neon-violet) 60%, var(--neon-magenta) 90%, transparent)',
              boxShadow: '0 0 12px rgba(var(--neon-cyan-rgb), 0.4)',
            }}
          />
        </div>
      </header>

      {/* ===== MAIN ===== */}
      <main className="flex-1 w-full mx-auto max-w-7xl px-4 py-8 relative z-[2]">
        {children}
      </main>

      {/* ===== FOOTER ===== */}
      <footer className="relative z-[2] border-t border-[var(--glass-border)] py-5">
        <div
          className="mx-auto flex max-w-7xl flex-col items-center gap-2 px-4 text-[11px] text-[var(--text-muted)] sm:flex-row sm:justify-between"
          style={{ fontFamily: 'var(--font-mono)' }}
        >
          <div className="flex items-center gap-2 uppercase tracking-[0.18em]">
            <Power size={11} className="text-[var(--neon-green)]" />
            <span>system :: online</span>
            <span className="text-[var(--neon-magenta)]">/</span>
            <span>cluster cm-01</span>
          </div>
          <div className="uppercase tracking-[0.14em]">
            MYEVIEW · Cameroon external digital-trust scoring platform
          </div>
          <div className="flex items-center gap-3 uppercase tracking-[0.18em]">
            <span>deterministic</span>
            <span className="text-[var(--neon-cyan)]">·</span>
            <span>non-intrusive</span>
            <span className="text-[var(--neon-magenta)]">·</span>
            <span>cached</span>
          </div>
        </div>
      </footer>
    </div>
  )
}
