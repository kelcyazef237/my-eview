import { useState } from 'react'
import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Tooltip as RTooltip,
  BarChart,
  Bar,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
} from 'recharts'
import { LayoutGrid, Radar as RadarIcon, BarChart3 } from 'lucide-react'
import { CategoryCard } from './CategoryCard'
import type { CategoryScore } from '@/types'
import { useThemeColors } from '@/hooks/useThemeColors'

interface CategoryBreakdownProps {
  categories: CategoryScore[]
  defaultView?: 'cards' | 'radar' | 'bar'
}

function shortName(name: string): string {
  const words = name.split(' ')
  if (words.length <= 2) return name
  return words.slice(0, 2).join(' ')
}

function barColor(remaining: number, total: number, c: { green: string; amber: string; red: string }): string {
  const ratio = (total - remaining) / total
  if (ratio === 0) return c.green
  if (ratio < 0.3) return c.amber
  return c.red
}

export function CategoryBreakdown({ categories, defaultView = 'cards' }: CategoryBreakdownProps) {
  const [view, setView] = useState<'cards' | 'radar' | 'bar'>(defaultView)
  const c = useThemeColors()

  const scored = categories.filter((c) => c.points_total > 0)
  const maxPoints = Math.max(...scored.map((c) => c.points_total), 1)

  const chartData = scored.map((c) => ({
    shortName: shortName(c.category_name),
    remaining: c.points_remaining,
    total: c.points_total,
  }))

  const buttons: { mode: 'cards' | 'radar' | 'bar'; icon: typeof LayoutGrid; label: string }[] = [
    { mode: 'cards', icon: LayoutGrid, label: 'Cards' },
    { mode: 'radar', icon: RadarIcon, label: 'Radar' },
    { mode: 'bar', icon: BarChart3, label: 'Bars' },
  ]

  const tooltipStyle = {
    background: c.bgElevated,
    border: `1px solid ${c.border}`,
    borderRadius: 6,
    color: c.textPrimary,
  } as const
  const gridStroke = `${c.cyan}1a`
  const tick = (size: number) => ({ fill: c.textMuted, fontSize: size })
  const axisStroke = c.border

  return (
    <div className="animate-fade-up">
      <div className="panel-terminal mb-4">
        <div className="panel-header">
          <div className="flex items-center gap-3">
            <span className="dot dot-violet" />
            <span>module :: category.breakdown</span>
          </div>
          <div className="flex items-center gap-1">
            {buttons.map(({ mode, icon: Icon, label }) => {
              const active = view === mode
              return (
                <button
                  key={mode}
                  onClick={() => setView(mode)}
                  className={`flex items-center gap-1.5 rounded-sm px-2 py-1 text-[10px] uppercase tracking-[0.12em] transition-all ${
                    active
                      ? 'border border-[var(--neon-cyan)] bg-[rgba(var(--neon-cyan-rgb),0.10)] text-[var(--neon-cyan)]'
                      : 'text-[var(--text-muted)] hover:text-[var(--neon-cyan)]'
                  }`}
                  aria-label={label}
                >
                  <Icon size={11} />
                  {label}
                </button>
              )
            })}
          </div>
        </div>
      </div>

      {view === 'cards' && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 stagger">
          {categories.map((cat) => (
            <CategoryCard key={cat.category_id} category={cat} />
          ))}
        </div>
      )}

      {view === 'radar' && (
        <div className="panel-terminal glass-card">
          <div className="panel-body">
            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={chartData} outerRadius="70%">
                  <PolarGrid stroke={gridStroke} />
                  <PolarAngleAxis dataKey="shortName" tick={tick(11)} />
                  <PolarRadiusAxis domain={[0, maxPoints]} tick={tick(10)} />
                  <Radar
                    dataKey="remaining"
                    stroke={c.cyan}
                    fill={c.cyan}
                    fillOpacity={0.25}
                    strokeWidth={2}
                  />
                  <RTooltip contentStyle={tooltipStyle} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {view === 'bar' && (
        <div className="panel-terminal glass-card">
          <div className="panel-body">
            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} layout="vertical" margin={{ left: 20, right: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} horizontal={false} />
                  <XAxis type="number" domain={[0, maxPoints]} tick={tick(11)} stroke={axisStroke} />
                  <YAxis type="category" dataKey="shortName" tick={tick(11)} stroke={axisStroke} width={100} />
                  <RTooltip contentStyle={tooltipStyle} />
                  <Bar dataKey="remaining" radius={[0, 4, 4, 0]}>
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={barColor(entry.remaining, entry.total, c)} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
