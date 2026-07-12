import { useState } from 'react'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'
import { LineChart as LineChartIcon, AreaChart as AreaChartIcon, BarChart3 } from 'lucide-react'
import { useThemeColors } from '@/hooks/useThemeColors'

interface Point {
  computed_at: string
  overall_score: number
  is_full_report: boolean
}

interface ScoreHistoryChartProps {
  data: Point[]
}

type ViewMode = 'line' | 'area' | 'bar'

function scoreColor(score: number, c: { violet: string; green: string; cyan: string; amber: string; red: string }): string {
  if (score >= 900) return c.violet
  if (score >= 750) return c.green
  if (score >= 600) return c.cyan
  if (score >= 400) return c.amber
  return c.red
}

export function ScoreHistoryChart({ data }: ScoreHistoryChartProps) {
  const [view, setView] = useState<ViewMode>('line')
  const c = useThemeColors()

  const sorted = [...data].sort(
    (a, b) => new Date(a.computed_at).getTime() - new Date(b.computed_at).getTime(),
  )

  const chartData = sorted.map((p) => ({
    date: new Date(p.computed_at).toLocaleDateString(),
    score: p.overall_score,
    full: p.is_full_report,
  }))

  const buttons: { mode: ViewMode; icon: typeof LineChartIcon; label: string }[] = [
    { mode: 'line', icon: LineChartIcon, label: 'Line' },
    { mode: 'area', icon: AreaChartIcon, label: 'Area' },
    { mode: 'bar', icon: BarChart3, label: 'Bars' },
  ]

  const tooltipStyle = {
    backgroundColor: c.bgElevated,
    border: `1px solid ${c.border}`,
    borderRadius: 6,
    color: c.textPrimary,
    boxShadow: '0 8px 24px rgba(15,23,42,0.10)',
    fontFamily: 'var(--font-mono)',
    fontSize: 12,
  } as const

  const gridStroke = `${c.cyan}1a`
  const tick = { fill: c.textMuted, fontSize: 12 }
  const axisStroke = c.border

  return (
    <div className="panel-terminal glass-card animate-fade-up">
      <div className="panel-header">
        <div className="flex items-center gap-2">
          <span className="dot dot-cyan" />
          <span>module :: score.history</span>
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
      <div className="panel-body">
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            {view === 'line' ? (
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} />
                <XAxis dataKey="date" tick={tick} stroke={axisStroke} />
                <YAxis domain={[0, 1000]} tick={tick} stroke={axisStroke} />
                <Tooltip contentStyle={tooltipStyle} />
                <ReferenceLine y={900} stroke={c.violet} strokeDasharray="4 4" />
                <ReferenceLine y={750} stroke={c.green} strokeDasharray="4 4" />
                <ReferenceLine y={600} stroke={c.cyan} strokeDasharray="4 4" />
                <ReferenceLine y={400} stroke={c.amber} strokeDasharray="4 4" />
                <Line type="monotone" dataKey="score" stroke={c.cyan} strokeWidth={2.5} dot={{ r: 4, fill: c.cyan, stroke: c.violet, strokeWidth: 1 }} activeDot={{ r: 6, fill: c.magenta }} />
              </LineChart>
            ) : view === 'area' ? (
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={c.cyan} stopOpacity={0.55} />
                    <stop offset="100%" stopColor={c.cyan} stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} />
                <XAxis dataKey="date" tick={tick} stroke={axisStroke} />
                <YAxis domain={[0, 1000]} tick={tick} stroke={axisStroke} />
                <Tooltip contentStyle={tooltipStyle} />
                <ReferenceLine y={900} stroke={c.violet} strokeDasharray="4 4" />
                <ReferenceLine y={750} stroke={c.green} strokeDasharray="4 4" />
                <ReferenceLine y={600} stroke={c.cyan} strokeDasharray="4 4" />
                <ReferenceLine y={400} stroke={c.amber} strokeDasharray="4 4" />
                <Area type="monotone" dataKey="score" stroke={c.cyan} fill="url(#scoreGradient)" strokeWidth={2.5} dot={{ r: 4, fill: c.cyan }} activeDot={{ r: 6, fill: c.magenta }} />
              </AreaChart>
            ) : (
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} />
                <XAxis dataKey="date" tick={tick} stroke={axisStroke} />
                <YAxis domain={[0, 1000]} tick={tick} stroke={axisStroke} />
                <Tooltip contentStyle={tooltipStyle} />
                <ReferenceLine y={900} stroke={c.violet} strokeDasharray="4 4" />
                <ReferenceLine y={750} stroke={c.green} strokeDasharray="4 4" />
                <ReferenceLine y={600} stroke={c.cyan} strokeDasharray="4 4" />
                <ReferenceLine y={400} stroke={c.amber} strokeDasharray="4 4" />
                <Bar dataKey="score" radius={[4, 4, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={scoreColor(entry.score, c)} />
                  ))}
                </Bar>
              </BarChart>
            )}
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
