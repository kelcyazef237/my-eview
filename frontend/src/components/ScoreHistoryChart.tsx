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

interface Point {
  computed_at: string
  overall_score: number
  is_full_report: boolean
}

interface ScoreHistoryChartProps {
  data: Point[]
}

type ViewMode = 'line' | 'area' | 'bar'

const tooltipStyle = {
  backgroundColor: 'var(--bg-elevated)',
  border: '1px solid var(--border-color)',
  borderRadius: '0.5rem',
} as const

function scoreColor(score: number): string {
  if (score >= 900) return '#1d5c3f'
  if (score >= 750) return '#2e8a7a'
  if (score >= 600) return '#3b6e91'
  if (score >= 400) return '#c67a2e'
  return '#9f4a4a'
}

export function ScoreHistoryChart({ data }: ScoreHistoryChartProps) {
  const [view, setView] = useState<ViewMode>('line')

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

  return (
    <div className="glass-card p-5 animate-slide-up">
      <div className="mb-4 flex items-center justify-between">
        <div className="section-title">Score History</div>
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
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          {view === 'line' ? (
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
              <XAxis dataKey="date" tick={{ fill: 'var(--text-muted)', fontSize: 12 }} stroke="var(--border-color)" />
              <YAxis domain={[0, 1000]} tick={{ fill: 'var(--text-muted)', fontSize: 12 }} stroke="var(--border-color)" />
              <Tooltip contentStyle={tooltipStyle} itemStyle={{ color: 'var(--text-primary)' }} />
              <ReferenceLine y={900} stroke="#1d5c3f" strokeDasharray="4 4" />
              <ReferenceLine y={750} stroke="#2e8a7a" strokeDasharray="4 4" />
              <ReferenceLine y={600} stroke="#3b6e91" strokeDasharray="4 4" />
              <ReferenceLine y={400} stroke="#c67a2e" strokeDasharray="4 4" />
              <Line type="monotone" dataKey="score" stroke="var(--accent)" strokeWidth={2} dot={{ r: 4, fill: 'var(--accent)' }} activeDot={{ r: 6 }} />
            </LineChart>
          ) : view === 'area' ? (
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="var(--accent)" stopOpacity={0.4} />
                  <stop offset="100%" stopColor="var(--accent)" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
              <XAxis dataKey="date" tick={{ fill: 'var(--text-muted)', fontSize: 12 }} stroke="var(--border-color)" />
              <YAxis domain={[0, 1000]} tick={{ fill: 'var(--text-muted)', fontSize: 12 }} stroke="var(--border-color)" />
              <Tooltip contentStyle={tooltipStyle} itemStyle={{ color: 'var(--text-primary)' }} />
              <ReferenceLine y={900} stroke="#1d5c3f" strokeDasharray="4 4" />
              <ReferenceLine y={750} stroke="#2e8a7a" strokeDasharray="4 4" />
              <ReferenceLine y={600} stroke="#3b6e91" strokeDasharray="4 4" />
              <ReferenceLine y={400} stroke="#c67a2e" strokeDasharray="4 4" />
              <Area type="monotone" dataKey="score" stroke="var(--accent)" fill="url(#scoreGradient)" strokeWidth={2} dot={{ r: 4, fill: 'var(--accent)' }} activeDot={{ r: 6 }} />
            </AreaChart>
          ) : (
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
              <XAxis dataKey="date" tick={{ fill: 'var(--text-muted)', fontSize: 12 }} stroke="var(--border-color)" />
              <YAxis domain={[0, 1000]} tick={{ fill: 'var(--text-muted)', fontSize: 12 }} stroke="var(--border-color)" />
              <Tooltip contentStyle={tooltipStyle} itemStyle={{ color: 'var(--text-primary)' }} />
              <ReferenceLine y={900} stroke="#1d5c3f" strokeDasharray="4 4" />
              <ReferenceLine y={750} stroke="#2e8a7a" strokeDasharray="4 4" />
              <ReferenceLine y={600} stroke="#3b6e91" strokeDasharray="4 4" />
              <ReferenceLine y={400} stroke="#c67a2e" strokeDasharray="4 4" />
              <Bar dataKey="score" radius={[4, 4, 0, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={scoreColor(entry.score)} />
                ))}
              </Bar>
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  )
}