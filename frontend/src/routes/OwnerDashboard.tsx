import { useEffect, useState } from 'react'
import { Loader2, RefreshCw, AlertTriangle, CheckCircle2, ChevronDown, ChevronUp } from 'lucide-react'
import { api } from '@/api/client'
import { CategoryCard } from '@/components/CategoryCard'
import { ScoreGauge } from '@/components/ScoreGauge'
import { ScoreHistoryChart } from '@/components/ScoreHistoryChart'
import { TIAPanel } from '@/components/TIAPanel'
import { TechnicalTable } from '@/components/TechnicalTable'
import type { OwnerDashboardData, VectorFinding } from '@/types'

export function OwnerDashboard() {
  const [data, setData] = useState<OwnerDashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [rescanning, setRescanning] = useState(false)
  const [showTechnical, setShowTechnical] = useState(false)
  const [vectors, setVectors] = useState<VectorFinding[]>([])
  const [loadingVectors, setLoadingVectors] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const d = await api.dashboard()
      setData(d)
      setError('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard')
    } finally {
      setLoading(false)
    }
  }

  const handleRescan = async () => {
    setRescanning(true)
    try {
      await api.rescan()
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Rescan failed')
    } finally {
      setRescanning(false)
    }
  }

  const handleTechnicalToggle = async () => {
    if (!showTechnical && vectors.length === 0) {
      setLoadingVectors(true)
      try {
        const techData = await api.technical()
        setVectors(techData.vectors)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load technical data')
      } finally {
        setLoadingVectors(false)
      }
    }
    setShowTechnical(!showTechnical)
  }

  useEffect(() => {
    load()
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
        {error || 'No dashboard data available'}
      </div>
    )
  }

  const canSeeTechnical = data.user_role === 'owner_technical' || data.user_role === 'ops'

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">{data.org.name}</h1>
          <p className="text-[var(--text-secondary)]">{data.org.domain}</p>
        </div>
        <div className="flex items-center gap-3">
          {data.org.ownership_verified ? (
            <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400">
              <CheckCircle2 size={14} /> Verified
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-800 dark:bg-amber-900/30 dark:text-amber-400">
              <AlertTriangle size={14} /> Unverified
            </span>
          )}
          <button
            onClick={handleRescan}
            disabled={rescanning}
            className="flex items-center gap-2 rounded-lg bg-[var(--accent)] px-4 py-2 text-sm font-semibold text-white hover:bg-[var(--accent)]/90 disabled:opacity-50"
          >
            {rescanning ? (
              <Loader2 className="animate-spin" size={16} />
            ) : (
              <RefreshCw size={16} />
            )}
            Rescan
          </button>
        </div>
      </div>

      <ScoreGauge
        score={data.score.overall}
        tier={data.score.shield_tier}
        label={data.score.outlook}
        outlook={data.score.outlook}
      />

      {data.history.length > 0 && (
        <ScoreHistoryChart data={data.history} />
      )}

      <div>
        <div className="section-title mb-4">Category Breakdown</div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {data.categories.map((cat) => (
            <CategoryCard key={cat.category_id} category={cat} />
          ))}
        </div>
      </div>

      <div>
        <div className="section-title mb-4">Trust Impact Analysis</div>
        <div className="grid gap-4 lg:grid-cols-2">
          {data.tia.map((entry) => (
            <TIAPanel key={entry.category_id} tia={entry} />
          ))}
        </div>
      </div>

      {data.entity_intelligence && (
        <div>
          <div className="mb-4 flex items-center gap-3">
            <div className="section-title">Entity Intelligence</div>
            <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-semibold text-slate-600 dark:bg-slate-800 dark:text-slate-400">
              Not Scored
            </span>
          </div>
          <div className="card grid gap-4 p-5 sm:grid-cols-2">
            <div>
              <div className="mb-1 text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">
                Related Domains
              </div>
              <div className="text-sm text-[var(--text-secondary)]">
                {data.entity_intelligence.related_domains.count} discovered subdomains
              </div>
              {data.entity_intelligence.related_domains.items.length > 0 && (
                <ul className="mt-2 space-y-1 font-mono text-xs text-[var(--text-muted)]">
                  {data.entity_intelligence.related_domains.items.slice(0, 10).map((d) => (
                    <li key={d}>{d}</li>
                  ))}
                </ul>
              )}
            </div>
            <div>
              <div className="mb-1 text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">
                Shared Infrastructure
              </div>
              <div className="text-sm text-[var(--text-secondary)]">
                Registrar: {data.entity_intelligence.shared_infrastructure.registrar || '—'}
              </div>
              <div className="mt-1 text-sm text-[var(--text-secondary)]">
                Name servers: {data.entity_intelligence.shared_infrastructure.name_servers.length}
              </div>
            </div>
          </div>
          <p className="mt-2 text-xs text-[var(--text-muted)]">
            {data.entity_intelligence.label}
          </p>
        </div>
      )}

      {canSeeTechnical && (
        <div>
          <button
            onClick={handleTechnicalToggle}
            className="flex items-center gap-2 text-sm font-semibold text-[var(--accent)] hover:underline"
          >
            {showTechnical ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            Technical View (24-Vector Drill-Down)
          </button>
          {showTechnical && (
            <div className="mt-4">
              {loadingVectors ? (
                <div className="flex h-32 items-center justify-center">
                  <Loader2 className="animate-spin text-[var(--accent)]" size={24} />
                </div>
              ) : (
                <TechnicalTable vectors={vectors} />
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}