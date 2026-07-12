import { useState } from 'react'
import { Search, Loader2, LogIn, Terminal, Globe, AlertTriangle, Sparkles } from 'lucide-react'
import { api } from '@/api/client'
import { ScoreGauge } from '@/components/ScoreGauge'
import type { PublicScore } from '@/types'

export function PublicLookup() {
  const [domain, setDomain] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [score, setScore] = useState<PublicScore | null>(null)

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
    <div className="mx-auto max-w-3xl stagger">
      {/* Header */}
      <div className="mb-8 text-center">
        <div className="eyebrow mb-3 justify-center">
          <span className="line" />
          <span>module :: public.lookup</span>
          <span className="line" />
        </div>
        <h1 className="display-title text-4xl gradient-text mb-2">
          External Digital Trust Score
        </h1>
        <p className="text-sm text-[var(--text-secondary)]">
          Enter a Cameroonian domain to inspect its public MYEVIEW score, shield tier, and benchmark.
        </p>
      </div>

      {showDevLogin && (
        <div className="panel-terminal glass-card mb-6">
          <div className="panel-header">
            <div className="flex items-center gap-2">
              <span className="dot dot-magenta" />
              <span>dev.login</span>
            </div>
            <span>debug only</span>
          </div>
          <div className="panel-body space-y-3">
            <div className="num text-[12px] uppercase tracking-[0.12em] text-[var(--neon-magenta)]">
              <span className="prompt-prefix">!</span>development.access
            </div>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
              <div className="flex-1">
                <label className="eyebrow mb-1 block">
                  <span className="line" />
                  <span>domain</span>
                </label>
                <input
                  type="text"
                  value={devDomain}
                  onChange={(e) => setDevDomain(e.target.value)}
                  placeholder="matrixtelecoms.com"
                  className="glass-input num w-full px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="eyebrow mb-1 block">
                  <span className="line" />
                  <span>role</span>
                </label>
                <select
                  value={devRole}
                  onChange={(e) => setDevRole(e.target.value as 'owner' | 'owner_technical' | 'ops')}
                  className="glass-input num px-3 py-2 text-sm"
                >
                  <option value="owner">Owner</option>
                  <option value="owner_technical">Owner / Technical</option>
                  <option value="ops">Ops (admin)</option>
                </select>
              </div>
              <button
                onClick={devLogin}
                disabled={devLoading}
                className="btn-gradient"
              >
                {devLoading ? <Loader2 className="animate-spin" size={14} /> : <LogIn size={14} />}
                Login
              </button>
            </div>
            {devError && (
              <div className="num text-[12px]" style={{ color: 'var(--neon-red)' }}>
                <span className="prompt-prefix">!</span>
                {devError}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Terminal-styled lookup */}
      <div className="panel-terminal glass-card mb-8">
        <div className="panel-header">
          <div className="flex items-center gap-2">
            <span className="dot dot-cyan" />
            <span>trust --lookup</span>
          </div>
          <div className="flex items-center gap-2">
            <Terminal size={10} className="text-[var(--text-muted)]" />
            <span>interactive</span>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="panel-body">
          <div className="mb-2 flex items-center gap-2 num text-[12px] text-[var(--text-muted)]">
            <span className="prompt-prefix">$</span>
            <span>trust.os lookup --domain</span>
          </div>
          <div className="flex flex-col gap-2 sm:flex-row">
            <div className="relative flex-1">
              <Globe size={14} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[var(--neon-cyan)]" />
              <input
                type="text"
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                placeholder="example.cm"
                className="glass-input num w-full py-3 pl-9 pr-3"
              />
              {!loading && domain && <span className="caret absolute right-3 top-1/2 -translate-y-1/2" />}
            </div>
            <button
              type="submit"
              disabled={loading || !domain}
              className="btn-gradient"
            >
              {loading ? <Loader2 className="animate-spin" size={16} /> : <Search size={16} />}
              Execute Lookup
            </button>
          </div>
        </form>
      </div>

      {error && (
        <div
          className="panel mb-6 p-4 flex items-center justify-between gap-3"
          style={{ borderColor: 'var(--neon-red)', boxShadow: '0 0 30px rgba(var(--neon-red-rgb),0.15)' }}
        >
          <div className="flex items-center gap-2 num text-[13px]" style={{ color: 'var(--neon-red)' }}>
            <AlertTriangle size={14} /> {error}
          </div>
          <button onClick={handleTrigger} disabled={loading} className="btn-ghost">
            <Sparkles size={12} /> Trigger Scan
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
            sectorBenchmark={score.sector_benchmark ?? null}
          />

          <div className="panel-terminal glass-card">
            <div className="panel-header">
              <div className="flex items-center gap-2">
                <span className="dot dot-violet" />
                <span>record.observation</span>
              </div>
              <span>read.only</span>
            </div>
            <div className="panel-body">
              <div className="mb-4 flex items-center justify-between gap-3">
                <div className="min-w-0">
                  <div className="eyebrow mb-1">
                    <span className="line" />
                    <span>domain</span>
                  </div>
                  <div
                    className="num truncate text-xl font-semibold text-[var(--text-primary)] glitch"
                    data-text={score.domain}
                  >
                    {score.domain}
                  </div>
                </div>
                <div className="min-w-0 text-right">
                  <div className="eyebrow mb-1 justify-end">
                    <span className="line" />
                    <span>organization</span>
                  </div>
                  <div className="num truncate text-xl font-semibold text-[var(--text-primary)]">
                    {score.org_name}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 text-sm">
                <DataCell label="band" value={score.band} accent="cyan" />
                <DataCell label="ruleset" value={score.ruleset_version} accent="violet" />
                <DataCell
                  label="sector.benchmark"
                  value={
                    score.sector_benchmark !== null && score.sector_benchmark !== undefined
                      ? String(score.sector_benchmark)
                      : '—'
                  }
                  accent="green"
                />
                <DataCell
                  label="computed"
                  value={new Date(score.computed_at).toLocaleString()}
                  accent="magenta"
                />
              </div>

              {score.sector_benchmark !== null && score.sector_benchmark !== undefined && (
                <div className="mt-4 flex items-center gap-2 num text-[12px]">
                  <span className="prompt-prefix">{`>`}</span>
                  {score.overall_score > score.sector_benchmark ? (
                    <span className="above-sector-avg">
                      ▲ Above sector average by {(score.overall_score - score.sector_benchmark)} points
                    </span>
                  ) : score.overall_score < score.sector_benchmark ? (
                    <span style={{ color: 'var(--neon-amber)' }}>▼ Below sector benchmark by {(score.sector_benchmark - score.overall_score)}</span>
                  ) : (
                    <span style={{ color: 'var(--text-secondary)' }}>= matches sector average</span>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="mt-8 text-center num text-[11px] uppercase tracking-[0.16em] text-[var(--text-muted)]">
        ▸ public lookup shows score, tier, trend only · detailed findings require verified ownership
      </div>
    </div>
  )
}

function DataCell({
  label,
  value,
  accent,
}: {
  label: string
  value: string
  accent: 'cyan' | 'violet' | 'magenta' | 'green' | 'amber'
}) {
  const colorVar =
    accent === 'cyan' ? 'var(--neon-cyan)'
    : accent === 'violet' ? 'var(--neon-violet)'
    : accent === 'magenta' ? 'var(--neon-magenta)'
    : accent === 'green' ? 'var(--neon-green)'
    : 'var(--neon-amber)'

  return (
    <div
      className="rounded-sm border terminal-surface-strong p-3"
      style={{ borderColor: colorVar }}
    >
      <div className="num text-[10px] uppercase tracking-[0.14em] text-[var(--text-muted)]">
        {label}
      </div>
      <div className="num mt-1 font-semibold" style={{ color: colorVar, textShadow: `0 0 8px ${colorVar}80` }}>
        {value}
      </div>
    </div>
  )
}
