import { useEffect, useState } from 'react'
import { Building2, ChevronDown } from 'lucide-react'
import { api } from '@/api/client'
import type { AdminOrg } from '@/types'

interface OrgSelectorProps {
  /** Currently selected org id (from ?org_id=), or undefined for "auto". */
  orgId: string | undefined
  /** Called when the user picks a different org. */
  onSelect: (orgId: string) => void
}

/**
 * Organization switcher dropdown.
 *
 * Fetches the org list via the admin endpoint. Only users who can call that
 * endpoint (global_admin / ops) see the selector; for regular owners the
 * component renders nothing and the page falls back to its default org.
 */
export function OrgSelector({ orgId, onSelect }: OrgSelectorProps) {
  const [orgs, setOrgs] = useState<AdminOrg[] | null>(null)

  useEffect(() => {
    let alive = true
    api
      .admin
      .orgs()
      .then((list) => alive && setOrgs(list))
      .catch(() => alive && setOrgs(null))
    return () => {
      alive = false
    }
  }, [])

  // No list (forbidden / fetch failed) → hide the selector entirely.
  if (!orgs || orgs.length === 0) return null

  return (
    <div className="relative inline-flex items-center">
      <Building2
        size={16}
        className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)]"
      />
      <select
        value={orgId ?? ''}
        onChange={(e) => onSelect(e.target.value)}
        className="glass-input appearance-none rounded-lg py-2 pl-9 pr-9 text-sm font-medium transition-colors hover:bg-[var(--glass-bg)]"
        title="Select organization"
      >
        {!orgId && <option value="">Auto (most recent)</option>}
        {orgs.map((o) => (
          <option key={o.id} value={o.id}>
            {o.domain}
          </option>
        ))}
      </select>
      <ChevronDown
        size={15}
        className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)]"
      />
    </div>
  )
}