import { useEffect, useState } from 'react'
import { Building2, ChevronDown } from 'lucide-react'
import { api } from '@/api/client'
import type { AdminOrg } from '@/types'

interface OrgSelectorProps {
  orgId: string | undefined
  onSelect: (orgId: string) => void
}

export function OrgSelector({ orgId, onSelect }: OrgSelectorProps) {
  const [orgs, setOrgs] = useState<AdminOrg[] | null>(null)

  useEffect(() => {
    let alive = true
    api.admin
      .orgs({ limit: 500 })
      .then((page) => alive && setOrgs(page.items))
      .catch(() => alive && setOrgs(null))
    return () => {
      alive = false
    }
  }, [])

  if (!orgs || orgs.length === 0) return null

  return (
    <div className="relative inline-flex items-center">
      <Building2
        size={14}
        className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[var(--neon-cyan)]"
      />
      <select
        value={orgId ?? ''}
        onChange={(e) => onSelect(e.target.value)}
        className="glass-input appearance-none rounded-sm py-2 pl-9 pr-9 text-[12px] uppercase tracking-[0.12em] font-semibold transition-colors hover:bg-[rgba(var(--neon-cyan-rgb),0.06)]"
        style={{ fontFamily: 'var(--font-display)' }}
        title="Select organization"
      >
        {!orgId && <option value="">Auto · most.recent</option>}
        {orgs.map((o) => (
          <option key={o.id} value={o.id}>
            {o.domain}
          </option>
        ))}
      </select>
      <ChevronDown
        size={14}
        className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)]"
      />
    </div>
  )
}
