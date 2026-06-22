import { CheckCircle2, AlertTriangle, XCircle, MinusCircle } from 'lucide-react'
import type { VectorFinding } from '@/types'

interface TechnicalTableProps {
  vectors: VectorFinding[]
}

function stateBadgeClass(state: string): string {
  switch (state) {
    case 'PASS':
      return 'badge badge-pass'
    case 'WARN':
      return 'badge badge-warn'
    case 'FAIL':
      return 'badge badge-fail'
    case 'NOT_APPLICABLE':
      return 'badge badge-neutral'
    case 'NOT_OBSERVED':
    default:
      return 'badge badge-neutral'
  }
}

function StateIcon({ state }: { state: string }) {
  switch (state) {
    case 'PASS':
      return <CheckCircle2 size={12} />
    case 'WARN':
      return <AlertTriangle size={12} />
    case 'FAIL':
      return <XCircle size={12} />
    default:
      return <MinusCircle size={12} />
  }
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
    { label: 'PASS', count: counts.pass, icon: CheckCircle2, className: 'badge badge-pass' },
    { label: 'WARN', count: counts.warn, icon: AlertTriangle, className: 'badge badge-warn' },
    { label: 'FAIL', count: counts.fail, icon: XCircle, className: 'badge badge-fail' },
    { label: 'N/A', count: counts.other, icon: MinusCircle, className: 'badge badge-neutral' },
  ]

  return (
    <div className="animate-slide-up">
      {/* Summary bar */}
      <div className="mb-3 flex flex-wrap gap-2">
        {summaryPills.map(({ label, count, icon: Icon, className }) => (
          <span key={label} className={className}>
            <Icon size={12} />
            {label}: {count}
          </span>
        ))}
      </div>

      <div className="glass-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-[var(--glass-bg)]">
              <tr>
                <th className="px-4 py-3 font-mono text-xs font-semibold text-[var(--text-muted)]">Vector</th>
                <th className="px-4 py-3 font-mono text-xs font-semibold text-[var(--text-muted)]">Category</th>
                <th className="px-4 py-3 font-mono text-xs font-semibold text-[var(--text-muted)]">State</th>
                <th className="px-4 py-3 font-mono text-xs font-semibold text-[var(--text-muted)]">Evidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--glass-border-subtle)]">
              {vectors.map((vf, idx) => (
                <tr
                  key={vf.vector_key}
                  className={`transition-colors hover:bg-[var(--accent)]/5 ${
                    idx % 2 === 1 ? 'bg-[var(--glass-bg)]' : ''
                  }`}
                >
                  <td className="px-4 py-3 font-medium">{vf.vector_name}</td>
                  <td className="px-4 py-3 text-[var(--text-secondary)]">{vf.category_key}</td>
                  <td className="px-4 py-3">
                    <span className={stateBadgeClass(vf.state)}>
                      <StateIcon state={vf.state} />
                      {vf.state}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-[var(--text-muted)]">
                    {vf.evidence_ref || '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}