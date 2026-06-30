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

function scoreColor(score: number): string {
  if (score >= 900) return '#b400ff'
  if (score >= 750) return '#00ff9c'
  if (score >= 600) return '#00f0ff'
  if (score >= 400) return '#ffb020'
  return '#ff3060'
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

  const tooltipStyle = {
    backgroundColor: '#0c1126',
    border: '1px solid #00f0ff',
    borderRadius: 3,
    color: '#e6f2ff',
    fontFamily: 'var(--font-mono)',
    fontSize: 12,
  } as const

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
                    ? 'border border-[var(--neon-cyan)] bg-[rgba(0,240,255,0.1)] text-[var(--neon-cyan)]'
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
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,240,255,0.08)" />
                <XAxis dataKey="date" tick={{ fill: '#8a9fc4', fontSize: 12 }} stroke="#1a2342" />
                <YAxis domain={[0, 1000]} tick={{ fill: '#8a9fc4', fontSize: 12 }} stroke="#1a2342" />
                <Tooltip contentStyle={tooltipStyle} />
                <ReferenceLine y={900} stroke="#b400ff" strokeDasharray="4 4" />
                <ReferenceLine y={750} stroke="#00ff9c" strokeDasharray="4 4" />
                <ReferenceLine y={600} stroke="#00f0ff" strokeDasharray="4 4" />
                <ReferenceLine y={400} stroke="#ffb020" strokeDasharray="4 4" />
                <Line type="monotone" dataKey="score" stroke="#00f0ff" strokeWidth={2.5} dot={{ r: 4, fill: '#00f0ff', stroke: '#b400ff', strokeWidth: 1 }} activeDot={{ r: 6, fill: '#ff00d4' }} />
              </LineChart>
            ) : view === 'area' ? (
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#00f0ff" stopOpacity={0.55} />
                    <stop offset="100%" stopColor="#00f0ff" stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,240,255,0.08)" />
                <XAxis dataKey="date" tick={{ fill: '#8a9fc4', fontSize: 12 }} stroke="#1a2342" />
                <YAxis domain={[0, 1000]} tick={{ fill: '#8a9fc4', fontSize: 12 }} stroke="#1a2342" />
                <Tooltip contentStyle={tooltipStyle} />
                <ReferenceLine y={900} stroke="#b400ff" strokeDasharray="4 4" />
                <ReferenceLine y={750} stroke="#00ff9c" strokeDasharray="4 4" />
                <ReferenceLine y={600} stroke="#00f0ff" strokeDasharray="4 4" />
                <ReferenceLine y={400} stroke="#ffb020" strokeDasharray="4 4" />
                <Area type="monotone" dataKey="score" stroke="#00f0ff" fill="url(#scoreGradient)" strokeWidth={2.5} dot={{ r: 4, fill: '#00f0ff' }} activeDot={{ r: 6, fill: '#ff00d4' }} />
              </AreaChart>
            ) : (
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,240,255,0.08)" />
                <XAxis dataKey="date" tick={{ fill: '#8a9fc4', fontSize: 12 }} stroke="#1a2342" />
                <YAxis domain={[0, 1000]} tick={{ fill: '#8a9fc4', fontSize: 12 }} stroke="#1a2342" />
                <Tooltip contentStyle={tooltipStyle} />
                <ReferenceLine y={900} stroke="#b400ff" strokeDasharray="4 4" />
                <ReferenceLine y={750} stroke="#00ff9c" strokeDasharray="4 4" />
                <ReferenceLine y={600} stroke="#00f0ff" strokeDasharray="4 4" />
                <ReferenceLine y={400} stroke="#ffb020" strokeDasharray="4 4" />
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
    </div>
  )
}
