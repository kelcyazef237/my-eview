import { Globe, Server, Brain, Info } from 'lucide-react'
import type { EntityIntelligence as EntityIntelligenceData } from '@/types'

interface EntityIntelligenceProps {
  entity: EntityIntelligenceData
}

export function EntityIntelligence({ entity }: EntityIntelligenceProps) {
  return (
    <div className="animate-slide-up">
      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--accent)]/10 text-[var(--accent)]">
          <Brain size={18} />
        </div>
        <div className="section-title">Entity Intelligence</div>
        <span className="badge badge-neutral">Not Scored</span>
      </div>

      <div className="glass-card grid gap-4 p-5 sm:grid-cols-2">
        {/* Related Domains */}
        <div className="rounded-xl bg-[var(--glass-bg)] p-4">
          <div className="mb-3 flex items-center gap-2">
            <Globe size={18} className="text-[var(--accent)]" />
            <span className="text-sm font-semibold">Related Domains</span>
          </div>
          <div className="text-2xl font-bold">{entity.related_domains.count}</div>
          <div className="text-xs text-[var(--text-muted)]">discovered subdomains</div>
          {entity.related_domains.items.length > 0 && (
            <ul className="mt-3 max-h-28 space-y-1 overflow-y-auto font-mono text-xs text-[var(--text-muted)]">
              {entity.related_domains.items.map((d) => (
                <li key={d} className="truncate">{d}</li>
              ))}
            </ul>
          )}
        </div>

        {/* Shared Infrastructure */}
        <div className="rounded-xl bg-[var(--glass-bg)] p-4">
          <div className="mb-3 flex items-center gap-2">
            <Server size={18} className="text-[var(--accent)]" />
            <span className="text-sm font-semibold">Shared Infrastructure</span>
          </div>
          <div className="text-sm text-[var(--text-secondary)]">
            <span className="text-[var(--text-muted)]">Registrar: </span>
            <span className="font-medium">{entity.shared_infrastructure.registrar || '—'}</span>
          </div>
          <div className="mt-2 text-sm text-[var(--text-secondary)]">
            <span className="text-[var(--text-muted)]">Name servers: </span>
            <span className="font-medium">{entity.shared_infrastructure.name_servers.length}</span>
          </div>
          {entity.shared_infrastructure.name_servers.length > 0 && (
            <ul className="mt-3 max-h-28 space-y-1 overflow-y-auto font-mono text-xs text-[var(--text-muted)]">
              {entity.shared_infrastructure.name_servers.map((ns) => (
                <li key={ns} className="truncate">{ns}</li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <div className="mt-2 flex items-center gap-1.5 text-xs text-[var(--text-muted)]">
        <Info size={12} />
        <span>{entity.label}</span>
      </div>
    </div>
  )
}