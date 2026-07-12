import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Building2, Globe, Loader2, Radar, AlertTriangle, ShieldCheck, ArrowLeft, Briefcase } from 'lucide-react'
import { api } from '@/api/client'

const SECTOR_OPTIONS = [
  { code: 'general',    label: 'General / Unspecified' },
  { code: 'finance',    label: 'Finance & Microfinance' },
  { code: 'fintech',    label: 'Fintech & Payments' },
  { code: 'health',     label: 'Health & Medical' },
  { code: 'education',  label: 'Education & Research' },
  { code: 'telecom',    label: 'Telecom & ISP' },
  { code: 'ecommerce',  label: 'E-Commerce & Retail' },
  { code: 'government', label: 'Government & Public Sector' },
]

export function AdminScanPage() {
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [domain, setDomain] = useState('')
  const [sector, setSector] = useState('general')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<{ scan_run_id: string; org_id: string; name: string; domain: string } | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim() || !domain.trim()) {
      setError('Both organization name and domain are required.')
      return
    }
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const data = await api.admin.scan(name.trim(), domain.trim(), sector)
      setResult({ scan_run_id: data.scan_run_id, org_id: data.org_id, name: data.name, domain: data.domain })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Scan trigger failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl stagger">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={() => navigate('/admin')}
          className="btn-ghost mb-4"
          type="button"
        >
          <ArrowLeft size={13} /> Back to Admin
        </button>
        <div className="eyebrow mb-1">
          <span className="line" />
          <span>module :: admin.scan</span>
        </div>
        <h1 className="display-title text-3xl gradient-text">New Organization Scan</h1>
        <p className="num mt-1 text-[12px] uppercase tracking-[0.14em] text-[var(--text-secondary)]">
          ▸ register an institution and trigger a full external trust assessment
        </p>
      </div>

      <div className="panel-terminal glass-card mb-6">
        <div className="panel-header">
          <div className="flex items-center gap-2">
            <span className="dot dot-cyan" />
            <span>scan --new-org</span>
          </div>
          <span className="num">full.report</span>
        </div>

        <form onSubmit={handleSubmit} className="panel-body space-y-5">
          <div>
            <label className="eyebrow mb-2 block">
              <span className="line" />
              <span>organization.name</span>
            </label>
            <div className="relative">
              <Building2 size={14} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[var(--neon-cyan)]" />
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Bayelle Credit Union"
                className="glass-input num w-full py-3 pl-9 pr-3"
                disabled={loading}
                autoFocus
              />
            </div>
            <p className="num mt-1 text-[11px] text-[var(--text-muted)]">
              The legal/brand name — this is what reports will lead with.
            </p>
          </div>

          <div>
            <label className="eyebrow mb-2 block">
              <span className="line" />
              <span>primary.domain</span>
            </label>
            <div className="relative">
              <Globe size={14} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[var(--neon-cyan)]" />
              <input
                type="text"
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                placeholder="bayellecreditunion.com"
                className="glass-input num w-full py-3 pl-9 pr-3"
                disabled={loading}
              />
            </div>
            <p className="num mt-1 text-[11px] text-[var(--text-muted)]">
              The primary external domain to assess. Lowercased automatically.
            </p>
          </div>

          <div>
            <label className="eyebrow mb-2 block">
              <span className="line" />
              <span>sector.specialization</span>
            </label>
            <div className="relative">
              <Briefcase size={14} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[var(--neon-cyan)]" />
              <select
                value={sector}
                onChange={(e) => setSector(e.target.value)}
                className="glass-input num w-full py-3 pl-9 pr-3 appearance-none"
                disabled={loading}
              >
                {SECTOR_OPTIONS.map((s) => (
                  <option key={s.code} value={s.code}>{s.label}</option>
                ))}
              </select>
            </div>
            <p className="num mt-1 text-[11px] text-[var(--text-muted)]">
              Determines which sector-specific regulations are cited in the report.
            </p>
          </div>

          <button
            type="submit"
            disabled={loading || !name.trim() || !domain.trim()}
            className="btn-gradient w-full"
          >
            {loading ? (
              <>
                <Loader2 className="animate-spin" size={14} /> Scanning…
              </>
            ) : (
              <>
                <Radar size={14} /> Trigger Full Scan
              </>
            )}
          </button>
        </form>
      </div>

      {error && (
        <div
          className="panel mb-6 p-4 flex items-center gap-2 num text-[13px]"
          style={{ borderColor: 'var(--neon-red)', color: 'var(--neon-red)' }}
        >
          <AlertTriangle size={14} /> {error}
        </div>
      )}

      {result && (
        <div
          className="panel-terminal glass-card"
          style={{ borderColor: 'var(--neon-green)' }}
        >
          <div className="panel-header" style={{ borderColor: 'var(--neon-green)' }}>
            <div className="flex items-center gap-2">
              <span className="dot dot-green" />
              <span>scan.queued</span>
            </div>
            <span className="num" style={{ color: 'var(--neon-green)' }}>ok</span>
          </div>
          <div className="panel-body space-y-3">
            <div className="flex items-center gap-2 num text-[13px]" style={{ color: 'var(--neon-green)' }}>
              <ShieldCheck size={14} /> Scan started for {result.name} ({result.domain})
            </div>
            <div className="num text-[12px] text-[var(--text-secondary)]">
              scan_run_id :: {result.scan_run_id}
            </div>
            <div className="flex flex-wrap gap-2 pt-2">
              <button
                onClick={() => navigate(`/dashboard?org_id=${result.org_id}`)}
                className="btn-ghost"
                type="button"
              >
                <Building2 size={13} /> Go to Dashboard
              </button>
              <button
                onClick={() => navigate('/admin')}
                className="btn-ghost"
                type="button"
              >
                Back to Admin
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}