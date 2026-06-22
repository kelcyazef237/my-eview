import { useCallback, useEffect, useState } from 'react'
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

function MetricTile({ icon: Icon, label, value, accent }: { icon: React.ElementType; label: string; value: number; accent: string }) {
  return (
    <div className="glass-card glass-card-hover p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="section-title">{label}</p>
          <p className="mt-1 text-3xl font-bold">{value}</p>
        </div>
        <div className="flex h-12 w-12 items-center justify-center rounded-xl" style={{ background: accent }}>
          <Icon className="text-white" size={22} />
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
  const [scanRuns, setScanRuns] = useState<AdminScanRun[]>([])
  const [loading, setLoading] = useState(true)
  const [actionError, setActionError] = useState('')
  const [busyId, setBusyId] = useState<string | null>(null)
  const [selectedRoles, setSelectedRoles] = useState<Record<string, string>>({})
  const [rescanning, setRescanning] = useState<string | null>(null)
  const [editingUser, setEditingUser] = useState<AdminUser | null>(null)
  const [editForm, setEditForm] = useState({ full_name: '', username: '', email: '' })

  const refreshAll = useCallback(async () => {
    try {
      const [m, p, u, o, s] = await Promise.all([
        api.admin.metrics(),
        api.admin.registrations(),
        api.admin.users(),
        api.admin.orgs(),
        api.admin.scanRuns(),
      ])
      setMetrics(m)
      setPending(p)
      setUsers(u)
      setOrgs(o)
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
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Port scan auth failed')
    } finally {
      setBusyId(null)
    }
  }

  const goToOrgDashboard = (orgId: string) => {
    navigate(`/dashboard?org_id=${orgId}`)
  }

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-[var(--accent)]" />
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">
            <span className="gradient-text">Admin Console</span>
          </h1>
          <p className="text-sm text-[var(--text-secondary)]">
            System-wide oversight — users, organizations, and scans.
          </p>
        </div>
        <button
          onClick={refreshAll}
          className="flex items-center gap-1.5 rounded-lg border border-[var(--glass-border)] px-3 py-2 text-sm font-medium transition-colors hover:bg-[var(--glass-bg)]"
        >
          <RefreshCw size={15} /> Refresh
        </button>
      </div>

      {actionError && (
        <div className="rounded-lg border border-[var(--danger)]/30 bg-[var(--danger)]/10 p-3 text-sm text-[var(--danger)]">
          {actionError}
        </div>
      )}

      {/* Metric tiles */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <MetricTile icon={Building2} label="Organizations" value={metrics?.total_orgs ?? 0} accent="linear-gradient(135deg, #0f4c81, #2a8dd6)" />
        <MetricTile icon={Users} label="Users" value={metrics?.total_users ?? 0} accent="linear-gradient(135deg, #7c3aed, #a78bfa)" />
        <MetricTile icon={Activity} label="Scan Runs" value={metrics?.total_scans ?? 0} accent="linear-gradient(135deg, #0891b2, #22d3ee)" />
        <MetricTile icon={UserCheck} label="Pending" value={metrics?.pending_registrations ?? 0} accent="linear-gradient(135deg, #c67a2e, #f59e0b)" />
      </div>

      {/* System Overview — org scores + category breakdown */}
      <AdminChartSystem orgs={orgs} onSelectOrg={goToOrgDashboard} />

      {/* Pending Registrations */}
      <div className="glass-card overflow-hidden">
        <div className="flex items-center justify-between border-b border-[var(--glass-border)] px-5 py-3">
          <h2 className="font-semibold">Pending Registrations</h2>
          <span className="badge badge-warn">{pending.length} awaiting</span>
        </div>
        {pending.length === 0 ? (
          <p className="px-5 py-8 text-center text-sm text-[var(--text-muted)]">No pending registrations. Everyone is validated.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--glass-border)] text-left text-xs uppercase tracking-wider text-[var(--text-muted)]">
                  <th className="px-5 py-2 font-medium">Name</th>
                  <th className="px-5 py-2 font-medium">Domain</th>
                  <th className="px-5 py-2 font-medium">Username</th>
                  <th className="px-5 py-2 font-medium">Registered</th>
                  <th className="px-5 py-2 font-medium">Assign role & act</th>
                </tr>
              </thead>
              <tbody>
                {pending.map((reg) => (
                  <tr key={reg.id} className="border-b border-[var(--glass-border-subtle)] last:border-0">
                    <td className="px-5 py-3 font-medium">{reg.full_name}</td>
                    <td className="px-5 py-3 text-[var(--text-secondary)]">{reg.organization_domain}</td>
                    <td className="px-5 py-3 font-mono text-xs text-[var(--accent)]">{reg.username}</td>
                    <td className="px-5 py-3 text-[var(--text-muted)]">{new Date(reg.created_at).toLocaleDateString()}</td>
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-2">
                        <select
                          value={selectedRoles[reg.id] || 'owner'}
                          onChange={(e) => setSelectedRoles({ ...selectedRoles, [reg.id]: e.target.value })}
                          disabled={busyId === reg.id}
                          className="glass-input rounded-lg px-2 py-1.5 text-xs"
                        >
                          {ROLE_OPTIONS.map((r) => (
                            <option key={r.value} value={r.value}>{r.label}</option>
                          ))}
                        </select>
                        <button
                          onClick={() => handleApprove(reg.id)}
                          disabled={busyId === reg.id}
                          className="flex items-center gap-1 rounded-lg bg-emerald-600 px-2.5 py-1.5 text-xs font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-50"
                        >
                          {busyId === reg.id ? <Loader2 className="animate-spin" size={13} /> : <Check size={13} />}
                          Approve
                        </button>
                        <button
                          onClick={() => handleReject(reg.id)}
                          disabled={busyId === reg.id}
                          className="flex items-center gap-1 rounded-lg bg-red-600 px-2.5 py-1.5 text-xs font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-50"
                        >
                          <X size={13} /> Reject
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
      <div className="glass-card overflow-hidden">
        <div className="flex items-center justify-between border-b border-[var(--glass-border)] px-5 py-3">
          <h2 className="font-semibold">All Users</h2>
          <span className="text-xs text-[var(--text-muted)]">{users.length} total</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--glass-border)] text-left text-xs uppercase tracking-wider text-[var(--text-muted)]">
                <th className="px-5 py-2 font-medium">User</th>
                <th className="px-5 py-2 font-medium">Role</th>
                <th className="px-5 py-2 font-medium">Status</th>
                <th className="px-5 py-2 font-medium">Org</th>
                <th className="px-5 py-2 font-medium">Last login</th>
                <th className="px-5 py-2 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-b border-[var(--glass-border-subtle)] last:border-0">
                  <td className="px-5 py-3">
                    {editingUser?.id === u.id ? (
                      <div className="flex flex-col gap-1">
                        <input
                          className="glass-input rounded px-2 py-1 text-xs"
                          placeholder="Full name"
                          value={editForm.full_name}
                          onChange={(e) => setEditForm({ ...editForm, full_name: e.target.value })}
                        />
                        <input
                          className="glass-input rounded px-2 py-1 text-xs"
                          placeholder="Username"
                          value={editForm.username}
                          onChange={(e) => setEditForm({ ...editForm, username: e.target.value })}
                        />
                        <input
                          className="glass-input rounded px-2 py-1 text-xs"
                          placeholder="Email"
                          value={editForm.email}
                          onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                        />
                      </div>
                    ) : (
                      <>
                        <div className="font-medium">{u.full_name || u.username || u.email || 'Unnamed'}</div>
                        <div className="text-xs text-[var(--text-muted)]">
                          {u.email ? `\u{1F4E7} ${u.email}` : u.username ? `@${u.username}` : ''}
                        </div>
                      </>
                    )}
                  </td>
                  <td className="px-5 py-3">
                    {u.role === 'global_admin' ? (
                      <span className="badge badge-pass">{u.role}</span>
                    ) : (
                      <select
                        value={u.role}
                        onChange={(e) => handleRoleChange(u.id, e.target.value)}
                        disabled={busyId === u.id || u.role === 'global_admin' || editingUser?.id === u.id}
                        className="glass-input rounded-lg px-2 py-1 text-xs"
                      >
                        {ROLE_OPTIONS.map((r) => (
                          <option key={r.value} value={r.value}>{r.label}</option>
                        ))}
                        <option value="public">Public</option>
                      </select>
                    )}
                  </td>
                  <td className="px-5 py-3">
                    <span className={STATUS_BADGE[u.registration_status] || 'badge badge-neutral'}>
                      {u.registration_status}
                    </span>
                    {!u.is_active && u.registration_status === 'active' && (
                      <span className="ml-1 badge badge-neutral">disabled</span>
                    )}
                  </td>
                  <td className="px-5 py-3 text-[var(--text-secondary)]">{u.organization_domain || '\u2014'}</td>
                  <td className="px-5 py-3 text-[var(--text-muted)]">
                    {u.last_login_at ? new Date(u.last_login_at).toLocaleString() : 'never'}
                  </td>
                  <td className="px-5 py-3">
                    {u.role !== 'global_admin' && (
                      <div className="flex items-center gap-1.5">
                        {editingUser?.id === u.id ? (
                          <>
                            <button
                              onClick={handleSaveEdit}
                              disabled={busyId === u.id}
                              className="flex items-center gap-1 rounded-lg bg-emerald-600 px-2 py-1.5 text-xs font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-50"
                            >
                              {busyId === u.id ? <Loader2 className="animate-spin" size={13} /> : <Check size={13} />}
                              Save
                            </button>
                            <button
                              onClick={() => setEditingUser(null)}
                              className="rounded-lg border border-[var(--glass-border)] px-2 py-1.5 text-xs font-medium transition-colors hover:bg-[var(--glass-bg)]"
                            >
                              Cancel
                            </button>
                          </>
                        ) : (
                          <>
                            <button
                              onClick={() => startEdit(u)}
                              disabled={busyId === u.id}
                              title="Edit user"
                              className="flex items-center gap-1 rounded-lg border border-[var(--glass-border)] px-2 py-1.5 text-xs font-medium transition-colors hover:bg-[var(--glass-bg)] disabled:opacity-50"
                            >
                              <Pencil size={13} />
                            </button>
                            <button
                              onClick={() => handleToggleActive(u.id, u.is_active)}
                              disabled={busyId === u.id}
                              title={u.is_active ? 'Disable user' : 'Enable user'}
                              className={`flex items-center gap-1 rounded-lg px-2 py-1.5 text-xs font-medium transition-opacity hover:opacity-90 disabled:opacity-50 ${
                                u.is_active
                                  ? 'border border-[var(--danger)]/40 text-[var(--danger)]'
                                  : 'bg-emerald-600 text-white'
                              }`}
                            >
                              {busyId === u.id ? <Loader2 className="animate-spin" size={13} /> : u.is_active ? <Ban size={13} /> : <Power size={13} />}
                            </button>
                            <button
                              onClick={() => handleDeleteUser(u.id, u.full_name || u.username || u.email || 'Unnamed')}
                              disabled={busyId === u.id}
                              title="Delete user"
                              className="flex items-center gap-1 rounded-lg bg-red-600 px-2 py-1.5 text-xs font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-50"
                            >
                              <Trash2 size={13} />
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

      {/* Organizations + Scan Runs side by side on large screens */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Organizations */}
        <div className="glass-card overflow-hidden">
          <div className="flex items-center justify-between border-b border-[var(--glass-border)] px-5 py-3">
            <h2 className="font-semibold">Organizations</h2>
            <span className="text-xs text-[var(--text-muted)]">{orgs.length} total · click row to view dashboard</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--glass-border)] text-left text-xs uppercase tracking-wider text-[var(--text-muted)]">
                  <th className="px-5 py-2 font-medium">Domain</th>
                  <th className="px-5 py-2 font-medium">Verified</th>
                  <th className="px-5 py-2 font-medium">Score</th>
                  <th className="px-5 py-2 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {orgs.map((o) => (
                  <tr
                    key={o.id}
                    className="cursor-pointer border-b border-[var(--glass-border-subtle)] last:border-0 transition-colors hover:bg-[var(--glass-bg)]"
                    onClick={() => goToOrgDashboard(o.id)}
                  >
                    <td className="px-5 py-3">
                      <div className="font-medium">{o.domain}</div>
                      <div className="text-xs text-[var(--text-muted)]">{o.name}</div>
                    </td>
                    <td className="px-5 py-3" onClick={(e) => e.stopPropagation()}>
                      {o.ownership_verified ? (
                        <span className="badge badge-pass"><ShieldCheck size={12} /> Yes</span>
                      ) : (
                        <span className="badge badge-neutral"><ShieldAlert size={12} /> No</span>
                      )}
                    </td>
                    <td className="px-5 py-3">
                      {o.latest_score !== null ? (
                        <span className="font-mono font-semibold">{o.latest_score}</span>
                      ) : (
                        <span className="text-[var(--text-muted)]">{'\u2014'}</span>
                      )}
                    </td>
                    <td className="px-5 py-3" onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center gap-1.5">
                        <button
                          onClick={() => handleTogglePortscan(o.id, o.verified_portscan_authorized)}
                          disabled={busyId === o.id}
                          title={o.verified_portscan_authorized ? 'Revoke port scan' : 'Authorize port scan'}
                          className={`flex items-center gap-1 rounded-lg px-2 py-1.5 text-xs font-medium transition-opacity hover:opacity-90 disabled:opacity-50 ${
                            o.verified_portscan_authorized
                              ? 'bg-cyan-600 text-white'
                              : 'border border-[var(--glass-border)] text-[var(--text-secondary)]'
                          }`}
                        >
                          {busyId === o.id ? <Loader2 className="animate-spin" size={13} /> : <Radar size={13} />}
                        </button>
                        <button
                          onClick={() => handleRescan(o.id)}
                          disabled={rescanning === o.id}
                          className="flex items-center gap-1 rounded-lg border border-[var(--glass-border)] px-2 py-1.5 text-xs font-medium transition-colors hover:bg-[var(--glass-bg)] disabled:opacity-50"
                        >
                          {rescanning === o.id ? <Loader2 className="animate-spin" size={13} /> : <RefreshCw size={13} />}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Scan Runs */}
        <div className="glass-card overflow-hidden">
          <div className="flex items-center justify-between border-b border-[var(--glass-border)] px-5 py-3">
            <h2 className="font-semibold">Recent Scan Runs</h2>
            <span className="text-xs text-[var(--text-muted)]">last 50 · click to view dashboard</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--glass-border)] text-left text-xs uppercase tracking-wider text-[var(--text-muted)]">
                  <th className="px-5 py-2 font-medium">Domain</th>
                  <th className="px-5 py-2 font-medium">Status</th>
                  <th className="px-5 py-2 font-medium">Score</th>
                  <th className="px-5 py-2 font-medium">Started</th>
                </tr>
              </thead>
              <tbody>
                {scanRuns.length === 0 ? (
                  <tr><td colSpan={4} className="px-5 py-8 text-center text-[var(--text-muted)]">No scans yet.</td></tr>
                ) : (
                  scanRuns.map((r) => (
                    <tr
                      key={r.id}
                      className="cursor-pointer border-b border-[var(--glass-border-subtle)] last:border-0 transition-colors hover:bg-[var(--glass-bg)]"
                      onClick={() => goToOrgDashboard(r.org_id)}
                    >
                      <td className="px-5 py-3 font-medium">{r.domain}</td>
                      <td className="px-5 py-3">
                        <span className={
                          r.status === 'complete' ? 'badge badge-pass' :
                          r.status === 'failed' ? 'badge badge-fail' :
                          'badge badge-warn'
                        }>
                          {r.status}
                        </span>
                      </td>
                      <td className="px-5 py-3 font-mono">
                        {r.overall_score !== null ? r.overall_score : '\u2014'}
                      </td>
                      <td className="px-5 py-3 text-[var(--text-muted)]">
                        {new Date(r.started_at).toLocaleString()}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}