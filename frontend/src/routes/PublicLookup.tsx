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
        <h1 className="mb-2 text-3xl font-bold">
          <span className="gradient-text">External Digital Trust Score</span>
        </h1>
        <p className="text-[var(--text-secondary)]">
          Enter a Cameroonian domain to see its public MYEVIEW score, shield tier, and trend.
        </p>
      </div>

      {showDevLogin && (
        <div className="glass-card mb-6 p-4">
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
                className="glass-input w-full px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs text-[var(--text-muted)]">Role</label>
              <select
                value={devRole}
                onChange={(e) => setDevRole(e.target.value as 'owner' | 'owner_technical' | 'ops')}
                className="glass-input px-3 py-2 text-sm"
              >
                <option value="owner">Owner</option>
                <option value="owner_technical">Technical</option>
                <option value="ops">Ops (admin)</option>
              </select>
            </div>
            <button
              onClick={devLogin}
              disabled={devLoading}
              className="flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
              style={{ background: 'var(--gradient-accent)' }}
            >
              {devLoading ? <Loader2 className="animate-spin" size={16} /> : <LogIn size={16} />}
              Login
            </button>
          </div>
          {devError && (
            <div className="mt-2 text-sm text-[var(--danger)]">{devError}</div>
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
            className="glass-input flex-1 px-4 py-3"
          />
          <button
            type="submit"
            disabled={loading || !domain}
            className="flex items-center gap-2 rounded-xl px-6 py-3 font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
            style={{ background: 'var(--gradient-accent)' }}
          >
            {loading ? <Loader2 className="animate-spin" size={18} /> : <Search size={18} />}
            Lookup
          </button>
        </div>
      </form>

      {error && (
        <div className="mb-6 rounded-lg border border-[var(--danger)]/30 bg-[var(--danger)]/10 p-4 text-sm text-[var(--danger)]">
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

          <div className="glass-card p-5">
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
              <div className="rounded-lg bg-[var(--glass-bg)] p-3">
                <div className="text-[var(--text-muted)]">Band</div>
                <div className="font-medium">{score.band}</div>
              </div>
              <div className="rounded-lg bg-[var(--glass-bg)] p-3">
                <div className="text-[var(--text-muted)]">Ruleset</div>
                <div className="font-medium">{score.ruleset_version}</div>
              </div>
              <div className="rounded-lg bg-[var(--glass-bg)] p-3">
                <div className="text-[var(--text-muted)]">Sector Benchmark</div>
                <div className="font-medium">{score.sector_benchmark ?? '—'}</div>
              </div>
              <div className="rounded-lg bg-[var(--glass-bg)] p-3">
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
