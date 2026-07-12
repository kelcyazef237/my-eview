import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Download, Loader2, Gauge, Shield as ShieldIcon, TrendingUp, TrendingDown, Minus, FileText, Link as LinkIcon, Check, Sparkles } from 'lucide-react'
import { api } from '@/api/client'
import { CategoryBreakdown } from '@/components/CategoryBreakdown'
import { OrgSelector } from '@/components/OrgSelector'
import { ScoreGauge } from '@/components/ScoreGauge'
import { ScoreHistoryChart } from '@/components/ScoreHistoryChart'
import type { OwnerDashboardData, ScoreHistoryPoint } from '@/types'

const tierNames: Record<number, string> = {
  1: 'Critical',
  2: 'Elevated',
  3: 'Moderate',
  4: 'Strong',
  5: 'Exceptional',
}

function outlookIcon(outlook: string) {
  const lower = outlook.toLowerCase()
  if (lower.includes('positive') || lower.includes('improv')) return TrendingUp
  if (lower.includes('negative') || lower.includes('declin')) return TrendingDown
  return Minus
}

export function ReportPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const orgId = searchParams.get('org_id') || undefined

  const handleSelectOrg = (id: string) => {
    const next = new URLSearchParams(searchParams)
    next.set('org_id', id)
    setSearchParams(next)
  }
  const [data, setData] = useState<OwnerDashboardData | null>(null)
  const [history, setHistory] = useState<ScoreHistoryPoint[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [reportHtmlUrl, setReportHtmlUrl] = useState<string | null>(null)
  const [reportPdfUrl, setReportPdfUrl] = useState<string | null>(null)
  const [reportAiHtmlUrl, setReportAiHtmlUrl] = useState<string | null>(null)
  const [reportAiPdfUrl, setReportAiPdfUrl] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    Promise.all([api.dashboard(orgId), api.history(orgId)])
      .then(([dash, hist]) => {
        setData(dash)
        setHistory(hist)
      })
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load report'))
      .finally(() => setLoading(false))
  }, [orgId])

  // Build the report view URLs. Prefer a short capability share link (no JWT in the
  // URL, safe to copy/share); fall back to the long token-bearing URL if share
  // minting is unavailable. orgId is passed so a global admin can view any org.
  const scanRunId = data?.score.scan_run_id
  useEffect(() => {
    setReportHtmlUrl(null)
    setReportPdfUrl(null)
    setReportAiHtmlUrl(null)
    setReportAiPdfUrl(null)
    if (!scanRunId) return
    let cancelled = false
    api
      .shareReport(scanRunId, orgId)
      .then((res) => {
        if (cancelled) return
        const base = `${window.location.origin}${res.path}`
        setReportHtmlUrl(base)
        setReportPdfUrl(`${base}/pdf`)
      })
      .catch(() => {
        if (cancelled) return
        setReportHtmlUrl(`${window.location.origin}${api.reportHtml(scanRunId, orgId)}`)
        setReportPdfUrl(`${window.location.origin}${api.reportPdf(scanRunId, orgId)}`)
      })
    // AI report URLs always use the authenticated path (no share link for AI)
    setReportAiHtmlUrl(`${window.location.origin}${api.reportHtmlAI(scanRunId, orgId)}`)
    setReportAiPdfUrl(`${window.location.origin}${api.reportPdfAI(scanRunId, orgId)}`)
    return () => {
      cancelled = true
    }
  }, [scanRunId, orgId])

  async function copyShareLink() {
    if (!reportHtmlUrl) return
    try {
      await navigator.clipboard.writeText(reportHtmlUrl)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // Clipboard may be unavailable; the link is still visible via the Web View href.
    }
  }

  if (loading) {
    return (
      <div className="flex h-64 flex-col items-center justify-center gap-3 num text-[var(--text-muted)]">
        <Loader2 className="animate-spin text-[var(--neon-cyan)]" size={32} />
        <span className="text-[11px] uppercase tracking-[0.24em]">
          ▸ compiling.report
          <span className="caret" />
        </span>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div
        className="panel p-6 num text-[12px] uppercase tracking-[0.12em]"
        style={{ borderColor: 'var(--neon-red)', color: 'var(--neon-red)' }}
      >
        <span className="prompt-prefix">!</span>
        {error || 'no.report.data'}
      </div>
    )
  }

  const totalPointsLost = data.categories.reduce((sum, c) => sum + c.points_lost, 0)
  const OutlookIcon = outlookIcon(data.score.outlook)
  const tierColor = ['var(--neon-red)', 'var(--neon-amber)', 'var(--neon-cyan)', 'var(--neon-green)', 'var(--neon-violet)'][Math.max(0, data.score.shield_tier - 1)] || 'var(--text-muted)'

  const shareHref = reportHtmlUrl ?? '#'
  const pdfHref = reportPdfUrl ?? '#'

  return (
    <div className="space-y-8 stagger">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="eyebrow mb-1">
            <span className="line" />
            <span>module :: report.center</span>
          </div>
          <h1 className="display-title text-3xl gradient-text">Report Center</h1>
          <p className="num mt-1 text-[12px] uppercase tracking-[0.14em] text-[var(--text-secondary)]">
            ▸ {data.org.name} <span className="text-[var(--neon-magenta)]">·</span> {data.org.domain}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <OrgSelector orgId={orgId} onSelect={handleSelectOrg} />
          <button
            type="button"
            onClick={copyShareLink}
            disabled={!reportHtmlUrl}
            className="btn-ghost"
            title={reportHtmlUrl ?? 'Generating link…'}
          >
            {copied ? <Check size={13} /> : <LinkIcon size={13} />} {copied ? 'Copied' : 'Copy Link'}
          </button>
          <a
            href={shareHref}
            target="_blank"
            rel="noreferrer"
            className="btn-ghost"
          >
            <FileText size={13} /> Web View
          </a>
          <a
            href={pdfHref}
            className="btn-gradient"
          >
            <Download size={13} /> PDF
          </a>
          {reportAiHtmlUrl && (
            <a
              href={reportAiHtmlUrl}
              target="_blank"
              rel="noreferrer"
              className="btn-ghost"
              style={{ borderColor: 'var(--neon-violet)', color: 'var(--neon-violet)' }}
              title="AI-assisted report with PoCs and scan quality analysis"
            >
              <Sparkles size={13} /> AI View
            </a>
          )}
          {reportAiPdfUrl && (
            <a
              href={reportAiPdfUrl}
              className="btn-ghost"
              style={{ borderColor: 'var(--neon-violet)', color: 'var(--neon-violet)' }}
              title="AI-assisted PDF report"
            >
              <Download size={13} /> AI PDF
            </a>
          )}
        </div>
      </div>

      <ScoreGauge
        score={data.score.overall}
        tier={data.score.shield_tier}
        label={data.score.outlook}
        outlook={data.score.outlook}
        pointsLost={totalPointsLost}
        categoryCount={data.categories.length}
        sectorBenchmark={undefined}
      />

      {history.length > 0 && <ScoreHistoryChart data={history} />}

      <CategoryBreakdown categories={data.categories} defaultView="radar" />

      <div className="grid gap-4 sm:grid-cols-3 stagger">
        <Snapshot
          icon={Gauge}
          color="var(--neon-cyan)"
          label="score"
          value={
            <div className="num text-3xl font-bold glitch" data-text={String(data.score.overall)} style={{ color: 'var(--neon-cyan)', textShadow: '0 0 12px rgba(var(--neon-cyan-rgb),0.5)' }}>
              {data.score.overall}
              <span className="ml-1 text-[12px] text-[var(--text-muted)]"> / 1000</span>
            </div>
          }
        />
        <Snapshot
          icon={ShieldIcon}
          color={tierColor}
          label="shield.tier"
          value={
            <div className="num text-3xl font-bold glitch" data-text={String(data.score.shield_tier)} style={{ color: tierColor, textShadow: `0 0 12px ${tierColor}` }}>
              {data.score.shield_tier}
              <span className="ml-2 text-[12px] text-[var(--text-muted)]"> · {tierNames[data.score.shield_tier] || '—'}</span>
            </div>
          }
        />
        <Snapshot
          icon={OutlookIcon}
          color="var(--neon-green)"
          label="outlook"
          value={
            <div className="num text-lg font-semibold" style={{ color: 'var(--neon-green)' }}>
              {data.score.outlook}
            </div>
          }
        />
      </div>
    </div>
  )
}

function Snapshot({
  icon: Icon,
  color,
  label,
  value,
}: {
  icon: React.ElementType
  color: string
  label: string
  value: React.ReactNode
}) {
  return (
    <div className="panel glass-card-hover p-5">
      <div className="flex items-center gap-4">
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
        <div>
          <div className="eyebrow">{label}</div>
          <div className="mt-1">{value}</div>
        </div>
      </div>
    </div>
  )
}
