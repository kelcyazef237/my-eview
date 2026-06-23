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
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="animate-spin text-[var(--accent)]" size={32} />
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="rounded-lg border border-[var(--danger)]/30 bg-[var(--danger)]/10 p-6 text-[var(--danger)]">
        {error || 'No dashboard data available'}
      </div>
    )
  }

  const canSeeTechnical = data.user_role === 'owner_technical' || data.user_role === 'ops' || data.user_role === 'global_admin'

  const totalPointsLost = data.categories.reduce((sum, c) => sum + c.points_lost, 0)

  // Sort TIA by criticality (most points lost first)
  const sortedTIA = [...data.tia].sort((a, b) => {
    const catA = data.categories.find((c) => c.category_id === a.category_id)
    const catB = data.categories.find((c) => c.category_id === b.category_id)
    return (catB?.points_lost || 0) - (catA?.points_lost || 0)
  })
  const visibleTIA = showAllTIA ? sortedTIA : sortedTIA.slice(0, 2)
  const hiddenTIACount = sortedTIA.length - 2

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">{data.org.name}</h1>
          <p className="text-[var(--text-secondary)]">{data.org.domain}</p>
        </div>
        <div className="flex items-center gap-3">
          <OrgSelector orgId={orgId} onSelect={handleSelectOrg} />
          {data.org.ownership_verified ? (
            <span className="badge badge-pass">
              <CheckCircle2 size={14} /> Verified
            </span>
          ) : (
            <span className="badge badge-warn">
              <AlertTriangle size={14} /> Unverified
            </span>
          )}
          <button
            onClick={handlePortscan}
            disabled={scanning}
            className="flex items-center gap-2 rounded-lg border border-[var(--glass-border)] px-4 py-2 text-sm font-medium transition-colors hover:bg-[var(--glass-bg)] disabled:opacity-50"
            title="Run verified port scan"
          >
            {scanning ? (
              <Loader2 className="animate-spin" size={16} />
            ) : (
              <Radar size={16} />
            )}
            Port Scan
          </button>
          <button
            onClick={handleRescan}
            disabled={rescanning}
            className="flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
            style={{ background: 'var(--gradient-accent)' }}
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
        pointsLost={totalPointsLost}
        categoryCount={data.categories.length}
      />

      {data.history.length > 0 && (
        <ScoreHistoryChart data={data.history} />
      )}

      <CategoryBreakdown categories={data.categories} />

      <div>
        <div className="section-title mb-4">Trust Impact Analysis</div>
        <div className="grid gap-4 lg:grid-cols-2">
          {visibleTIA.map((entry) => (
            <TIAPanel key={entry.category_id} tia={entry} />
          ))}
        </div>
        {hiddenTIACount > 0 && (
          <button
            onClick={() => setShowAllTIA(!showAllTIA)}
            className="mt-4 flex items-center gap-2 text-sm font-semibold text-[var(--accent)] hover:underline"
          >
            {showAllTIA ? (
              <>
                <ChevronUp size={16} /> Show Less
              </>
            ) : (
              <>
                <ChevronDown size={16} /> View All ({hiddenTIACount} more)
              </>
            )}
          </button>
        )}
      </div>

      {data.entity_intelligence && (
        <EntityIntelligence entity={data.entity_intelligence} />
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