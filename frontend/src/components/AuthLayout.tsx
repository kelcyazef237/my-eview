import { useEffect, useRef, useState, type ReactNode } from 'react'
import { ShieldCheck, Activity, Building2, TrendingUp, Lock, BarChart3, Globe, BadgeCheck } from 'lucide-react'
import { api } from '@/api/client'

interface StatItem {
  label: string
  value: number
  suffix?: string
  icon: React.ElementType
}

// Defaults shown until real stats load (and as a floor if the API call fails).
const DEFAULT_ORGS = 100
const DEFAULT_SCANS = 100

const STATIC_STATS: StatItem[] = [
  { label: 'Trust Vectors Tracked', value: 28, icon: BarChart3 },
  { label: 'Avg. Score Uplift', value: 32, suffix: '%', icon: TrendingUp },
]

const FEATURES = [
  { icon: ShieldCheck, title: 'Verified Trust Scoring', desc: '1,000-point trust score across 8 categories.' },
  { icon: Lock, title: 'Technical Drill-Down', desc: '28-vector evidence-backed security analysis.' },
  { icon: Globe, title: 'Entity Intelligence', desc: 'Related domains and shared infrastructure mapping.' },
  { icon: BadgeCheck, title: 'Ownership Verification', desc: 'Domain-verified org ownership before access.' },
]

function useCountUp(target: number, duration = 1600, start = 0) {
  const [value, setValue] = useState(start)
  const ref = useRef<number>(0)
  useEffect(() => {
    let raf = 0
    const t0 = performance.now()
    const tick = (now: number) => {
      const p = Math.min((now - t0) / duration, 1)
      const eased = 1 - Math.pow(1 - p, 3)
      setValue(Math.round(start + (target - start) * eased))
      if (p < 1) raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    ref.current = raf
    return () => cancelAnimationFrame(raf)
  }, [target, duration, start])
  return value
}

function StatCounter({ stat, index }: { stat: StatItem; index: number }) {
  const v = useCountUp(stat.value, 1400 + index * 200)
  const Icon = stat.icon
  return (
    <div
      className="glass-card-hover rounded-xl p-4 animate-slide-up"
      style={{ animationDelay: `${200 + index * 120}ms` }}
    >
      <div className="flex items-center gap-3">
        <div
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg"
          style={{ background: 'var(--gradient-accent-soft)' }}
        >
          <Icon size={18} className="text-[var(--accent)]" />
        </div>
        <div>
          <div className="text-2xl font-bold leading-none">
            {v.toLocaleString()}
            {stat.suffix}
          </div>
          <div className="mt-1 text-xs text-[var(--text-muted)]">{stat.label}</div>
        </div>
      </div>
    </div>
  )
}

interface AuthLayoutProps {
  title: string
  subtitle: string
  icon: ReactNode
  children: ReactNode
  footer: ReactNode
}

export function AuthLayout({ title, subtitle, icon, children, footer }: AuthLayoutProps) {
  const [orgs, setOrgs] = useState(DEFAULT_ORGS)
  const [scans, setScans] = useState(DEFAULT_SCANS)

  useEffect(() => {
    let alive = true
    api
      .publicStats()
      .then((s) => {
        if (!alive) return
        setOrgs(s.organizations)
        setScans(s.scans)
      })
      .catch(() => {
        /* keep defaults on failure */
      })
    return () => {
      alive = false
    }
  }, [])

  const dynamicStats: StatItem[] = [
    { label: 'Organizations Trusted', value: orgs, suffix: '+', icon: Building2 },
    { label: 'Scans Completed', value: scans, suffix: '+', icon: Activity },
  ]
  const STATS = [...dynamicStats, ...STATIC_STATS]

  return (
    <div className="mx-auto grid min-h-[calc(100vh-8rem)] max-w-6xl items-stretch gap-8 py-8 lg:grid-cols-2">
      {/* Left — form */}
      <div className="flex flex-col justify-center animate-fade-in">
        <div className="mx-auto w-full max-w-md">
          <div className="mb-8 text-center">
            <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl gradient-surface animate-glow">
              {icon}
            </div>
            <h1 className="mb-2 text-3xl font-bold">
              <span className="gradient-text">{title}</span>
            </h1>
            <p className="text-[var(--text-secondary)]">{subtitle}</p>
          </div>
          {children}
          <div className="mt-6 text-center text-sm text-[var(--text-muted)]">{footer}</div>
        </div>
      </div>

      {/* Right — branded info panel */}
      <div className="relative hidden flex-col justify-center overflow-hidden rounded-3xl lg:flex">
        <div
          className="glass-card-hero absolute inset-0"
          style={{ borderRadius: '1.5rem' }}
        />
        <div className="relative z-10 flex flex-col gap-6 p-10">
          {/* Brand */}
          <div className="animate-slide-up">
            <div className="flex items-center gap-3">
              <div
                className="flex h-11 w-11 items-center justify-center rounded-xl text-white"
                style={{ background: 'var(--gradient-accent)' }}
              >
                <ShieldCheck size={22} />
              </div>
              <div>
                <div className="text-xl font-bold tracking-tight">
                  <span className="gradient-text">MYEVIEW</span>
                </div>
                <div className="text-xs text-[var(--text-muted)]">Trust Intelligence Platform</div>
              </div>
            </div>
          </div>

          {/* Tagline */}
          <div
            className="animate-slide-up text-2xl font-semibold leading-snug"
            style={{ animationDelay: '120ms' }}
          >
            Measure, prove, and improve your organization's digital trust.
          </div>

          {/* Stats grid */}
          <div className="grid grid-cols-2 gap-3">
            {STATS.map((s, i) => (
              <StatCounter key={s.label} stat={s} index={i} />
            ))}
          </div>

          {/* Features */}
          <div className="flex flex-col gap-3">
            {FEATURES.map((f, i) => {
              const Icon = f.icon
              return (
                <div
                  key={f.title}
                  className="flex items-start gap-3 animate-slide-up"
                  style={{ animationDelay: `${600 + i * 120}ms` }}
                >
                  <div
                    className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg"
                    style={{ background: 'var(--gradient-accent-soft)' }}
                  >
                    <Icon size={15} className="text-[var(--accent)]" />
                  </div>
                  <div>
                    <div className="text-sm font-semibold">{f.title}</div>
                    <div className="text-xs text-[var(--text-muted)]">{f.desc}</div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}