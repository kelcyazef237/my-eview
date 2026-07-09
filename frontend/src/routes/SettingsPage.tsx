import { useEffect, useState } from 'react'
import { Loader2, Zap, ShieldCheck, LogOut, Cpu, AlertTriangle } from 'lucide-react'
import { api } from '@/api/client'
import type { User } from '@/types'

export function SettingsPage() {
  const [user, setUser] = useState<User | null>(null)
  const [portscanLoading, setPortscanLoading] = useState(false)
  const [portscanMessage, setPortscanMessage] = useState('')
  const [error, setError] = useState('')
  const [wipeLoading, setWipeLoading] = useState(false)
  const [wipeConfirm, setWipeConfirm] = useState('')
  const [wipeResult, setWipeResult] = useState('')

  useEffect(() => {
    api.me().then(setUser).catch(() => setUser(null))
  }, [])

  const handlePortscan = async () => {
    setPortscanLoading(true)
    setPortscanMessage('')
    try {
      const data = await api.triggerPortscan()
      setPortscanMessage(`Queued task ${data.task_id} for scan ${data.scan_run_id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Portscan trigger failed')
    } finally {
      setPortscanLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('myeview_token')
    window.location.href = '/'
  }

  const handleWipe = async () => {
    if (wipeConfirm !== 'WIPE') {
      setError('Type "WIPE" exactly to confirm.')
      return
    }
    if (!confirm('This will permanently delete ALL organizations and all scan data. Global admin accounts will survive. Continue?')) {
      return
    }
    setWipeLoading(true)
    setError('')
    setWipeResult('')
    try {
      const res = await api.admin.cleanScanData(wipeConfirm)
      setWipeResult(`Wiped ${res.deleted_organizations} organization(s). All scan data cleared.`)
      setWipeConfirm('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Wipe failed')
    } finally {
      setWipeLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-2xl stagger">
      <div className="mb-6">
        <div className="eyebrow mb-1">
          <span className="line" />
          <span>module :: settings</span>
        </div>
        <h1 className="display-title text-3xl gradient-text">Settings</h1>
      </div>

      {user && (
        <div className="panel-terminal glass-card mb-6">
          <div className="panel-header">
            <div className="flex items-center gap-2">
              <span className="dot dot-cyan" />
              <span>current.session</span>
            </div>
            <span className="num">{user.registration_status}</span>
          </div>
          <div className="panel-body space-y-3 text-[13px]">
            <Row label="name" value={user.full_name} color="var(--neon-cyan)" />
            <Row label="username" value={user.username ? `@${user.username}` : null} mono color="var(--neon-cyan)" />
            <Row label="email" value={user.email} color="var(--neon-magenta)" />
            <Row label="role" value={user.role} color="var(--neon-violet)" />
            <Row label="status" value={user.registration_status} color="var(--neon-green)" />
            <Row label="org.id" value={user.org_id || 'none'} mono color="var(--text-secondary)" />
            <div className="pt-3">
              <button onClick={handleLogout} className="btn-ghost">
                <LogOut size={13} /> Log Out
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="panel-terminal glass-card mb-6">
        <div className="panel-header">
          <div className="flex items-center gap-2">
            <span className="dot dot-magenta" />
            <span>module :: verified.port-scan</span>
          </div>
          <span>gated</span>
        </div>
        <div className="panel-body">
          <div className="mb-2 flex items-center gap-2">
            <Zap size={14} className="text-[var(--neon-magenta)]" />
            <span className="display-title text-[12px] tracking-[0.08em] text-white">
              Verified Port Scan
            </span>
          </div>
          <p className="mb-4 num text-[12px] text-[var(--text-secondary)]">
            ▸ Trigger the gated TCP-connect + banner-read scan for legacy services. Requires organization authorization and owner/technical role.
          </p>
          <button
            onClick={handlePortscan}
            disabled={portscanLoading}
            className="btn-gradient w-full"
          >
            {portscanLoading ? (
              <>
                <Loader2 className="animate-spin" size={14} /> Queuing
              </>
            ) : (
              <>
                <Zap size={14} /> Trigger Verified Port Scan
              </>
            )}
          </button>
          {portscanMessage && (
            <div
              className="mt-3 flex items-center gap-2 num text-[12px]"
              style={{ color: 'var(--neon-green)' }}
            >
              <ShieldCheck size={14} /> {portscanMessage}
            </div>
          )}
        </div>
      </div>

      {user?.role === 'global_admin' && (
        <div
          className="panel-terminal glass-card mb-6"
          style={{ borderColor: 'var(--neon-red)' }}
        >
          <div className="panel-header" style={{ borderColor: 'var(--neon-red)' }}>
            <div className="flex items-center gap-2">
              <span className="dot" style={{ background: 'var(--neon-red)' }} />
              <span>module :: danger.zone</span>
            </div>
            <span className="num" style={{ color: 'var(--neon-red)' }}>global_admin</span>
          </div>
          <div className="panel-body">
            <div className="mb-2 flex items-center gap-2">
              <AlertTriangle size={14} className="text-[var(--neon-red)]" />
              <span className="display-title text-[12px] tracking-[0.08em] text-white">
                Wipe All Scan Data & Organizations
              </span>
            </div>
            <p className="mb-4 num text-[12px] text-[var(--text-secondary)]">
              ▸ Permanently deletes every organization and cascades to scan_runs, findings,
              scores, score_history, assets, report_shares, and attached owner/ops users.
              Global admin accounts survive (detached first). This cannot be undone.
            </p>
            <div className="mb-3">
              <label className="num text-[11px] uppercase tracking-[0.14em] text-[var(--text-muted)]">
                type WIPE to confirm
              </label>
              <input
                type="text"
                value={wipeConfirm}
                onChange={(e) => setWipeConfirm(e.target.value)}
                placeholder="WIPE"
                className="num w-full mt-1 bg-transparent border border-[var(--neon-red)] px-3 py-1.5 text-[12px] uppercase tracking-[0.12em] text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none"
                style={{ background: 'rgba(255,48,96,0.05)' }}
                disabled={wipeLoading}
              />
            </div>
            <button
              onClick={handleWipe}
              disabled={wipeLoading || wipeConfirm !== 'WIPE'}
              className="btn-ghost w-full"
              style={{
                borderColor: 'var(--neon-red)',
                color: 'var(--neon-red)',
                opacity: wipeConfirm !== 'WIPE' ? 0.4 : 1,
              }}
            >
              {wipeLoading ? (
                <>
                  <Loader2 className="animate-spin" size={14} /> Wiping
                </>
              ) : (
                <>
                  <AlertTriangle size={14} /> Wipe All Data
                </>
              )}
            </button>
            {wipeResult && (
              <div
                className="mt-3 flex items-center gap-2 num text-[12px]"
                style={{ color: 'var(--neon-green)' }}
              >
                <ShieldCheck size={14} /> {wipeResult}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Decorative system card */}
      <div className="panel glass-card p-4">
        <div className="flex items-center gap-3 num text-[11px] uppercase tracking-[0.16em] text-[var(--text-muted)]">
          <Cpu size={14} className="text-[var(--neon-cyan)]" />
          <span>build :: myeview.trust-os v1.0.4</span>
          <span className="text-[var(--neon-magenta)]">·</span>
          <span>node :: cm-01</span>
          <span className="text-[var(--neon-cyan)]">·</span>
          <span>channel :: stable</span>
          <span className="ml-auto inline-flex items-center gap-1 text-[var(--neon-green)]">
            <span className="dot dot-green" /> online
          </span>
        </div>
      </div>

      {error && (
        <div
          className="panel mt-6 p-4 num text-[12px] uppercase tracking-[0.12em]"
          style={{
            borderColor: 'var(--neon-red)',
            background: 'rgba(255,48,96,0.08)',
            color: 'var(--neon-red)',
          }}
        >
          <span className="prompt-prefix">!</span>
          {error}
        </div>
      )}
    </div>
  )
}

function Row({
  label,
  value,
  mono,
  color,
}: {
  label: string
  value: string | null
  mono?: boolean
  color: string
}) {
  if (!value) return null
  return (
    <div className="flex items-center justify-between gap-2 border-b border-[var(--glass-border-subtle)] pb-2 last:border-0">
      <span className="num text-[11px] uppercase tracking-[0.14em] text-[var(--text-muted)]">
        ▸ {label}
      </span>
      <span
        className={mono ? 'num' : ''}
        style={{ color, textShadow: `0 0 8px ${color}40` }}
      >
        {value}
      </span>
    </div>
  )
}
