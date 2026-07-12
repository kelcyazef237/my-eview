import { Brain, ChevronRight } from 'lucide-react'
import type { TiaEntry } from '@/types'

interface TIAPanelProps {
  tia: TiaEntry
}

const slotOrder = [
  'technical_observation',
  'business_impact',
  'stakeholders_affected',
  'regulatory_relevance',
  'recommended_action',
] as const

const slotLabels: Record<string, { label: string; color: string }> = {
  technical_observation: { label: 'technical.observation', color: 'var(--neon-cyan)' },
  business_impact:       { label: 'business.impact',       color: 'var(--neon-magenta)' },
  stakeholders_affected: { label: 'stakeholders.affected', color: 'var(--neon-violet)' },
  regulatory_relevance:  { label: 'regulatory.relevance',  color: 'var(--neon-amber)' },
  recommended_action:    { label: 'recommended.action',    color: 'var(--neon-green)' },
}

export function TIAPanel({ tia }: TIAPanelProps) {
  return (
    <div className="panel-terminal glass-card h-full">
      <div className="panel-header">
        <div className="flex items-center gap-2">
          <span className="dot dot-cyan" />
          <span>tia.report</span>
        </div>
        <span className="num text-[var(--neon-magenta)]">{tia.template_id}</span>
      </div>
      <div className="panel-body">
        <div className="mb-4 flex items-center gap-2">
          <Brain size={16} className="text-[var(--neon-cyan)]" />
          <h3 className="display-title text-[14px] tracking-[0.08em] text-[var(--text-primary)]">
            {tia.category_key}
          </h3>
        </div>

        <dl className="space-y-3">
          {slotOrder.map((slot) => {
            const value = tia.rendered_text[slot]
            if (!value) return null
            const isHtmlSlot = slot === 'business_impact' || slot === 'regulatory_relevance'
            const meta = slotLabels[slot]
            return (
              <div key={slot} className="border-l-2 pl-3" style={{ borderColor: meta.color }}>
                <dt
                  className="num mb-1 text-[10px] uppercase tracking-[0.14em]"
                  style={{ color: meta.color }}
                >
                  <ChevronRight size={10} className="mr-1 inline" />
                  {meta.label}
                </dt>
                <dd className="text-[13px] leading-relaxed text-[var(--text-secondary)]">
                  {Array.isArray(value) ? (
                    value.join(', ')
                  ) : isHtmlSlot && value.includes('<') ? (
                    <span dangerouslySetInnerHTML={{ __html: value }} />
                  ) : (
                    value
                  )}
                </dd>
              </div>
            )
          })}
        </dl>
      </div>
    </div>
  )
}
