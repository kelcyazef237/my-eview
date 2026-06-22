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

const slotLabels: Record<string, string> = {
  technical_observation: 'Technical Observation',
  business_impact: 'Business Impact',
  stakeholders_affected: 'Stakeholders Affected',
  regulatory_relevance: 'Regulatory Relevance',
  recommended_action: 'Recommended Action',
}

export function TIAPanel({ tia }: TIAPanelProps) {
  return (
    <div className="glass-card p-5">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-base font-semibold">{tia.category_key}</h3>
        <span className="font-mono text-xs text-[var(--text-muted)]">
          {tia.template_id}
        </span>
      </div>

      <dl className="space-y-4">
        {slotOrder.map((slot) => {
          const value = tia.rendered_text[slot]
          if (!value) return null
          const isHtmlSlot = slot === 'business_impact' || slot === 'regulatory_relevance'
          return (
            <div key={slot}>
              <dt className="section-title mb-1">{slotLabels[slot]}</dt>
              <dd className="text-sm leading-relaxed text-[var(--text-secondary)]">
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
  )
}
