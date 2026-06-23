import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Download, Loader2, ExternalLink, Gauge, Shield as ShieldIcon, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { api } from '@/api/client'
import { CategoryBreakdown } from '@/components/CategoryBreakdown'
import { OrgSelector } from '@/components/OrgSelector'
import { ScoreGauge } from '@/components/ScoreGauge'
import { ScoreHistoryChart } from '@/components/ScoreHistoryChart'
import type { OwnerDashboardData, ScoreHistoryPoint } from '@/types'

const tierNames: Record<number, string> = {
  1: 'Critical',
  2: 'Elevated',
  3: 'Moderate',
  4: 'Strong',
  5: 'Exceptional',
}

function outlookIcon(outlook: string) {
  const lower = outlook.toLowerCase()
  if (lower.includes('positive') || lower.includes('improv')) return TrendingUp
  if (lower.includes('negative') || lower.includes('declin')) return TrendingDown
  return Minus
}

export function ReportPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const orgId = searchParams.get('org_id') || undefined

  const handleSelectOrg = (id: string) => {
    const next = new URLSearchParams(searchParams)
    next.set('org_id', id)
    setSearchParams(next)
  }
  const [data, setData] = useState<OwnerDashboardData | null>(null)
  const [history, setHistory] = useState<ScoreHistoryPoint[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([api.dashboard(orgId), api.history(orgId)])
      .then(([dash, hist]) => {
        setData(dash)
        setHistory(hist)
      })
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load report'))
      .finally(() => setLoading(false))
  }, [orgId])

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="animate-spin text-[var(--accent)]" size={32} />
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="rounded-lg border border-[var(--danger)]/30 bg-[var(--danger)]/10 p-6 text-[var(--danger)]">
        {error || 'No report data available'}
      </div>
    )
  }

  const scanRunId = data.score.scan_run_id
  const totalPointsLost = data.categories.reduce((sum, c) => sum + c.points_lost, 0)
  const OutlookIcon = outlookIcon(data.score.outlook)

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between animate-slide-up">
        <div>
          <h1 className="text-2xl font-bold">
            <span className="gradient-text">Report Center</span>
          </h1>
          <p className="text-[var(--text-secondary)]">{data.org.name} · {data.org.domain}</p>
        </div>
        <div className="flex gap-2">
          <OrgSelector orgId={orgId} onSelect={handleSelectOrg} />
          <a
            href={api.reportHtml(scanRunId)}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 rounded-lg border border-[var(--glass-border)] px-4 py-2 text-sm font-medium transition-colors hover:bg-[var(--glass-bg)]"
          >
            <ExternalLink size={16} /> Web View
          </a>
          <a
            href={api.reportPdf(scanRunId)}
            className="flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold text-white transition-opacity hover:opacity-90"
            style={{ background: 'var(--gradient-accent)' }}
          >
            <Download size={16} /> PDF
          </a>
        </div>
      </div>

      {/* Score Hero */}
      <ScoreGauge
        score={data.score.overall}
        tier={data.score.shield_tier}
        label={data.score.outlook}
        outlook={data.score.outlook}
        pointsLost={totalPointsLost}
        categoryCount={data.categories.length}
      />

      {/* Score History */}
      {history.length > 0 && (
        <ScoreHistoryChart data={history} />
      )}

      {/* Category Breakdown (radar default) */}
      <CategoryBreakdown categories={data.categories} defaultView="radar" />

      {/* Snapshot cards with icons */}
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="glass-card p-5 flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[var(--accent)]/10 text-[var(--accent)]">
            <Gauge size={24} />
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">Score</div>
            <div className="text-2xl font-bold">{data.score.overall}<span className="text-sm font-medium text-[var(--text-muted)]"> / 1000</span></div>
          </div>
        </div>

        <div className="glass-card p-5 flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[var(--accent)]/10 text-[var(--accent)]">
            <ShieldIcon size={24} />
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">Shield Tier</div>
            <div className="text-2xl font-bold">{data.score.shield_tier}<span className="text-sm font-medium text-[var(--text-muted)]"> · {tierNames[data.score.shield_tier] || '—'}</span></div>
          </div>
        </div>

        <div className="glass-card p-5 flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[var(--accent)]/10 text-[var(--accent)]">
            <OutlookIcon size={24} />
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">Outlook</div>
            <div className="text-lg font-semibold">{data.score.outlook}</div>
          </div>
        </div>
      </div>
    </div>
  )
}