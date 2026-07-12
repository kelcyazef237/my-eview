import { useEffect, useState } from 'react'
import {
  ShieldAlert,
  ShieldQuestion,
  Shield as ShieldIcon,
  ShieldCheck,
  BadgeCheck,
  TrendingUp,
  TrendingDown,
  Minus,
} from 'lucide-react'
import { Shield } from './Shield'
import { useThemeColors } from '@/hooks/useThemeColors'

interface ScoreGaugeProps {
  score: number
  tier: number
  label: string
  outlook: string
  /** Points deducted (used for the "X lost across N categories" line) */
  pointsLost?: number
  categoryCount?: number
  /** Sector benchmark — when defined and below `score`, show
   *  "Above sector average" pill in green + bold. */
  sectorBenchmark?: number | null
}

const tierNames: Record<number, string> = {
  1: 'Critical',
  2: 'Elevated',
  3: 'Moderate',
  4: 'Strong',
  5: 'Exceptional',
}

function tierIcon(tier: number) {
  switch (tier) {
    case 1:
      return ShieldAlert
    case 2:
      return ShieldQuestion
    case 3:
      return ShieldIcon
    case 4:
      return ShieldCheck
    case 5:
      return BadgeCheck
    default:
      return ShieldIcon
  }
}

function scoreBand(score: number): string {
  if (score >= 900) return 'Exceptional'
  if (score >= 750) return 'Strong'
  if (score >= 600) return 'Moderate'
  if (score >= 400) return 'Elevated Risk'
  return 'Critical Risk'
}

function outlookIcon(outlook: string) {
  const lower = outlook.toLowerCase()
  if (lower.includes('positive') || lower.includes('improv')) return TrendingUp
  if (lower.includes('negative') || lower.includes('declin') || lower.includes('deterior')) return TrendingDown
  return Minus
}

export function ScoreGauge({
  score,
  tier,
  label,
  outlook,
  pointsLost,
  categoryCount,
  sectorBenchmark,
}: ScoreGaugeProps) {
  const c = useThemeColors()
  const tierColors: Record<number, string> = {
    1: c.red,
    2: c.amber,
    3: c.cyan,
    4: c.green,
    5: c.violet,
  }

  const radius = 70
  const stroke = 8
  const circumference = 2 * Math.PI * radius
  const color = tierColors[tier] || c.textMuted
  const targetOffset = circumference * (1 - score / 1000)

  const [offset, setOffset] = useState(circumference)

  useEffect(() => {
    const timer = setTimeout(() => setOffset(targetOffset), 100)
    return () => clearTimeout(timer)
  }, [targetOffset])

  const TierIcon = tierIcon(tier)
  const OutlookIcon = outlookIcon(outlook)
  const band = scoreBand(score)
  const tierName = tierNames[tier] || '—'
  const aboveAvg =
    sectorBenchmark !== undefined &&
    sectorBenchmark !== null &&
    score > sectorBenchmark

  return (
    <div className="panel-terminal glass-card-hero animate-fade-up overflow-hidden">
      {/* HUD header strip */}
      <div className="panel-header">
        <div className="flex items-center gap-3">
          <span className="dot dot-cyan" />
          <span>module :: trust.score</span>
          <span className="dot dot-violet" />
        </div>
        <div className="flex items-center gap-3">
          <span>live</span>
          <span className="dot dot-green animate-pulse-soft" />
        </div>
      </div>

      <div className="panel-body relative">
        <div className="relative flex flex-col gap-8 sm:flex-row sm:items-center">
          {/* ==== Circular conic ring ==== */}
          <div
            className="relative flex-shrink-0"
            style={{ width: 180, height: 180 }}
          >
            {/* rotating conic gradient backdrop */}
            <div
              className="absolute inset-0 rounded-full opacity-50 blur-xl"
              style={{
                background: `conic-gradient(from 0deg, ${color}, ${tierColors[5] || '#b400ff'}, ${tierColors[1] || '#ff3060'}, ${color})`,
                animation: 'spin 8s linear infinite',
              }}
            />
            <svg width="180" height="180" className="-rotate-90 relative">
              <defs>
                <linearGradient id="ringGrad" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stopColor={c.cyan} />
                  <stop offset="50%" stopColor={c.violet} />
                  <stop offset="100%" stopColor={c.magenta} />
                </linearGradient>
              </defs>
              <circle
                cx="90"
                cy="90"
                r={radius}
                fill="none"
                stroke={`${c.cyan}1a`}
                strokeWidth={stroke}
              />
              {/* ticks */}
              {Array.from({ length: 40 }).map((_, i) => {
                const a = (i / 40) * Math.PI * 2
                const r1 = radius + 8
                const r2 = radius + (i % 5 === 0 ? 16 : 12)
                const x1 = 90 + Math.cos(a) * r1
                const y1 = 90 + Math.sin(a) * r1
                const x2 = 90 + Math.cos(a) * r2
                const y2 = 90 + Math.sin(a) * r2
                return (
                  <line
                    key={i}
                    x1={x1}
                    y1={y1}
                    x2={x2}
                    y2={y2}
                    stroke={i % 5 === 0 ? `${c.cyan}b3` : `${c.cyan}4d`}
                    strokeWidth={i % 5 === 0 ? 1.2 : 0.6}
                  />
                )
              })}
              <circle
                cx="90"
                cy="90"
                r={radius}
                fill="none"
                stroke="url(#ringGrad)"
                strokeWidth={stroke}
                strokeLinecap="round"
                strokeDasharray={circumference}
                strokeDashoffset={offset}
                style={{
                  transition: 'stroke-dashoffset 1.4s ease-out',
                  filter: `drop-shadow(0 0 8px ${color})`,
                }}
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span
                className="num text-4xl font-bold leading-none glitch"
                style={{ color: c.textPrimary }}
                data-text={String(score)}
              >
                {score}
              </span>
              <span className="mt-1 num text-[10px] uppercase tracking-[0.18em] text-[var(--text-muted)]">
                / 1000 pts
              </span>
              <span
                className="num mt-2 text-[10px] uppercase tracking-[0.16em]"
                style={{ color }}
              >
                ▸ tier {tier}
              </span>
            </div>
          </div>

          {/* ==== Info column ==== */}
          <div className="flex flex-1 flex-col gap-3 relative">
            <div className="flex items-center gap-3">
              <div
                className="flex h-10 w-10 items-center justify-center rounded-sm"
                style={{
                  color: color,
                  background: `${color}22`,
                  border: `1px solid ${color}`,
                }}
              >
                <TierIcon size={22} />
              </div>
              <div>
                <div className="eyebrow">
                  <span className="line" />
                  <span>Overall Trust Score</span>
                </div>
                <div className="display-title text-2xl gradient-text leading-tight">
                  {band}
                </div>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <span
                className="rounded-sm px-2 py-1 num text-[12px]"
                style={{
                  border: `1px solid ${color}`,
                  background: `${color}15`,
                  color,
                }}
              >
                tier {tier} · {tierName}
              </span>
              <span className="badge badge-info">{label}</span>
              {aboveAvg && (
                <span
                  className="above-sector-avg inline-flex items-center gap-1 rounded-sm border px-2 py-1 text-[12px]"
                  style={{
                    borderColor: 'var(--neon-green)',
                    background: 'rgba(var(--neon-green-rgb), 0.12)',
                  }}
                  title={`Score ${score} > sector benchmark ${sectorBenchmark}`}
                >
                  ▲ Above Sector Average
                </span>
              )}
            </div>

            <div className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
              <OutlookIcon size={16} className="text-[var(--neon-cyan)]" />
              <span className="num text-[12px] uppercase tracking-[0.14em]">
                outlook :: {outlook}
              </span>
            </div>

            {pointsLost !== undefined && categoryCount !== undefined && (
              <div className="num text-[11px] uppercase tracking-[0.12em] text-[var(--text-muted)]">
                ▸ {pointsLost} points deducted across {categoryCount} categories
              </div>
            )}

            {/* ==== Shield glyph row — actual number of shields based on tier ==== */}
            <div className="mt-2 flex items-center gap-1.5 rounded-sm border border-[var(--glass-border-subtle)] terminal-surface-strong px-3 py-2">
              <span className="num text-[10px] uppercase tracking-[0.18em] text-[var(--text-muted)]">
                shield.tier
              </span>
              <div className="ml-2 flex items-end gap-1">
                {[1, 2, 3, 4, 5].map((i) => (
                  <Shield
                    key={i}
                    tier={i}
                    size="md"
                    active={i <= tier}
                  />
                ))}
              </div>
              <span
                className="ml-auto num text-[11px] uppercase tracking-[0.16em]"
                style={{ color }}
              >
                ×{tier}/5
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
