import { Shield, shieldColor } from './Shield'

interface ScoreGaugeProps {
  score: number
  tier: number
  label: string
  outlook: string
}

export function ScoreGauge({ score, tier, label, outlook }: ScoreGaugeProps) {
  const colorClass = shieldColor(tier)

  return (
    <div className="card p-6">
      <div className="flex items-center gap-6">
        <div className={colorClass}>
          <Shield tier={tier} size="xl" />
        </div>
        <div>
          <div className="section-title mb-1">Overall Trust Score</div>
          <div className="flex items-baseline gap-3">
            <span className="text-5xl font-bold tracking-tight">{score}</span>
            <span className="text-lg font-medium text-[var(--text-secondary)]">
              / 1000
            </span>
          </div>
          <div className="mt-1 text-lg font-semibold text-[var(--accent)]">
            {label} · Tier {tier}
          </div>
          <div className="mt-1 text-sm text-[var(--text-secondary)]">
            Outlook: {outlook}
          </div>
        </div>
      </div>
    </div>
  )
}
