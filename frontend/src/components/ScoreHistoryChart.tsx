import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'

interface Point {
  computed_at: string
  overall_score: number
  is_full_report: boolean
}

interface ScoreHistoryChartProps {
  data: Point[]
}

export function ScoreHistoryChart({ data }: ScoreHistoryChartProps) {
  const sorted = [...data].sort(
    (a, b) => new Date(a.computed_at).getTime() - new Date(b.computed_at).getTime(),
  )

  const chartData = sorted.map((p) => ({
    date: new Date(p.computed_at).toLocaleDateString(),
    score: p.overall_score,
    full: p.is_full_report,
  }))

  return (
    <div className="card p-5">
      <div className="section-title mb-4">Score History</div>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
            <XAxis
              dataKey="date"
              tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
              stroke="var(--border-color)"
            />
            <YAxis
              domain={[0, 1000]}
              tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
              stroke="var(--border-color)"
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'var(--bg-elevated)',
                border: '1px solid var(--border-color)',
                borderRadius: '0.5rem',
              }}
              itemStyle={{ color: 'var(--text-primary)' }}
            />
            <ReferenceLine y={900} stroke="#1d5c3f" strokeDasharray="4 4" />
            <ReferenceLine y={750} stroke="#2e8a7a" strokeDasharray="4 4" />
            <ReferenceLine y={600} stroke="#3b6e91" strokeDasharray="4 4" />
            <ReferenceLine y={400} stroke="#c67a2e" strokeDasharray="4 4" />
            <Line
              type="monotone"
              dataKey="score"
              stroke="var(--accent)"
              strokeWidth={2}
              dot={{ r: 4, fill: 'var(--accent)' }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
