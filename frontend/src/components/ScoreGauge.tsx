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

interface ScoreGaugeProps {
  score: number
  tier: number
  label: string
  outlook: string
  pointsLost?: number
  categoryCount?: number
}

const tierColors: Record<number, string> = {
  1: '#9f4a4a',
  2: '#c67a2e',
  3: '#3b6e91',
  4: '#2e8a7a',
  5: '#1d5c3f',
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

export function ScoreGauge({ score, tier, label, outlook, pointsLost, categoryCount }: ScoreGaugeProps) {
  const radius = 60
  const stroke = 8
  const circumference = 2 * Math.PI * radius
  const color = tierColors[tier] || '#64748b'
  const targetOffset = circumference * (1 - score / 1000)

  const [offset, setOffset] = useState(circumference)

  useEffect(() => {
    const timer = setTimeout(() => setOffset(targetOffset), 100)
    return () => clearTimeout(timer)
  }, [targetOffset])

  const TierIcon = tierIcon(tier)
  const OutlookIcon = outlookIcon(outlook)
  const band = scoreBand(score)

  return (
    <div className="glass-card-hero p-8 animate-slide-up">
      <div className="relative flex flex-col items-center gap-6 sm:flex-row sm:items-center">
        {/* Circular progress ring */}
        <div className="relative flex-shrink-0" style={{ width: 150, height: 150 }}>
          <svg width="150" height="150" className="-rotate-90">
            <circle
              cx="75"
              cy="75"
              r={radius}
              fill="none"
              stroke="var(--glass-border)"
              strokeWidth={stroke}
            />
            <circle
              cx="75"
              cy="75"
              r={radius}
              fill="none"
              stroke={color}
              strokeWidth={stroke}
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              style={{
                transition: 'stroke-dashoffset 1.2s ease-out',
                filter: `drop-shadow(0 0 6px ${color}40)`,
              }}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-3xl font-bold tracking-tight">{score}</span>
            <span className="text-xs font-medium text-[var(--text-muted)]">/ 1000</span>
          </div>
        </div>

        {/* Info column */}
        <div className="flex flex-1 flex-col gap-2 relative">
          <div className="flex items-center gap-3">
            <div
              className="flex h-10 w-10 items-center justify-center rounded-lg"
              style={{ color, background: `${color}15` }}
            >
              <TierIcon size={24} />
            </div>
            <div className="section-title">Overall Trust Score</div>
          </div>

          <div className="text-2xl font-bold gradient-text">{band}</div>

          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold" style={{ color }}>
              Tier {tier}
            </span>
            <span className="text-[var(--text-muted)]">·</span>
            <span className="text-sm text-[var(--text-secondary)]">{label}</span>
          </div>

          <div className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
            <OutlookIcon size={16} className="text-[var(--accent)]" />
            <span>Outlook: {outlook}</span>
          </div>

          {pointsLost !== undefined && categoryCount !== undefined && (
            <div className="mt-1 text-xs text-[var(--text-muted)]">
              {pointsLost} points deducted across {categoryCount} categories
            </div>
          )}
        </div>
      </div>
    </div>
  )
}