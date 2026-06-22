import { useState } from 'react'
import { Search, Loader2, LogIn } from 'lucide-react'
import { api } from '@/api/client'
import { ScoreGauge } from '@/components/ScoreGauge'
import type { PublicScore } from '@/types'

export function PublicLookup() {
  const [domain, setDomain] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [score, setScore] = useState<PublicScore | null>(null)

  // Dev login is only available when VITE_DEV_LOGIN is set (development mode)
  const showDevLogin = import.meta.env.VITE_DEV_LOGIN === 'true'
  const [devDomain, setDevDomain] = useState('')
  const [devRole, setDevRole] = useState<'owner' | 'owner_technical' | 'ops'>('owner')
  const [devLoading, setDevLoading] = useState(false)
  const [devError, setDevError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setScore(null)
    try {
      const data = await api.lookupDomain(domain)
      setScore(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Lookup failed')
    } finally {
      setLoading(false)
    }
  }

  const handleTrigger = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await api.triggerLookup(domain)
      setScore(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Scan trigger failed')
    } finally {
      setLoading(false)
    }
  }

  const devLogin = async () => {
    setDevLoading(true)
    setDevError('')
    const email = `dev@${devDomain || 'example.cm'}`
    try {
      const data = await api.devLogin(email, devRole, devDomain || undefined)
      localStorage.setItem('myeview_token', data.access_token)
      window.location.href = devRole === 'owner_technical' ? '/technical' : '/dashboard'
    } catch (err) {
      setDevError(err instanceof Error ? err.message : 'Dev login failed')
    } finally {
      setDevLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl">
      <div className="mb-8 text-center">
        <h1 className="mb-2 text-3xl font-bold">External Digital Trust Score</h1>
        <p className="text-[var(--text-secondary)]">
          Enter a Cameroonian domain to see its public MYEVIEW score, shield tier, and trend.
        </p>
      </div>

      {showDevLogin && (
        <div className="mb-6 rounded-lg border border-[var(--border-color)] bg-[var(--bg-elevated)] p-4">
          <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-[var(--text-secondary)]">
            <LogIn size={16} /> Dev Login — access dashboard, technical view, reports
          </div>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
            <div className="flex-1">
              <label className="mb-1 block text-xs text-[var(--text-muted)]">Domain (your scanned org)</label>
              <input
                type="text"
                value={devDomain}
                onChange={(e) => setDevDomain(e.target.value)}
                placeholder="matrixtelecoms.com"
                className="w-full rounded-lg border border-[var(--border-color)] bg-[var(--bg-secondary)] px-3 py-2 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:border-[var(--accent)] focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs text-[var(--text-muted)]">Role</label>
              <select
                value={devRole}
                onChange={(e) => setDevRole(e.target.value as 'owner' | 'owner_technical' | 'ops')}
                className="rounded-lg border border-[var(--border-color)] bg-[var(--bg-secondary)] px-3 py-2 text-sm text-[var(--text-primary)] focus:border-[var(--accent)] focus:outline-none"
              >
                <option value="owner">Owner</option>
                <option value="owner_technical">Technical</option>
                <option value="ops">Ops (admin)</option>
              </select>
            </div>
            <button
              onClick={devLogin}
              disabled={devLoading}
              className="flex items-center justify-center gap-2 rounded-lg bg-[var(--accent)] px-4 py-2 text-sm font-semibold text-white hover:bg-[var(--accent)]/90 disabled:opacity-50"
            >
              {devLoading ? <Loader2 className="animate-spin" size={16} /> : <LogIn size={16} />}
              Login
            </button>
          </div>
          {devError && (
            <div className="mt-2 text-sm text-red-500">{devError}</div>
          )}
        </div>
      )}

      <form onSubmit={handleSubmit} className="mb-8">
        <div className="flex gap-2">
          <input
            type="text"
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            placeholder="example.cm"
            className="flex-1 rounded-lg border border-[var(--border-color)] bg-[var(--bg-elevated)] px-4 py-3 text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:border-[var(--accent)] focus:outline-none"
          />
          <button
            type="submit"
            disabled={loading || !domain}
            className="flex items-center gap-2 rounded-lg bg-[var(--accent)] px-6 py-3 font-semibold text-white hover:bg-[var(--accent)]/90 disabled:opacity-50"
          >
            {loading ? <Loader2 className="animate-spin" size={18} /> : <Search size={18} />}
            Lookup
          </button>
        </div>
      </form>

      {error && (
        <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800 dark:border-red-900 dark:bg-red-900/20 dark:text-red-300">
          {error}
          <button
            onClick={handleTrigger}
            disabled={loading}
            className="ml-2 font-semibold underline"
          >
            Trigger scan
          </button>
        </div>
      )}

      {score && (
        <div className="space-y-6">
          <ScoreGauge
            score={score.overall_score}
            tier={score.shield_tier}
            label={score.shield_label}
            outlook={score.outlook}
          />

          <div className="card p-5">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <div className="text-sm text-[var(--text-secondary)]">Domain</div>
                <div className="text-lg font-semibold">{score.domain}</div>
              </div>
              <div className="text-right">
                <div className="text-sm text-[var(--text-secondary)]">Organization</div>
                <div className="text-lg font-semibold">{score.org_name}</div>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="rounded-lg bg-[var(--bg-secondary)] p-3">
                <div className="text-[var(--text-muted)]">Band</div>
                <div className="font-medium">{score.band}</div>
              </div>
              <div className="rounded-lg bg-[var(--bg-secondary)] p-3">
                <div className="text-[var(--text-muted)]">Ruleset</div>
                <div className="font-medium">{score.ruleset_version}</div>
              </div>
              <div className="rounded-lg bg-[var(--bg-secondary)] p-3">
                <div className="text-[var(--text-muted)]">Sector Benchmark</div>
                <div className="font-medium">{score.sector_benchmark ?? '—'}</div>
              </div>
              <div className="rounded-lg bg-[var(--bg-secondary)] p-3">
                <div className="text-[var(--text-muted)]">Computed</div>
                <div className="font-medium">{new Date(score.computed_at).toLocaleString()}</div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="mt-8 text-center text-xs text-[var(--text-muted)]">
        Public lookup shows score, tier, and trend only. Detailed findings require verified ownership.
      </div>
    </div>
  )
}
