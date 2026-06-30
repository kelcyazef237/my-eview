import { Globe, Server, Brain } from 'lucide-react'
import type { EntityIntelligence as EntityIntelligenceData } from '@/types'

interface EntityIntelligenceProps {
  entity: EntityIntelligenceData
}

export function EntityIntelligence({ entity }: EntityIntelligenceProps) {
  return (
    <div className="animate-fade-up">
      <div className="panel-terminal mb-4">
        <div className="panel-header">
          <div className="flex items-center gap-2">
            <span className="dot dot-violet" />
            <span>module :: entity.intelligence</span>
          </div>
          <div className="flex items-center gap-2">
            <span>read.only</span>
            <span className="badge badge-neutral">not.scored</span>
          </div>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 stagger">
        <div className="panel glass-card-hover p-5">
          <div className="mb-3 flex items-center gap-2">
            <Globe size={16} className="text-[var(--neon-cyan)]" />
            <span className="display-title text-[12px] tracking-[0.08em] text-white">
              related.domains
            </span>
          </div>
          <div
            className="num text-3xl font-bold leading-none glitch"
            data-text={String(entity.related_domains.count)}
            style={{ color: 'var(--neon-cyan)', textShadow: '0 0 12px rgba(0,240,255,0.5)' }}
          >
            {entity.related_domains.count}
          </div>
          <div className="num mt-1 text-[10px] uppercase tracking-[0.14em] text-[var(--text-muted)]">
            ▸ discovered subdomains
          </div>
          {entity.related_domains.items.length > 0 && (
            <ul className="mt-4 max-h-32 space-y-1 overflow-y-auto rounded-sm border border-[var(--glass-border-subtle)] bg-black/30 p-2 num text-[12px] text-[var(--text-muted)]">
              {entity.related_domains.items.map((d) => (
                <li key={d} className="truncate">▸ {d}</li>
              ))}
            </ul>
          )}
        </div>

        <div className="panel glass-card-hover p-5">
          <div className="mb-3 flex items-center gap-2">
            <Server size={16} className="text-[var(--neon-violet)]" />
            <span className="display-title text-[12px] tracking-[0.08em] text-white">
              shared.infrastructure
            </span>
          </div>
          <div className="num text-[13px] text-[var(--text-secondary)]">
            <span className="text-[var(--text-muted)]">registrar ::</span>{' '}
            <span style={{ color: 'var(--neon-violet)' }} className="font-medium">
              {entity.shared_infrastructure.registrar || '—'}
            </span>
          </div>
          <div className="num mt-2 text-[13px] text-[var(--text-secondary)]">
            <span className="text-[var(--text-muted)]">name.servers ::</span>{' '}
            <span style={{ color: 'var(--neon-violet)' }} className="font-medium">
              {entity.shared_infrastructure.name_servers.length}
            </span>
          </div>
          {entity.shared_infrastructure.name_servers.length > 0 && (
            <ul className="mt-4 max-h-32 space-y-1 overflow-y-auto rounded-sm border border-[var(--glass-border-subtle)] bg-black/30 p-2 num text-[12px] text-[var(--text-muted)]">
              {entity.shared_infrastructure.name_servers.map((ns) => (
                <li key={ns} className="truncate">▸ {ns}</li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <div className="mt-3 flex items-center gap-1.5 num text-[11px] uppercase tracking-[0.12em] text-[var(--text-muted)]">
        <Brain size={12} className="text-[var(--neon-violet)]" />
        <span>{entity.label}</span>
      </div>
    </div>
  )
}
