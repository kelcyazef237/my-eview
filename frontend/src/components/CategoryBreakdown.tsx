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

interface CategoryBreakdownProps {
  categories: CategoryScore[]
  defaultView?: 'cards' | 'radar' | 'bar'
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

function barColor(remaining: number, total: number): string {
  const ratio = (total - remaining) / total
  if (ratio === 0) return '#22c55e'
  if (ratio < 0.3) return '#f59e0b'
  return '#ef4444'
}

export function CategoryBreakdown({ categories, defaultView = 'cards' }: CategoryBreakdownProps) {
  const [view, setView] = useState<'cards' | 'radar' | 'bar'>(defaultView)

  // Only scored categories (points_total > 0) for charts
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

  return (
    <div className="animate-slide-up">
      <div className="mb-4 flex items-center justify-between">
        <div className="section-title">Category Breakdown</div>
        <div className="flex gap-1">
          {buttons.map(({ mode, icon: Icon, label }) => (
            <button
              key={mode}
              onClick={() => setView(mode)}
              className={`flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-medium transition-colors ${
                view === mode
                  ? 'bg-[var(--accent)] text-white'
                  : 'text-[var(--text-secondary)] hover:bg-[var(--glass-bg)]'
              }`}
              aria-label={label}
            >
              <Icon size={14} />
              <span className="hidden sm:inline">{label}</span>
            </button>
          ))}
        </div>
      </div>

      {view === 'cards' && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {categories.map((cat) => (
            <CategoryCard key={cat.category_id} category={cat} />
          ))}
        </div>
      )}

      {view === 'radar' && (
        <div className="glass-card p-5">
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={chartData} outerRadius="70%">
                <PolarGrid stroke="var(--border-color)" />
                <PolarAngleAxis dataKey="shortName" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
                <PolarRadiusAxis domain={[0, maxPoints]} tick={{ fill: 'var(--text-muted)', fontSize: 10 }} />
                <Radar dataKey="remaining" stroke="var(--accent)" fill="var(--accent)" fillOpacity={0.3} strokeWidth={2} />
                <RTooltip contentStyle={tooltipStyle} itemStyle={{ color: 'var(--text-primary)' }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {view === 'bar' && (
        <div className="glass-card p-5">
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} layout="vertical" margin={{ left: 20, right: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" horizontal={false} />
                <XAxis type="number" domain={[0, maxPoints]} tick={{ fill: 'var(--text-muted)', fontSize: 11 }} stroke="var(--border-color)" />
                <YAxis type="category" dataKey="shortName" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} stroke="var(--border-color)" width={100} />
                <RTooltip contentStyle={tooltipStyle} itemStyle={{ color: 'var(--text-primary)' }} />
                <Bar dataKey="remaining" radius={[0, 4, 4, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={barColor(entry.remaining, entry.total)} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  )
}