import type { VectorFinding } from '@/types'

interface TechnicalTableProps {
  vectors: VectorFinding[]
}

function stateBadge(state: string): string {
  switch (state) {
    case 'PASS':
      return 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400'
    case 'WARN':
      return 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400'
    case 'FAIL':
      return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
    case 'NOT_APPLICABLE':
      return 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400'
    case 'NOT_OBSERVED':
    default:
      return 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
  }
}

export function TechnicalTable({ vectors }: TechnicalTableProps) {
  return (
    <div className="card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-[var(--bg-secondary)]">
            <tr>
              <th className="px-4 py-3 font-mono text-xs font-semibold text-[var(--text-muted)]">Vector</th>
              <th className="px-4 py-3 font-mono text-xs font-semibold text-[var(--text-muted)]">Category</th>
              <th className="px-4 py-3 font-mono text-xs font-semibold text-[var(--text-muted)]">State</th>
              <th className="px-4 py-3 font-mono text-xs font-semibold text-[var(--text-muted)]">Evidence</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--border-color)]">
            {vectors.map((vf) => (
              <tr key={vf.vector_key} className="hover:bg-[var(--bg-secondary)]/50">
                <td className="px-4 py-3 font-medium">{vf.vector_name}</td>
                <td className="px-4 py-3 text-[var(--text-secondary)]">{vf.category_key}</td>
                <td className="px-4 py-3">
                  <span
                    className={`inline-flex rounded-full px-2 py-0.5 text-xs font-semibold ${stateBadge(vf.state)}`}
                  >
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
