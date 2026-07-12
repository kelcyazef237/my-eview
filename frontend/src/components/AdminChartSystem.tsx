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
import { Loader2, ArrowRight } from 'lucide-react'
import { api } from '@/api/client'
import type { AdminOrg, CategoryScore } from '@/types'
import { useThemeColors } from '@/hooks/useThemeColors'

interface AdminChartSystemProps {
  orgs: AdminOrg[]
  onSelectOrg: (orgId: string) => void
}

function shortName(name: string): string {
  const words = name.split(' ')
  if (words.length <= 2) return name
  return words.slice(0, 2).join(' ')
}

export function AdminChartSystem({ orgs, onSelectOrg }: AdminChartSystemProps) {
  const [selectedOrgId, setSelectedOrgId] = useState<string | null>(null)
  const [categories, setCategories] = useState<CategoryScore[] | null>(null)
  const [loading, setLoading] = useState(false)
  const c = useThemeColors()

  const tierColors: Record<number, string> = {
    1: c.red,
    2: c.amber,
    3: c.cyan,
    4: c.green,
    5: c.violet,
  }

  const tooltipStyle = {
    backgroundColor: c.bgElevated,
    border: `1px solid ${c.border}`,
    borderRadius: 6,
    color: c.textPrimary,
    fontFamily: 'var(--font-mono)',
    fontSize: 12,
  } as const

  const orgsWithScores = orgs.filter((o) => o.latest_score !== null)

  useEffect(() => {
    if (!selectedOrgId && orgsWithScores.length > 0) {
      setSelectedOrgId(orgsWithScores[0].id)
    }
  }, [orgs])

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
      domain: o.domain.length > 22 ? o.domain.slice(0, 20) + '…' : o.domain,
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
    <div className="panel-terminal glass-card animate-fade-up">
      <div className="panel-header">
        <div className="flex items-center gap-2">
          <span className="dot dot-cyan" />
          <span>module :: system.overview</span>
        </div>
        <span>{orgs.length} orgs · {orgsWithScores.length} scored</span>
      </div>

      <div className="panel-body grid gap-6 lg:grid-cols-2">
        <div>
          <div className="eyebrow mb-2">
            <span className="line" />
            <span>organization.scores</span>
          </div>
          <div className="h-72 w-full rounded-sm terminal-surface p-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData} layout="vertical" margin={{ left: 10, right: 20, top: 5, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={`${c.cyan}1a`} horizontal={false} />
                <XAxis type="number" domain={[0, 1000]} tick={{ fill: c.textMuted, fontSize: 11 }} stroke={c.border} />
                <YAxis type="category" dataKey="domain" tick={{ fill: c.textMuted, fontSize: 10 }} stroke={c.border} width={120} />
                <Tooltip contentStyle={tooltipStyle} cursor={{ fill: `${c.cyan}10` }} />
                <Bar
                  dataKey="score"
                  radius={[0, 4, 4, 0]}
                  onClick={(data: { payload?: { orgId?: string } }) => {
                    if (data?.payload?.orgId) setSelectedOrgId(data.payload.orgId)
                  }}
                  cursor="pointer"
                >
                  {barData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.hasScore ? (tierColors[entry.tier] || c.textMuted) : c.textMuted}
                      opacity={entry.orgId === selectedOrgId ? 1 : 0.55}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div>
          <div className="mb-2 flex items-center justify-between">
            <div className="eyebrow">
              <span className="line" />
              <span>category.breakdown</span>
            </div>
            {selectedOrg && (
              <button
                onClick={() => onSelectOrg(selectedOrg.id)}
                className="flex items-center gap-1 num text-[11px] uppercase tracking-[0.12em] text-[var(--neon-cyan)] hover:underline"
              >
                {selectedOrg.domain}
                <ArrowRight size={11} />
              </button>
            )}
          </div>
          <div className="h-72 w-full rounded-sm terminal-surface p-2">
            {loading ? (
              <div className="flex h-full items-center justify-center gap-2 num text-[12px] text-[var(--text-muted)]">
                <Loader2 className="animate-spin text-[var(--neon-cyan)]" size={18} />
                fetching
              </div>
            ) : radarData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarData} outerRadius="65%">
                  <PolarGrid stroke={`${c.cyan}1a`} />
                  <PolarAngleAxis dataKey="shortName" tick={{ fill: c.textMuted, fontSize: 10 }} />
                  <PolarRadiusAxis domain={[0, maxPoints]} tick={{ fill: c.textMuted, fontSize: 9 }} />
                  <Radar dataKey="remaining" stroke={c.cyan} fill={c.cyan} fillOpacity={0.3} strokeWidth={2} />
                  <RTooltip contentStyle={tooltipStyle} />
                </RadarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full items-center justify-center num text-[12px] text-[var(--text-muted)]">
                ▸ select an organization to view its category breakdown
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="num border-t border-[var(--glass-border-subtle)] px-4 py-2 text-[11px] uppercase tracking-[0.12em] text-[var(--text-muted)]">
        ▸ click a bar to view that organization's category breakdown · click the domain link to open its dashboard
      </div>
    </div>
  )
}
