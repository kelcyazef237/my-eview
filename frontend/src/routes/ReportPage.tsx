import { useEffect, useState } from 'react'
import { Download, Loader2, ExternalLink } from 'lucide-react'
import { api } from '@/api/client'
import { ScoreHistoryChart } from '@/components/ScoreHistoryChart'
import type { OwnerDashboardData, ScoreHistoryPoint } from '@/types'

export function ReportPage() {
  const [data, setData] = useState<OwnerDashboardData | null>(null)
  const [history, setHistory] = useState<ScoreHistoryPoint[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([api.dashboard(), api.history()])
      .then(([dash, hist]) => {
        setData(dash)
        setHistory(hist)
      })
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load report'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="animate-spin text-[var(--accent)]" size={32} />
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-red-800 dark:border-red-900 dark:bg-red-900/20 dark:text-red-300">
        {error || 'No report data available'}
      </div>
    )
  }

  const scanRunId = data.score.scan_run_id

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">Report Center</h1>
          <p className="text-[var(--text-secondary)]">{data.org.name} · {data.org.domain}</p>
        </div>
        <div className="flex gap-2">
          <a
            href={api.reportHtml(scanRunId)}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 rounded-lg border border-[var(--border-color)] px-4 py-2 text-sm font-medium hover:bg-[var(--bg-secondary)]"
          >
            <ExternalLink size={16} /> Web View
          </a>
          <a
            href={api.reportPdf(scanRunId)}
            className="flex items-center gap-2 rounded-lg bg-[var(--accent)] px-4 py-2 text-sm font-semibold text-white hover:bg-[var(--accent)]/90"
          >
            <Download size={16} /> PDF
          </a>
        </div>
      </div>

      <ScoreHistoryChart data={history} />

      <div className="card p-5">
        <div className="section-title mb-3">Latest Snapshot</div>
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="rounded-lg bg-[var(--bg-secondary)] p-4">
            <div className="text-sm text-[var(--text-muted)]">Score</div>
            <div className="text-2xl font-bold">{data.score.overall}</div>
          </div>
          <div className="rounded-lg bg-[var(--bg-secondary)] p-4">
            <div className="text-sm text-[var(--text-muted)]">Shield Tier</div>
            <div className="text-2xl font-bold">{data.score.shield_tier}</div>
          </div>
          <div className="rounded-lg bg-[var(--bg-secondary)] p-4">
            <div className="text-sm text-[var(--text-muted)]">Outlook</div>
            <div className="text-lg font-semibold">{data.score.outlook}</div>
          </div>
        </div>
      </div>
    </div>
  )
}
