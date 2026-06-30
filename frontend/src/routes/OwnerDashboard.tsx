import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Loader2, RefreshCw, AlertTriangle, CheckCircle2, ChevronDown, ChevronUp, Radar } from 'lucide-react'
import { api } from '@/api/client'
import { CategoryBreakdown } from '@/components/CategoryBreakdown'
import { EntityIntelligence } from '@/components/EntityIntelligence'
import { OrgSelector } from '@/components/OrgSelector'
import { ScoreGauge } from '@/components/ScoreGauge'
import { ScoreHistoryChart } from '@/components/ScoreHistoryChart'
import { TIAPanel } from '@/components/TIAPanel'
import { TechnicalTable } from '@/components/TechnicalTable'
import type { OwnerDashboardData, VectorFinding } from '@/types'

export function OwnerDashboard() {
  const [searchParams, setSearchParams] = useSearchParams()
  const orgId = searchParams.get('org_id') || undefined

  const handleSelectOrg = (id: string) => {
    const next = new URLSearchParams(searchParams)
    next.set('org_id', id)
    setSearchParams(next)
  }
  const [data, setData] = useState<OwnerDashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [rescanning, setRescanning] = useState(false)
  const [scanning, setScanning] = useState(false)
  const [showTechnical, setShowTechnical] = useState(false)
  const [vectors, setVectors] = useState<VectorFinding[]>([])
  const [loadingVectors, setLoadingVectors] = useState(false)
  const [showAllTIA, setShowAllTIA] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const d = await api.dashboard(orgId)
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
      await api.rescan(orgId)
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Rescan failed')
    } finally {
      setRescanning(false)
    }
  }

  const handlePortscan = async () => {
    setScanning(true)
    setError('')
    try {
      await api.triggerPortscan(orgId)
      setError('')
      setTimeout(() => load(), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Port scan failed to start')
    } finally {
      setScanning(false)
    }
  }

  const handleTechnicalToggle = async () => {
    if (!showTechnical && vectors.length === 0) {
      setLoadingVectors(true)
      try {
        const techData = await api.technical(orgId)
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
  }, [orgId])

  if (loading) {
    return (
      <div className="flex h-64 flex-col items-center justify-center gap-3 num text-[var(--text-muted)]">
        <Loader2 className="animate-spin text-[var(--neon-cyan)]" size={32} />
        <span className="text-[11px] uppercase tracking-[0.24em]">
          ▸ loading.dashboard
          <span className="caret" />
        </span>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div
        className="panel p-6 num text-[12px] uppercase tracking-[0.12em]"
        style={{ borderColor: 'var(--neon-red)', color: 'var(--neon-red)' }}
      >
        <span className="prompt-prefix">!</span>
        {error || 'no.dashboard.data'}
      </div>
    )
  }

  const canSeeTechnical =
    data.user_role === 'owner_technical' ||
    data.user_role === 'ops' ||
    data.user_role === 'global_admin'

  const totalPointsLost = data.categories.reduce((sum, c) => sum + c.points_lost, 0)

  const sortedTIA = [...data.tia].sort((a, b) => {
    const catA = data.categories.find((c) => c.category_id === a.category_id)
    const catB = data.categories.find((c) => c.category_id === b.category_id)
    return (catB?.points_lost || 0) - (catA?.points_lost || 0)
  })
  const visibleTIA = showAllTIA ? sortedTIA : sortedTIA.slice(0, 2)
  const hiddenTIACount = sortedTIA.length - 2

  return (
    <div className="space-y-8 stagger">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="eyebrow mb-1">
            <span className="line" />
            <span>module :: owner.dashboard</span>
          </div>
          <h1
            className="display-title text-3xl glitch"
            data-text={data.org.name}
            style={{ letterSpacing: '0.06em' }}
          >
            {data.org.name}
          </h1>
          <p className="num mt-1 text-[12px] uppercase tracking-[0.18em] text-[var(--neon-cyan)]">
            ▸ {data.org.domain}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <OrgSelector orgId={orgId} onSelect={handleSelectOrg} />
          {data.org.ownership_verified ? (
            <span className="badge badge-pass">
              <CheckCircle2 size={11} /> verified
            </span>
          ) : (
            <span className="badge badge-warn">
              <AlertTriangle size={11} /> unverified
            </span>
          )}
          <button
            onClick={handlePortscan}
            disabled={scanning}
            className="btn-ghost"
            title="Run verified port scan"
          >
            {scanning ? <Loader2 className="animate-spin" size={13} /> : <Radar size={13} />}
            Port Scan
          </button>
          <button
            onClick={handleRescan}
            disabled={rescanning}
            className="btn-gradient"
          >
            {rescanning ? <Loader2 className="animate-spin" size={14} /> : <RefreshCw size={14} />}
            Rescan
          </button>
        </div>
      </div>

      <ScoreGauge
        score={data.score.overall}
        tier={data.score.shield_tier}
        label={data.score.outlook}
        outlook={data.score.outlook}
        pointsLost={totalPointsLost}
        categoryCount={data.categories.length}
        sectorBenchmark={undefined}
      />

      {data.history.length > 0 && <ScoreHistoryChart data={data.history} />}

      <CategoryBreakdown categories={data.categories} />

      <div>
        <div className="eyebrow mb-4">
          <span className="line" />
          <span>module :: tia.analysis</span>
        </div>
        <div className="grid gap-4 lg:grid-cols-2">
          {visibleTIA.map((entry) => (
            <TIAPanel key={entry.category_id} tia={entry} />
          ))}
        </div>
        {hiddenTIACount > 0 && (
          <button
            onClick={() => setShowAllTIA(!showAllTIA)}
            className="mt-4 flex items-center gap-2 num text-[12px] uppercase tracking-[0.12em] text-[var(--neon-cyan)] hover:underline"
          >
            {showAllTIA ? (
              <>
                <ChevronUp size={14} /> show.less
              </>
            ) : (
              <>
                <ChevronDown size={14} /> expand.all ({hiddenTIACount} more)
              </>
            )}
          </button>
        )}
      </div>

      {data.entity_intelligence && <EntityIntelligence entity={data.entity_intelligence} />}

      {canSeeTechnical && (
        <div>
          <button
            onClick={handleTechnicalToggle}
            className="btn-gradient"
          >
            {showTechnical ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            {showTechnical ? 'Hide' : 'Expand'} · 24-vector drill-down
          </button>
          {showTechnical && (
            <div className="mt-4">
              {loadingVectors ? (
                <div className="flex h-32 items-center justify-center gap-2 num text-[12px] text-[var(--text-muted)]">
                  <Loader2 className="animate-spin text-[var(--neon-cyan)]" size={20} />
                  loading.vectors
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
