import { useEffect, useState } from 'react'
import { Loader2 } from 'lucide-react'
import { api } from '@/api/client'
import { ScoreGauge } from '@/components/ScoreGauge'
import { TechnicalTable } from '@/components/TechnicalTable'
import type { TechnicalDashboardData } from '@/types'

export function TechnicalDashboard() {
  const [data, setData] = useState<TechnicalDashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api
      .technical()
      .then(setData)
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load technical view'))
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
      <div className="rounded-lg border border-[var(--danger)]/30 bg-[var(--danger)]/10 p-6 text-[var(--danger)]">
        {error || 'No technical data available'}
      </div>
    )
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">
          <span className="gradient-text">Technical Vector Drill-Down</span>
        </h1>
        <span className="font-mono text-xs text-[var(--text-muted)]">Run {data.scan_run_id}</span>
      </div>

      <ScoreGauge
        score={data.overall_score}
        tier={data.shield_tier}
        label="Technical View"
        outlook="Detailed vector states and raw evidence references"
      />

      <div>
        <div className="section-title mb-4">Vector Findings ({data.vectors.length})</div>
        <TechnicalTable vectors={data.vectors} />
      </div>
    </div>
  )
}
