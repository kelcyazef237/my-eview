import { useCallback, useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Building2,
  Users,
  Activity,
  UserCheck,
  Check,
  X,
  Loader2,
  RefreshCw,
  ShieldCheck,
  ShieldAlert,
  Ban,
  Power,
  Trash2,
  Pencil,
  Radar,
  Sparkles,
  FileText,
  Download,
} from 'lucide-react'
import { api } from '@/api/client'
import { AdminChartSystem } from '@/components/AdminChartSystem'
import type {
  AdminMetrics,
  AdminOrg,
  AdminScanRun,
  AdminUser,
  PendingRegistration,
} from '@/types'

const ROLE_OPTIONS = [
  { value: 'owner', label: 'Owner' },
  { value: 'owner_technical', label: 'Owner / Technical' },
  { value: 'ops', label: 'Ops' },
]

const STATUS_BADGE: Record<string, string> = {
  approved: 'badge badge-pass',
  pending: 'badge badge-warn',
  rejected: 'badge badge-fail',
  active: 'badge badge-pass',
}

function MetricTile({
  icon: Icon,
  label,
  value,
  color,
}: {
  icon: React.ElementType
  label: string
  value: number
  color: string
}) {
  return (
    <div className="panel glass-card-hover p-5">
      <div className="absolute inset-x-0 top-0 h-px" style={{ background: `linear-gradient(90deg, transparent, ${color}, transparent)` }} />
      <div className="flex items-center justify-between">
        <div>
          <p className="eyebrow">{label}</p>
          <p className="num mt-2 text-3xl font-bold glitch" data-text={String(value)} style={{ color, textShadow: `0 0 12px ${color}80` }}>
            {value}
          </p>
        </div>
        <div
          className="flex h-12 w-12 items-center justify-center rounded-sm"
          style={{
            border: `1px solid ${color}`,
            background: `${color}15`,
            color,
            boxShadow: `0 0 16px ${color}55`,
          }}
        >
          <Icon size={22} />
        </div>
      </div>
    </div>
  )
}

export function AdminDashboard() {
  const navigate = useNavigate()
  const [metrics, setMetrics] = useState<AdminMetrics | null>(null)
  const [pending, setPending] = useState<PendingRegistration[]>([])
  const [users, setUsers] = useState<AdminUser[]>([])
  const [orgs, setOrgs] = useState<AdminOrg[]>([])
  const [orgTotal, setOrgTotal] = useState(0)
  const [orgQuery, setOrgQuery] = useState('')
  const [orgSearch, setOrgSearch] = useState('')
  const [orgLoading, setOrgLoading] = useState(false)
  const [showAllOrgs, setShowAllOrgs] = useState(false)
  const ORG_LIMIT = 5
  const ORG_LIMIT_ALL = 100
  const searchDebounce = useRef<ReturnType<typeof setTimeout> | null>(null)
  const [scanRuns, setScanRuns] = useState<AdminScanRun[]>([])
  const [showAllScans, setShowAllScans] = useState(false)
  const [loading, setLoading] = useState(true)
  const [actionError, setActionError] = useState('')
  const [busyId, setBusyId] = useState<string | null>(null)
  const [selectedRoles, setSelectedRoles] = useState<Record<string, string>>({})
  const [rescanning, setRescanning] = useState<string | null>(null)
  const [editingUser, setEditingUser] = useState<AdminUser | null>(null)
  const [editForm, setEditForm] = useState({ full_name: '', username: '', email: '' })

  const refreshAll = useCallback(async () => {
    try {
      const [m, p, u, s] = await Promise.all([
        api.admin.metrics(),
        api.admin.registrations(),
        api.admin.users(),
        api.admin.scanRuns(),
      ])
      setMetrics(m)
      setPending(p)
      setUsers(u)
      setScanRuns(s)
      const defaults: Record<string, string> = {}
      for (const reg of p) defaults[reg.id] = 'owner'
      setSelectedRoles(defaults)
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Failed to load admin data')
    } finally {
      setLoading(false)
    }
  }, [])

  const fetchOrgs = useCallback(
    async (q: string, offset: number, append: boolean, limit?: number) => {
      setOrgLoading(true)
      try {
        const page = await api.admin.orgs({ q: q || undefined, limit: limit ?? ORG_LIMIT, offset })
        setOrgs((prev) => (append ? [...prev, ...page.items] : page.items))
        setOrgTotal(page.total)
      } catch (err) {
        setActionError(err instanceof Error ? err.message : 'Failed to load organizations')
      } finally {
        setOrgLoading(false)
      }
    },
    [],
  )

  // Initial load + debounced search.
  useEffect(() => {
    refreshAll()
    fetchOrgs('', 0, false)
  }, [refreshAll, fetchOrgs])

  const handleToggleAllOrgs = () => {
    if (showAllOrgs) {
      setShowAllOrgs(false)
      fetchOrgs(orgSearch, 0, false, ORG_LIMIT)
    } else {
      setShowAllOrgs(true)
      fetchOrgs(orgSearch, 0, false, ORG_LIMIT_ALL)
    }
  }

  useEffect(() => {
    if (searchDebounce.current) clearTimeout(searchDebounce.current)
    searchDebounce.current = setTimeout(() => {
      setOrgSearch(orgQuery)
      setShowAllOrgs(false)
      fetchOrgs(orgQuery, 0, false, ORG_LIMIT)
    }, 300)
    return () => {
      if (searchDebounce.current) clearTimeout(searchDebounce.current)
    }
  }, [orgQuery, fetchOrgs])

  useEffect(() => {
    refreshAll()
  }, [refreshAll])

  const handleApprove = async (userId: string) => {
    const role = selectedRoles[userId] || 'owner'
    setBusyId(userId)
    setActionError('')
    try {
      await api.admin.approve(userId, role)
      await refreshAll()
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Approval failed')
    } finally {
      setBusyId(null)
    }
  }

  const handleReject = async (userId: string) => {
    setBusyId(userId)
    setActionError('')
    try {
      await api.admin.reject(userId)
      await refreshAll()
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Rejection failed')
    } finally {
      setBusyId(null)
    }
  }

  const handleToggleActive = async (userId: string, currentActive: boolean) => {
    setBusyId(userId)
    setActionError('')
    try {
      await api.admin.updateUser(userId, { is_active: !currentActive })
      await refreshAll()
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Update failed')
    } finally {
      setBusyId(null)
    }
  }

  const handleRoleChange = async (userId: string, role: string) => {
    setBusyId(userId)
    setActionError('')
    try {
      await api.admin.updateUser(userId, { role })
      await refreshAll()
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Role change failed')
    } finally {
      setBusyId(null)
    }
  }

  const handleDeleteUser = async (userId: string, name: string) => {
    if (!confirm(`Delete user "${name}"? This cannot be undone.`)) return
    setBusyId(userId)
    setActionError('')
    try {
      await api.admin.deleteUser(userId)
      await refreshAll()
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Delete failed')
    } finally {
      setBusyId(null)
    }
  }

  const startEdit = (u: AdminUser) => {
    setEditingUser(u)
    setEditForm({
      full_name: u.full_name || '',
      username: u.username || '',
      email: u.email || '',
    })
  }

  const handleSaveEdit = async () => {
    if (!editingUser) return
    setBusyId(editingUser.id)
    setActionError('')
    try {
      await api.admin.updateUser(editingUser.id, editForm)
      setEditingUser(null)
      await refreshAll()
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Edit failed')
    } finally {
      setBusyId(null)
    }
  }

  const handleRescan = async (orgId: string) => {
    setRescanning(orgId)
    setActionError('')
    try {
      await api.admin.rescan(orgId)
      await refreshAll()
      await fetchOrgs(orgSearch, 0, false)
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Rescan failed')
    } finally {
      setRescanning(null)
    }
  }

  const handleTogglePortscan = async (orgId: string, current: boolean) => {
    setBusyId(orgId)
    setActionError('')
    try {
      await api.admin.authorizePortscan(orgId, !current)
      await refreshAll()
      await fetchOrgs(orgSearch, 0, false)
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Port scan auth failed')
    } finally {
      setBusyId(null)
    }
  }

  const [aiGenerating, setAiGenerating] = useState<string | null>(null)
  const handleGenerateAI = async (scanRunId: string, orgId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    setAiGenerating(scanRunId)
    setActionError('')
    try {
      await api.admin.generateAIReport(scanRunId)
      // Open the AI-assisted report in a new tab instead of showing an alert.
      const url = api.reportHtmlAI(scanRunId, orgId)
      window.open(url, '_blank')
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'AI report generation failed')
    } finally {
      setAiGenerating(null)
    }
  }

  const openReport = (scanRunId: string, orgId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    const url = api.reportHtml(scanRunId, orgId)
    window.open(url, '_blank')
  }

  const openReportPdf = (scanRunId: string, orgId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    const url = api.reportPdf(scanRunId, orgId)
    window.open(url, '_blank')
  }

  const goToOrgDashboard = (orgId: string) => {
    navigate(`/dashboard?org_id=${orgId}`)
  }

  if (loading) {
    return (
      <div className="flex h-64 flex-col items-center justify-center gap-3 num text-[var(--text-muted)]">
        <Loader2 className="animate-spin text-[var(--neon-cyan)]" size={32} />
        <span className="text-[11px] uppercase tracking-[0.24em]">
          ▸ loading.console
          <span className="caret" />
        </span>
      </div>
    )
  }

  return (
    <div className="space-y-6 stagger">
      {/* Header */}
      <div className="flex items-end justify-between gap-3">
        <div>
          <div className="eyebrow mb-1">
            <span className="line" />
            <span>module :: admin.console</span>
          </div>
          <h1 className="display-title text-3xl gradient-text">Admin Console</h1>
          <p className="num mt-1 text-[12px] uppercase tracking-[0.14em] text-[var(--text-secondary)]">
            ▸ system-wide oversight — users, organizations, scans
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => navigate('/admin/scan')}
            className="btn-gradient"
            type="button"
          >
            <Radar size={13} /> New Scan
          </button>
          <button onClick={refreshAll} className="btn-ghost">
            <RefreshCw size={13} /> Refresh
          </button>
        </div>
      </div>

      {actionError && (
        <div
          className="panel p-3 num text-[12px] uppercase tracking-[0.12em]"
          style={{
            borderColor: 'var(--neon-red)',
            background: 'rgba(var(--neon-red-rgb),0.08)',
            color: 'var(--neon-red)',
          }}
        >
          <span className="prompt-prefix">!</span>
          {actionError}
        </div>
      )}

      {/* Metrics */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <MetricTile icon={Building2} label="orgs" value={metrics?.total_orgs ?? 0} color="var(--neon-cyan)" />
        <MetricTile icon={Users} label="users" value={metrics?.total_users ?? 0} color="var(--neon-violet)" />
        <MetricTile icon={Activity} label="scans" value={metrics?.total_scans ?? 0} color="var(--neon-magenta)" />
        <MetricTile icon={UserCheck} label="pending" value={metrics?.pending_registrations ?? 0} color="var(--neon-amber)" />
      </div>

      <AdminChartSystem orgs={orgs} onSelectOrg={goToOrgDashboard} />

      {/* Pending */}
      <div className="panel-terminal glass-card overflow-hidden">
        <div className="panel-header">
          <div className="flex items-center gap-2">
            <span className="dot dot-amber" />
            <span>module :: pending.registrations</span>
          </div>
          <span className="badge badge-warn">{pending.length} :: awaiting</span>
        </div>
        {pending.length === 0 ? (
          <div className="num px-5 py-8 text-center text-[12px] uppercase tracking-[0.14em] text-[var(--text-muted)]">
            ▸ no.pending.registrations · queue is empty
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="hud-table">
              <thead>
                <tr>
                  <th>name</th>
                  <th>domain</th>
                  <th>username</th>
                  <th>registered</th>
                  <th>assign role · act</th>
                </tr>
              </thead>
              <tbody>
                {pending.map((reg) => (
                  <tr key={reg.id}>
                    <td className="font-medium text-[var(--text-primary)]">{reg.full_name}</td>
                    <td className="text-[var(--text-secondary)]">{reg.organization_domain}</td>
                    <td className="mono text-[var(--neon-cyan)]">{reg.username}</td>
                    <td className="text-[var(--text-muted)]">{new Date(reg.created_at).toLocaleDateString()}</td>
                    <td>
                      <div className="flex items-center gap-2">
                        <select
                          value={selectedRoles[reg.id] || 'owner'}
                          onChange={(e) => setSelectedRoles({ ...selectedRoles, [reg.id]: e.target.value })}
                          disabled={busyId === reg.id}
                          className="glass-input num rounded-sm px-2 py-1.5 text-[12px]"
                        >
                          {ROLE_OPTIONS.map((r) => (
                            <option key={r.value} value={r.value}>{r.label}</option>
                          ))}
                        </select>
                        <button
                          onClick={() => handleApprove(reg.id)}
                          disabled={busyId === reg.id}
                          className="btn-ghost btn-success"
                        >
                          {busyId === reg.id ? <Loader2 className="animate-spin" size={11} /> : <Check size={11} />}
                          Approve
                        </button>
                        <button
                          onClick={() => handleReject(reg.id)}
                          disabled={busyId === reg.id}
                          className="btn-ghost btn-danger"
                        >
                          <X size={11} /> Reject
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* All Users */}
      <div className="panel-terminal glass-card overflow-hidden">
        <div className="panel-header">
          <div className="flex items-center gap-2">
            <span className="dot dot-violet" />
            <span>module :: all.users</span>
          </div>
          <span className="num text-[var(--text-muted)]">▸ {users.length} total</span>
        </div>
        <div className="overflow-x-auto">
          <table className="hud-table">
            <thead>
              <tr>
                <th>user</th>
                <th>role</th>
                <th>status</th>
                <th>org</th>
                <th>last.login</th>
                <th>actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td>
                    {editingUser?.id === u.id ? (
                      <div className="flex flex-col gap-1">
                        <input className="glass-input num rounded-sm px-2 py-1 text-[12px]" placeholder="Full name" value={editForm.full_name} onChange={(e) => setEditForm({ ...editForm, full_name: e.target.value })} />
                        <input className="glass-input num rounded-sm px-2 py-1 text-[12px]" placeholder="Username" value={editForm.username} onChange={(e) => setEditForm({ ...editForm, username: e.target.value })} />
                        <input className="glass-input num rounded-sm px-2 py-1 text-[12px]" placeholder="Email" value={editForm.email} onChange={(e) => setEditForm({ ...editForm, email: e.target.value })} />
                      </div>
                    ) : (
                      <>
                        <div className="font-medium text-[var(--text-primary)]">{u.full_name || u.username || u.email || 'Unnamed'}</div>
                        <div className="num text-[10px] uppercase tracking-[0.12em] text-[var(--text-muted)]">
                          {u.email ? `${u.email}` : u.username ? `@${u.username}` : ''}
                        </div>
                      </>
                    )}
                  </td>
                  <td>
                    {u.role === 'global_admin' ? (
                      <span className="badge badge-pass">{u.role}</span>
                    ) : (
                      <select
                        value={u.role}
                        onChange={(e) => handleRoleChange(u.id, e.target.value)}
                        disabled={busyId === u.id || u.role === 'global_admin' || editingUser?.id === u.id}
                        className="glass-input num rounded-sm px-2 py-1 text-[12px]"
                      >
                        {ROLE_OPTIONS.map((r) => (
                          <option key={r.value} value={r.value}>{r.label}</option>
                        ))}
                        <option value="public">Public</option>
                      </select>
                    )}
                  </td>
                  <td>
                    <span className={STATUS_BADGE[u.registration_status] || 'badge badge-neutral'}>
                      {u.registration_status}
                    </span>
                    {!u.is_active && u.registration_status === 'active' && (
                      <span className="ml-1 badge badge-neutral">disabled</span>
                    )}
                  </td>
                  <td className="text-[var(--text-secondary)]">{u.organization_domain || '—'}</td>
                  <td className="text-[var(--text-muted)]">
                    {u.last_login_at ? new Date(u.last_login_at).toLocaleString() : 'never'}
                  </td>
                  <td>
                    {u.role !== 'global_admin' && (
                      <div className="flex items-center gap-1.5">
                        {editingUser?.id === u.id ? (
                          <>
                            <button onClick={handleSaveEdit} disabled={busyId === u.id} className="btn-ghost btn-success">
                              {busyId === u.id ? <Loader2 className="animate-spin" size={11} /> : <Check size={11} />} Save
                            </button>
                            <button onClick={() => setEditingUser(null)} className="btn-ghost">Cancel</button>
                          </>
                        ) : (
                          <>
                            <button onClick={() => startEdit(u)} disabled={busyId === u.id} title="Edit" className="btn-ghost">
                              <Pencil size={11} />
                            </button>
                            <button
                              onClick={() => handleToggleActive(u.id, u.is_active)}
                              disabled={busyId === u.id}
                              title={u.is_active ? 'Disable user' : 'Enable user'}
                              className={`btn-ghost ${u.is_active ? 'btn-danger' : 'btn-success'}`}
                            >
                              {busyId === u.id ? <Loader2 className="animate-spin" size={11} /> : u.is_active ? <Ban size={11} /> : <Power size={11} />}
                            </button>
                            <button onClick={() => handleDeleteUser(u.id, u.full_name || u.username || u.email || 'Unnamed')} disabled={busyId === u.id} title="Delete" className="btn-ghost btn-danger">
                              <Trash2 size={11} />
                            </button>
                          </>
                        )}
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Orgs + Scans side by side */}
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="panel-terminal glass-card overflow-hidden">
          <div className="panel-header">
            <div className="flex items-center gap-2">
              <span className="dot dot-cyan" />
              <span>module :: organizations</span>
            </div>
            <span className="num text-[var(--text-muted)]">▸ {Math.min(orgs.length, orgTotal)} / {orgTotal}</span>
          </div>
          <div className="flex items-center gap-2 px-4 py-3 border-b border-[var(--border)]">
            <input
              type="search"
              value={orgQuery}
              onChange={(e) => setOrgQuery(e.target.value)}
              placeholder="search by name or domain…"
              className="num w-full bg-transparent border border-[var(--border)] px-3 py-1.5 text-[12px] uppercase tracking-[0.12em] text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:border-[var(--neon-cyan)]"
            />
            {orgLoading && <Loader2 size={13} className="animate-spin text-[var(--neon-cyan)]" />}
          </div>
          <div className="overflow-x-auto">
            <table className="hud-table">
              <thead>
                <tr>
                  <th>domain</th>
                  <th>verified</th>
                  <th>score</th>
                  <th>actions</th>
                </tr>
              </thead>
              <tbody>
                {orgs.map((o) => (
                  <tr key={o.id} className="cursor-pointer" onClick={() => goToOrgDashboard(o.id)}>
                    <td>
                      <div className="font-medium text-[var(--text-primary)]">{o.domain}</div>
                      <div className="num text-[10px] uppercase tracking-[0.12em] text-[var(--text-muted)]">{o.name}</div>
                    </td>
                    <td onClick={(e) => e.stopPropagation()}>
                      {o.ownership_verified ? (
                        <span className="badge badge-pass"><ShieldCheck size={11} /> yes</span>
                      ) : (
                        <span className="badge badge-neutral"><ShieldAlert size={11} /> no</span>
                      )}
                    </td>
                    <td>
                      {o.latest_score !== null ? (
                        <span
                          className="num font-semibold"
                          style={{
                            color:
                              (o.latest_shield_tier ?? 0) === 5 ? 'var(--neon-violet)'
                              : (o.latest_shield_tier ?? 0) === 4 ? 'var(--neon-green)'
                              : (o.latest_shield_tier ?? 0) === 3 ? 'var(--neon-cyan)'
                              : (o.latest_shield_tier ?? 0) === 2 ? 'var(--neon-amber)'
                              : 'var(--neon-red)',
                            textShadow: `0 0 8px currentColor`,
                          }}
                        >
                          {o.latest_score}
                        </span>
                      ) : (
                        <span className="text-[var(--text-muted)]">—</span>
                      )}
                    </td>
                    <td onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center gap-1.5">
                        <button
                          onClick={() => handleTogglePortscan(o.id, o.verified_portscan_authorized)}
                          disabled={busyId === o.id}
                          title={o.verified_portscan_authorized ? 'Revoke port scan' : 'Authorize port scan'}
                          className={`btn-ghost ${o.verified_portscan_authorized ? 'btn-success' : ''}`}
                        >
                          {busyId === o.id ? <Loader2 className="animate-spin" size={11} /> : <Radar size={11} />}
                          {o.verified_portscan_authorized ? 'auth' : 'grant'}
                        </button>
                        <button
                          onClick={() => handleRescan(o.id)}
                          disabled={rescanning === o.id}
                          className="btn-ghost"
                        >
                          {rescanning === o.id ? <Loader2 className="animate-spin" size={11} /> : <RefreshCw size={11} />}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {orgTotal > ORG_LIMIT && (
            <div className="px-4 py-3 border-t border-[var(--border)] flex justify-center">
              <button
                type="button"
                onClick={handleToggleAllOrgs}
                disabled={orgLoading}
                className="btn-ghost"
              >
                {orgLoading ? <Loader2 className="animate-spin" size={11} /> : null}
                {showAllOrgs ? 'Show Less' : `View All (${orgTotal})`}
              </button>
            </div>
          )}
        </div>

        <div className="panel-terminal glass-card overflow-hidden">
          <div className="panel-header">
            <div className="flex items-center gap-2">
              <span className="dot dot-magenta" />
              <span>module :: recent.scan-runs</span>
            </div>
            <span className="num text-[var(--text-muted)]">▸ {showAllScans ? scanRuns.length : Math.min(5, scanRuns.length)} / {scanRuns.length}</span>
          </div>
          <div className="overflow-x-auto">
            <table className="hud-table">
              <thead>
                <tr>
                  <th>domain</th>
                  <th>status</th>
                  <th>score</th>
                  <th>started</th>
                  <th>report</th>
                </tr>
              </thead>
              <tbody>
                {scanRuns.length === 0 ? (
                  <tr><td colSpan={5} className="px-5 py-8 text-center num text-[12px] uppercase tracking-[0.14em] text-[var(--text-muted)]">▸ no scans yet</td></tr>
                ) : (
                  (showAllScans ? scanRuns : scanRuns.slice(0, 5)).map((r) => (
                    <tr key={r.id} className="cursor-pointer" onClick={() => goToOrgDashboard(r.org_id)}>
                      <td className="font-medium text-[var(--text-primary)]">{r.domain}</td>
                      <td>
                        <span
                          className={
                            r.status === 'complete' ? 'badge badge-pass'
                            : r.status === 'failed' ? 'badge badge-fail'
                            : 'badge badge-warn'
                          }
                        >
                          {r.status}
                        </span>
                      </td>
                      <td className="mono">
                        {r.overall_score !== null ? (
                          <span style={{ color: 'var(--neon-cyan)' }}>{r.overall_score}</span>
                        ) : '—'}
                      </td>
                      <td className="num text-[var(--text-muted)]">
                        {new Date(r.started_at).toLocaleString()}
                      </td>
                      <td onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center gap-1.5">
                          <button
                            onClick={(e) => openReport(r.id, r.org_id, e)}
                            disabled={r.overall_score === null}
                            title={r.overall_score === null ? 'No score yet' : 'View standard report'}
                            className="btn-ghost"
                            style={{ borderColor: 'var(--neon-cyan)', color: 'var(--neon-cyan)' }}
                          >
                            <FileText size={11} />
                          </button>
                          <button
                            onClick={(e) => openReportPdf(r.id, r.org_id, e)}
                            disabled={r.overall_score === null}
                            title={r.overall_score === null ? 'No score yet' : 'Download standard PDF'}
                            className="btn-ghost"
                          >
                            <Download size={11} />
                          </button>
                          <button
                            onClick={(e) => handleGenerateAI(r.id, r.org_id, e)}
                            disabled={aiGenerating === r.id || r.overall_score === null}
                            title={r.overall_score === null ? 'No score yet' : 'Generate / view AI-assisted report'}
                            className="btn-ghost"
                            style={{ borderColor: 'var(--neon-violet)', color: 'var(--neon-violet)' }}
                          >
                            {aiGenerating === r.id ? <Loader2 className="animate-spin" size={11} /> : <Sparkles size={11} />}
                            AI
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
          {scanRuns.length > 5 && (
            <div className="px-4 py-3 border-t border-[var(--border)] flex justify-center">
              <button
                type="button"
                onClick={() => setShowAllScans((v) => !v)}
                className="btn-ghost"
              >
                {showAllScans ? 'Show Less' : `View All (${scanRuns.length})`}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
