import { useEffect, useState } from 'react'
import {
  BarChart,
  Bar,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Tooltip as RTooltip,
} from 'recharts'
import { BarChart3, Loader2, ArrowRight } from 'lucide-react'
import { api } from '@/api/client'
import type { AdminOrg, CategoryScore } from '@/types'

interface AdminChartSystemProps {
  orgs: AdminOrg[]
  onSelectOrg: (orgId: string) => void
}

const tierColors: Record<number, string> = {
  1: '#9f4a4a',
  2: '#c67a2e',
  3: '#3b6e91',
  4: '#2e8a7a',
  5: '#1d5c3f',
}

const tooltipStyle = {
  backgroundColor: 'var(--bg-elevated)',
  border: '1px solid var(--border-color)',
  borderRadius: '0.5rem',
} as const

function shortName(name: string): string {
  const words = name.split(' ')
  if (words.length <= 2) return name
  return words.slice(0, 2).join(' ')
}

export function AdminChartSystem({ orgs, onSelectOrg }: AdminChartSystemProps) {
  const [selectedOrgId, setSelectedOrgId] = useState<string | null>(null)
  const [categories, setCategories] = useState<CategoryScore[] | null>(null)
  const [loading, setLoading] = useState(false)

  const orgsWithScores = orgs.filter((o) => o.latest_score !== null)

  // Auto-select first org with a score on mount
  useEffect(() => {
    if (!selectedOrgId && orgsWithScores.length > 0) {
      setSelectedOrgId(orgsWithScores[0].id)
    }
  }, [orgs])

  // Fetch category breakdown when selected org changes
  useEffect(() => {
    if (!selectedOrgId) return
    setLoading(true)
    api.dashboard(selectedOrgId)
      .then((data) => setCategories(data.categories))
      .catch(() => setCategories(null))
      .finally(() => setLoading(false))
  }, [selectedOrgId])

  const barData = orgs
    .map((o) => ({
      domain: o.domain.length > 20 ? o.domain.slice(0, 18) + '…' : o.domain,
      fullDomain: o.domain,
      score: o.latest_score ?? 0,
      orgId: o.id,
      tier: o.latest_shield_tier ?? 0,
      hasScore: o.latest_score !== null,
    }))
    .sort((a, b) => b.score - a.score)

  const selectedOrg = orgs.find((o) => o.id === selectedOrgId)

  const scoredCategories = (categories || []).filter((c) => c.points_total > 0)
  const maxPoints = Math.max(...scoredCategories.map((c) => c.points_total), 1)
  const radarData = scoredCategories.map((c) => ({
    shortName: shortName(c.category_name),
    remaining: c.points_remaining,
    total: c.points_total,
  }))

  return (
    <div className="glass-card p-6 animate-slide-up">
      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--accent)]/10 text-[var(--accent)]">
          <BarChart3 size={18} />
        </div>
        <div className="section-title">System Overview</div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Bar chart — org scores */}
        <div>
          <div className="mb-2 text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">
            Organization Scores
          </div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={barData}
                layout="vertical"
                margin={{ left: 10, right: 20, top: 5, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" horizontal={false} />
                <XAxis
                  type="number"
                  domain={[0, 1000]}
                  tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
                  stroke="var(--border-color)"
                />
                <YAxis
                  type="category"
                  dataKey="domain"
                  tick={{ fill: 'var(--text-muted)', fontSize: 10 }}
                  stroke="var(--border-color)"
                  width={110}
                />
                <Tooltip
                  contentStyle={tooltipStyle}
                  itemStyle={{ color: 'var(--text-primary)' }}
                  cursor={{ fill: 'var(--glass-bg)' }}
                />
                <Bar
                  dataKey="score"
                  radius={[0, 4, 4, 0]}
                  onClick={(data: { payload?: { orgId?: string } }) => {
                    if (data?.payload?.orgId) {
                      setSelectedOrgId(data.payload.orgId)
                    }
                  }}
                  cursor="pointer"
                >
                  {barData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.hasScore ? (tierColors[entry.tier] || '#64748b') : 'var(--text-muted)'}
                      opacity={entry.orgId === selectedOrgId ? 1 : 0.6}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Radar chart — selected org's category breakdown */}
        <div>
          <div className="mb-2 flex items-center justify-between">
            <div className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">
              Category Breakdown
            </div>
            {selectedOrg && (
              <button
                onClick={() => onSelectOrg(selectedOrg.id)}
                className="flex items-center gap-1 text-xs font-medium text-[var(--accent)] hover:underline"
              >
                {selectedOrg.domain}
                <ArrowRight size={12} />
              </button>
            )}
          </div>
          <div className="h-72 w-full">
            {loading ? (
              <div className="flex h-full items-center justify-center">
                <Loader2 className="animate-spin text-[var(--accent)]" size={24} />
              </div>
            ) : radarData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarData} outerRadius="65%">
                  <PolarGrid stroke="var(--border-color)" />
                  <PolarAngleAxis
                    dataKey="shortName"
                    tick={{ fill: 'var(--text-muted)', fontSize: 10 }}
                  />
                  <PolarRadiusAxis
                    domain={[0, maxPoints]}
                    tick={{ fill: 'var(--text-muted)', fontSize: 9 }}
                  />
                  <Radar
                    dataKey="remaining"
                    stroke="var(--accent)"
                    fill="var(--accent)"
                    fillOpacity={0.3}
                    strokeWidth={2}
                  />
                  <RTooltip
                    contentStyle={tooltipStyle}
                    itemStyle={{ color: 'var(--text-primary)' }}
                  />
                </RadarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full items-center justify-center text-sm text-[var(--text-muted)]">
                Select an organization to view its category breakdown
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="mt-2 text-xs text-[var(--text-muted)]">
        Click a bar to view that organization's category breakdown. Click the domain link to open its dashboard.
      </div>
    </div>
  )
}