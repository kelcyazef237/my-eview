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

export function TechnicalTable({ vectors }: TechnicalTableProps) {
  return (
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
            {vectors.map((vf) => (
              <tr key={vf.vector_key} className="transition-colors hover:bg-[var(--glass-bg)]">
                <td className="px-4 py-3 font-medium">{vf.vector_name}</td>
                <td className="px-4 py-3 text-[var(--text-secondary)]">{vf.category_key}</td>
                <td className="px-4 py-3">
                  <span className={stateBadgeClass(vf.state)}>
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
  )
}
