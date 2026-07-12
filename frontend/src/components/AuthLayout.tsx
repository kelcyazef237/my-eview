import { useEffect, useRef, useState, type ReactNode } from 'react'
import { ShieldCheck, Activity, Building2, TrendingUp, Lock, BarChart3, Globe, BadgeCheck } from 'lucide-react'
import { api } from '@/api/client'

interface StatItem {
  label: string
  value: number
  suffix?: string
  icon: React.ElementType
  color: string
}

const DEFAULT_ORGS = 100
const DEFAULT_SCANS = 100

const STATIC_STATS: StatItem[] = [
  { label: 'Trust Vectors Tracked', value: 28, icon: BarChart3, color: 'var(--neon-cyan)' },
  { label: 'Avg. Score Uplift', value: 32, suffix: '%', icon: TrendingUp, color: 'var(--neon-green)' },
]

const FEATURES = [
  { icon: ShieldCheck, title: 'Verified Trust Scoring', desc: '1,000-point trust score across 8 categories.', color: 'var(--neon-cyan)' },
  { icon: Lock, title: 'Technical Drill-Down', desc: '28-vector evidence-backed security analysis.', color: 'var(--neon-violet)' },
  { icon: Globe, title: 'Entity Intelligence', desc: 'Related domains and shared infrastructure mapping.', color: 'var(--neon-magenta)' },
  { icon: BadgeCheck, title: 'Ownership Verification', desc: 'Domain-verified org ownership before access.', color: 'var(--neon-green)' },
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

function useClock() {
  const [time, setTime] = useState(() => new Date())
  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(t)
  }, [])
  return time
}

const TERMINAL_LINES = [
  '[boot] sys.boot.trust-os v1.0.4',
  '[init] loading vector model · 28 cats',
  '[net ] upstream OK · cms-edge.cm-01',
  '[auth] session.ready',
  '[ok  ] awaiting operator input_',
]

function TypingLine({ text, delay = 0 }: { text: string; delay?: number }) {
  const [shown, setShown] = useState('')
  useEffect(() => {
    let i = 0
    const id = setTimeout(() => {
      const t = setInterval(() => {
        i++
        setShown(text.slice(0, i))
        if (i >= text.length) clearInterval(t)
      }, 22)
      return () => clearInterval(t)
    }, delay)
    return () => clearTimeout(id)
  }, [text, delay])
  return <div className="num whitespace-pre">{shown}</div>
}

function StatCounter({ stat, index }: { stat: StatItem; index: number }) {
  const v = useCountUp(stat.value, 1400 + index * 200)
  const Icon = stat.icon
  return (
    <div
      className="panel glass-card-hover p-3 animate-fade-up"
      style={{ animationDelay: `${200 + index * 120}ms` }}
    >
      <div className="flex items-center gap-3">
        <div
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-sm"
          style={{
            background: `${stat.color}1a`,
            border: `1px solid ${stat.color}`,
            boxShadow: `0 0 12px ${stat.color}40`,
            color: stat.color,
          }}
        >
          <Icon size={16} />
        </div>
        <div className="min-w-0">
          <div
            className="num truncate text-xl font-bold leading-none"
            style={{ color: stat.color, textShadow: `0 0 8px ${stat.color}80` }}
          >
            {v.toLocaleString()}
            {stat.suffix}
          </div>
          <div className="mt-1 text-[10px] uppercase tracking-[0.12em] text-[var(--text-muted)]">
            {stat.label}
          </div>
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
  const clock = useClock()

  useEffect(() => {
    let alive = true
    api
      .publicStats()
      .then((s) => {
        if (!alive) return
        setOrgs(s.organizations)
        setScans(s.scans)
      })
      .catch(() => { /* keep defaults on failure */ })
    return () => {
      alive = false
    }
  }, [])

  const dynamicStats: StatItem[] = [
    { label: 'Organizations Trusted', value: orgs, suffix: '+', icon: Building2, color: 'var(--neon-cyan)' },
    { label: 'Scans Completed', value: scans, suffix: '+', icon: Activity, color: 'var(--neon-magenta)' },
  ]
  const STATS = [...dynamicStats, ...STATIC_STATS]

  return (
    <div className="mx-auto max-w-6xl py-8">
      {/* Single unified panel — HUD brackets encase the whole two-pane view */}
      <div className="panel-terminal glass-card-hero overflow-hidden">
        {/* Shared panel-header across both panes */}
        <div className="panel-header">
          <div className="flex items-center gap-3">
            <span className="dot dot-cyan" />
            <span>trust.os</span>
            <span className="text-[var(--neon-magenta)]">/</span>
            <span>{title.toLowerCase().replace(/\s/g, '_')}</span>
            <span className="dot dot-violet" />
          </div>
          <div className="flex items-center gap-3">
            <span className="num">{clock.toUTCString().slice(17, 25)} UTC</span>
            <span className="dot dot-green animate-pulse-soft" />
          </div>
        </div>

        {/* Two-pane split — one shared body, internal divider */}
        <div className="grid min-h-[calc(100vh-12rem)] grid-cols-1 lg:grid-cols-5">
          {/* ==== LEFT — form ==== */}
          <div className="relative flex flex-col justify-center p-6 animate-fade-in lg:col-span-2 lg:p-10">
            {/* vertical divider on lg screens */}
            <span
              aria-hidden
              className="pointer-events-none absolute right-0 top-6 bottom-6 hidden w-px lg:block"
              style={{
                background:
                  'linear-gradient(180deg, transparent, var(--neon-cyan) 30%, var(--neon-violet) 70%, transparent)',
                boxShadow: '0 0 12px rgba(var(--neon-cyan-rgb),0.4)',
              }}
            />

          <div className="mx-auto w-full max-w-md">
          <div className="mb-6 flex items-center gap-4">
            <div
              className="flex h-12 w-12 items-center justify-center rounded-sm relative"
              style={{
                background: 'var(--gradient-neon-soft)',
                border: '1px solid var(--neon-cyan)',
                boxShadow: '0 0 20px rgba(var(--neon-cyan-rgb),0.35), inset 0 0 12px rgba(var(--neon-cyan-rgb),0.2)',
                color: 'var(--neon-cyan)',
              }}
            >
              {icon}
              {/* corner ticks */}
              <span className="absolute -left-1 -top-1 h-2 w-2 border-t border-l border-[var(--neon-cyan)]" />
              <span className="absolute -right-1 -bottom-1 h-2 w-2 border-b border-r border-[var(--neon-magenta)]" />
            </div>
            <div className="flex-1">
              <div className="eyebrow">
                <span className="line" />
                <span>module :: auth</span>
              </div>
              <h1 className="display-title text-3xl gradient-text">{title}</h1>
            </div>
          </div>

          <p className="mb-6 text-sm text-[var(--text-secondary)]">{subtitle}</p>

          {/* terminal "ready" line */}
          <div className="mb-6 rounded-sm border border-[var(--glass-border-subtle)] terminal-surface px-3 py-2 num text-[12px] text-[var(--neon-green)]">
            <span className="prompt-prefix">$</span>
            <span>trust-os --ready</span>
            <span className="ml-2 text-[var(--text-muted)]">{`// awaiting credentials`}</span>
            <span className="caret" />
          </div>

          {children}

          <div className="mt-6 text-center text-sm text-[var(--text-muted)]">{footer}</div>
          </div>
          </div>

          {/* ==== RIGHT — branded info ==== */}
          <div className="relative hidden flex-col justify-center border-t border-[var(--glass-border-subtle)] p-6 lg:flex lg:col-span-3 lg:border-l lg:border-t-0 lg:p-10">
            <div className="flex h-full flex-col gap-6 bg-grid">
              {/* brand + tagline */}
              <div className="flex items-center gap-4 animate-fade-up">
                <div className="relative flex h-14 w-14 items-center justify-center rounded-sm text-black"
                  style={{
                    background: 'var(--gradient-neon)',
                    boxShadow: '0 0 30px rgba(var(--neon-cyan-rgb),0.5), 0 0 30px rgba(var(--neon-violet-rgb),0.4)',
                  }}
                >
                  <ShieldCheck size={28} />
                  <span className="absolute -right-1 -bottom-1 h-3 w-3 border-b border-r border-[var(--neon-magenta)]" />
                  <span className="absolute -left-1 -top-1 h-3 w-3 border-t border-l border-[var(--neon-cyan)]" />
                </div>
                <div>
                  <div
                    className="display-title text-2xl glitch"
                    data-text="MYEVIEW"
                    style={{ letterSpacing: '0.18em' }}
                  >
                    MYEVIEW
                  </div>
                  <div className="num text-[11px] uppercase tracking-[0.18em] text-[var(--text-muted)]">
                    trust.os / cm-01 / v1.0.4
                  </div>
                </div>
              </div>

              <div
                className="display-title text-2xl leading-tight animate-fade-up"
                style={{ animationDelay: '120ms', letterSpacing: '0.04em' }}
              >
                Measure. Prove. Improve.{' '}
                <span style={{
                  background: 'var(--gradient-neon)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}>Your Digital Trust.</span>
              </div>

              {/* terminal scroll lines */}
              <div className="rounded-sm border border-[var(--glass-border-subtle)] terminal-surface p-3 num text-[12px]">
                {TERMINAL_LINES.map((line, i) => {
                  const isLast = i === TERMINAL_LINES.length - 1
                  return (
                    <div
                      key={i}
                      className="text-[var(--neon-green)]"
                    >
                      <TypingLine text={line} delay={i * 250} />
                      {isLast && <span className="caret" />}
                    </div>
                  )
                })}
              </div>

              {/* stats */}
              <div className="grid grid-cols-2 gap-3">
                {STATS.map((s, i) => (
                  <StatCounter key={s.label} stat={s} index={i} />
                ))}
              </div>

              {/* features */}
              <div className="flex flex-col gap-3">
                <div className="eyebrow">
                  <span className="line" />
                  <span>capabilities</span>
                </div>
                {FEATURES.map((f, i) => {
                  const Icon = f.icon
                  return (
                    <div
                      key={f.title}
                      className="flex items-start gap-3 animate-fade-up"
                      style={{ animationDelay: `${600 + i * 110}ms` }}
                    >
                      <div
                        className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-sm"
                        style={{
                          border: `1px solid ${f.color}`,
                          background: `${f.color}1a`,
                          color: f.color,
                          boxShadow: `0 0 12px ${f.color}40`,
                        }}
                      >
                        <Icon size={14} />
                      </div>
                      <div>
                        <div className="display-title text-[12px] tracking-[0.08em] text-[var(--text-primary)]">
                          {f.title}
                        </div>
                        <div className="text-[12px] text-[var(--text-muted)]">{f.desc}</div>
                      </div>
                    </div>
                  )
                })}
              </div>

              {/* status bar */}
              <div className="mt-auto flex items-center justify-between rounded-sm border border-[var(--glass-border-subtle)] terminal-surface-strong px-3 py-2 num text-[10px] uppercase tracking-[0.18em] text-[var(--text-muted)]">
                <div className="flex items-center gap-2">
                  <span className="dot dot-green animate-pulse-soft" />
                  <span>node.cm-01</span>
                </div>
                <div className="flex items-center gap-3">
                  <span>uptime 99.9</span>
                  <span className="text-[var(--neon-cyan)]">·</span>
                  <span>latency 14ms</span>
                  <span className="text-[var(--neon-magenta)]">·</span>
                  <span>secure</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
