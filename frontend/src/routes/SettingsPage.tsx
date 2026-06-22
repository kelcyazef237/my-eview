import { useEffect, useState } from 'react'
import { Loader2, Zap, ShieldCheck } from 'lucide-react'
import { api } from '@/api/client'
import type { User } from '@/types'

export function SettingsPage() {
  const [user, setUser] = useState<User | null>(null)
  const [portscanLoading, setPortscanLoading] = useState(false)
  const [portscanMessage, setPortscanMessage] = useState('')
  const [error, setError] = useState('')

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

  return (
    <div className="mx-auto max-w-2xl space-y-8 animate-fade-in">
      <h1 className="text-2xl font-bold">Settings</h1>

      {user && (
        <div className="glass-card p-5">
          <div className="section-title mb-3">Current Session</div>
          <div className="mb-4 space-y-1 text-sm">
            {user.full_name && <div><strong>Name:</strong> {user.full_name}</div>}
            {user.username && <div><strong>Username:</strong> <span className="font-mono text-[var(--accent)]">{user.username}</span></div>}
            {user.email && <div><strong>Email:</strong> {user.email}</div>}
            <div><strong>Role:</strong> <span className="badge badge-pass">{user.role}</span></div>
            <div><strong>Status:</strong> {user.registration_status}</div>
            <div><strong>Org ID:</strong> {user.org_id || 'none'}</div>
          </div>
          <button
            onClick={handleLogout}
            className="rounded-lg border border-[var(--glass-border)] px-4 py-2 text-sm font-medium transition-colors hover:bg-[var(--glass-bg)]"
          >
            Log out
          </button>
        </div>
      )}

      <div className="glass-card p-5">
        <div className="section-title mb-3">Verified Port Scan</div>
        <p className="mb-4 text-sm text-[var(--text-secondary)]">
          Trigger the gated TCP-connect + banner-read scan for legacy services. Requires
          organization authorization and owner/technical role.
        </p>
        <button
          onClick={handlePortscan}
          disabled={portscanLoading}
          className="flex w-full items-center justify-center gap-2 rounded-lg border border-[var(--glass-border)] px-4 py-2 font-medium transition-colors hover:bg-[var(--glass-bg)] disabled:opacity-50"
        >
          {portscanLoading ? (
            <Loader2 className="animate-spin" size={18} />
          ) : (
            <Zap size={18} />
          )}
          Trigger Verified Port Scan
        </button>
        {portscanMessage && (
          <div className="mt-3 flex items-center gap-2 text-sm text-[var(--success)]">
            <ShieldCheck size={16} /> {portscanMessage}
          </div>
        )}
      </div>

      {error && (
        <div className="rounded-lg border border-[var(--danger)]/30 bg-[var(--danger)]/10 p-4 text-sm text-[var(--danger)]">
          {error}
        </div>
      )}
    </div>
  )
}