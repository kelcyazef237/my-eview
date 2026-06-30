import { CheckCircle2, AlertTriangle, XCircle, MinusCircle } from 'lucide-react'
import type { VectorFinding } from '@/types'

interface TechnicalTableProps {
  vectors: VectorFinding[]
}

function stateBadgeClass(state: string): string {
  switch (state) {
    case 'PASS':  return 'badge badge-pass'
    case 'WARN':  return 'badge badge-warn'
    case 'FAIL':  return 'badge badge-fail'
    default:      return 'badge badge-neutral'
  }
}

function StateIcon({ state }: { state: string }) {
  switch (state) {
    case 'PASS':  return <CheckCircle2 size={11} />
    case 'WARN':  return <AlertTriangle size={11} />
    case 'FAIL':  return <XCircle size={11} />
    default:      return <MinusCircle size={11} />
  }
}

const STATE_COLOR: Record<string, string> = {
  PASS: 'var(--neon-green)',
  WARN: 'var(--neon-amber)',
  FAIL: 'var(--neon-red)',
}

export function TechnicalTable({ vectors }: TechnicalTableProps) {
  const counts = vectors.reduce(
    (acc, v) => {
      if (v.state === 'PASS') acc.pass++
      else if (v.state === 'WARN') acc.warn++
      else if (v.state === 'FAIL') acc.fail++
      else acc.other++
      return acc
    },
    { pass: 0, warn: 0, fail: 0, other: 0 },
  )

  const summaryPills = [
    { label: 'PASS', count: counts.pass, icon: CheckCircle2, className: 'badge badge-pass', color: 'var(--neon-green)' },
    { label: 'WARN', count: counts.warn, icon: AlertTriangle, className: 'badge badge-warn', color: 'var(--neon-amber)' },
    { label: 'FAIL', count: counts.fail, icon: XCircle, className: 'badge badge-fail', color: 'var(--neon-red)' },
    { label: 'N/A',  count: counts.other, icon: MinusCircle, className: 'badge badge-neutral', color: 'var(--text-secondary)' },
  ]

  return (
    <div className="animate-fade-up">
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <span className="eyebrow mr-1">
          <span className="line" />
          <span>summary</span>
        </span>
        {summaryPills.map(({ label, count, icon: Icon, color }) => (
          <span
            key={label}
            className="badge"
            style={{
              borderColor: color,
              color,
              background: 'rgba(0,0,0,0.3)',
              boxShadow: `inset 0 0 12px ${color}25, 0 0 8px ${color}30`,
            }}
          >
            <Icon size={11} />
            {label} :: <span className="num">{count}</span>
          </span>
        ))}
        <span className="ml-auto num text-[11px] uppercase tracking-[0.12em] text-[var(--text-muted)]">
          ▸ {vectors.length} vectors scanned
        </span>
      </div>

      <div className="panel-terminal glass-card">
        <div className="panel-header">
          <div className="flex items-center gap-2">
            <span className="dot dot-cyan" />
            <span>module :: technical.drill-down</span>
          </div>
          <span>28 vectors</span>
        </div>
        <div className="overflow-x-auto">
          <table className="hud-table">
            <thead>
              <tr>
                <th>vector</th>
                <th>category</th>
                <th>state</th>
                <th>evidence</th>
              </tr>
            </thead>
            <tbody>
              {vectors.map((vf) => (
                <tr key={vf.vector_key}>
                  <td className="font-medium text-white">{vf.vector_name}</td>
                  <td className="num text-[var(--text-secondary)]">{vf.category_key}</td>
                  <td>
                    <span
                      className={stateBadgeClass(vf.state)}
                      style={{
                        color: STATE_COLOR[vf.state] || 'var(--text-secondary)',
                        borderColor: STATE_COLOR[vf.state] || 'var(--text-secondary)',
                      }}
                    >
                      <StateIcon state={vf.state} />
                      {vf.state}
                    </span>
                  </td>
                  <td className="mono text-[var(--text-muted)]">{vf.evidence_ref || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
