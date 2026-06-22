import { useEffect, useState } from 'react'
import { Loader2, Zap, ShieldCheck } from 'lucide-react'
import { api } from '@/api/client'
import type { User } from '@/types'

export function SettingsPage() {
  const [user, setUser] = useState<User | null>(null)
  const [email, setEmail] = useState('')
  const [role, setRole] = useState('owner')
  const [portscanLoading, setPortscanLoading] = useState(false)
  const [portscanMessage, setPortscanMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    api.me().then(setUser).catch(() => setUser(null))
  }, [])

  const handleDevLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const data = await api.devLogin(email, role)
      localStorage.setItem('myeview_token', data.access_token)
      window.location.reload()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    }
  }

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
    <div className="mx-auto max-w-2xl space-y-8">
      <h1 className="text-2xl font-bold">Settings</h1>

      {user && (
        <div className="card p-5">
          <div className="section-title mb-3">Current Session</div>
          <div className="mb-4 text-sm">
            <div><strong>User:</strong> {user.email}</div>
            <div><strong>Role:</strong> {user.role}</div>
            <div><strong>Org ID:</strong> {user.org_id || 'none'}</div>
          </div>
          <button
            onClick={handleLogout}
            className="rounded-lg border border-[var(--border-color)] px-4 py-2 text-sm font-medium hover:bg-[var(--bg-secondary)]"
          >
            Log out
          </button>
        </div>
      )}

      <form onSubmit={handleDevLogin} className="card p-5">
        <div className="section-title mb-3">Development Login</div>
        <div className="mb-4 space-y-3">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="user@example.cm"
            className="w-full rounded-lg border border-[var(--border-color)] bg-[var(--bg-elevated)] px-3 py-2 text-[var(--text-primary)]"
            required
          />
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="w-full rounded-lg border border-[var(--border-color)] bg-[var(--bg-elevated)] px-3 py-2 text-[var(--text-primary)]"
          >
            <option value="owner">Owner</option>
            <option value="owner_technical">Owner Technical</option>
            <option value="ops">Ops</option>
          </select>
        </div>
        <button
          type="submit"
          className="w-full rounded-lg bg-[var(--accent)] px-4 py-2 font-semibold text-white hover:bg-[var(--accent)]/90"
        >
          Set Token
        </button>
      </form>

      <div className="card p-5">
        <div className="section-title mb-3">Verified Port Scan</div>
        <p className="mb-4 text-sm text-[var(--text-secondary)]">
          Trigger the gated TCP-connect + banner-read scan for legacy services. Requires
          organization authorization and owner/technical role.
        </p>
        <button
          onClick={handlePortscan}
          disabled={portscanLoading}
          className="flex w-full items-center justify-center gap-2 rounded-lg border border-[var(--border-color)] px-4 py-2 font-medium hover:bg-[var(--bg-secondary)] disabled:opacity-50"
        >
          {portscanLoading ? (
            <Loader2 className="animate-spin" size={18} />
          ) : (
            <Zap size={18} />
          )}
          Trigger Verified Port Scan
        </button>
        {portscanMessage && (
          <div className="mt-3 flex items-center gap-2 text-sm text-emerald-600 dark:text-emerald-400">
            <ShieldCheck size={16} /> {portscanMessage}
          </div>
        )}
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800 dark:border-red-900 dark:bg-red-900/20 dark:text-red-300">
          {error}
        </div>
      )}
    </div>
  )
}
