import { useEffect, useState } from 'react'
import { Loader2, ShieldCheck } from 'lucide-react'
import { api } from '@/api/client'
import { VerificationDNS } from '@/components/VerificationDNS'
import { VerificationEmail } from '@/components/VerificationEmail'

type VerificationStatus = { ownership_verified: boolean; just_verified: boolean }

export function VerifyPage() {
  const [method, setMethod] = useState<'dns_txt' | 'email'>('dns_txt')
  const [instructions, setInstructions] = useState<Record<string, string> | null>(null)
  const [status, setStatus] = useState<VerificationStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [checking, setChecking] = useState(false)
  const [error, setError] = useState('')

  const start = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await api.startVerification(method)
      setInstructions(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Verification start failed')
    } finally {
      setLoading(false)
    }
  }

  const check = async () => {
    setChecking(true)
    try {
      const data = await api.verificationStatus()
      setStatus(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Status check failed')
    } finally {
      setChecking(false)
    }
  }

  useEffect(() => {
    check()
  }, [])

  return (
    <div className="mx-auto max-w-2xl stagger">
      <div className="eyebrow mb-2">
        <span className="line" />
        <span>module :: verify.domain</span>
      </div>
      <h1 className="display-title mb-6 text-3xl gradient-text">
        Verify Domain Ownership
      </h1>

      {status?.ownership_verified && (
        <div
          className="panel mb-6 flex items-center gap-3 p-4"
          style={{ borderColor: 'var(--neon-green)', boxShadow: '0 0 30px rgba(0,255,156,0.15)' }}
        >
          <ShieldCheck size={18} className="text-[var(--neon-green)]" />
          <div className="num text-[13px] text-[var(--neon-green)]">
            <span className="prompt-prefix">{`>`}</span>
            ownership.verified {status.just_verified && '· just now'}
          </div>
        </div>
      )}

      <div className="panel-terminal glass-card mb-6">
        <div className="panel-header">
          <div className="flex items-center gap-2">
            <span className="dot dot-cyan" />
            <span>verify.start</span>
          </div>
          <span>choose.method</span>
        </div>
        <div className="panel-body space-y-4">
          <div>
            <label className="eyebrow mb-2 block">
              <span className="line" />
              <span>method</span>
            </label>
            <select
              value={method}
              onChange={(e) => setMethod(e.target.value as 'dns_txt' | 'email')}
              className="glass-input num w-full px-3 py-2"
            >
              <option value="dns_txt">DNS TXT Record</option>
              <option value="email">Email to admin@ / security@</option>
            </select>
          </div>
          <div className="flex flex-col gap-2 sm:flex-row">
            <button onClick={start} disabled={loading} className="btn-gradient flex-1">
              {loading ? <Loader2 className="animate-spin" size={14} /> : null}
              {loading ? 'Starting' : 'Start Verification'}
            </button>
            <button onClick={check} disabled={checking} className="btn-ghost">
              {checking ? <Loader2 className="animate-spin" size={14} /> : null}
              {checking ? 'Checking' : 'Check Status'}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div
          className="panel mb-6 p-4 num text-[12px] uppercase tracking-[0.12em]"
          style={{
            borderColor: 'var(--neon-red)',
            color: 'var(--neon-red)',
            boxShadow: '0 0 20px rgba(255,48,96,0.15)',
          }}
        >
          <span className="prompt-prefix">!</span>
          {error}
        </div>
      )}

      {instructions && method === 'dns_txt' && (
        <VerificationDNS
          domain={instructions.domain}
          token={instructions.token}
          verified={status?.ownership_verified ?? false}
        />
      )}

      {instructions && method === 'email' && (
        <VerificationEmail
          email={instructions.email}
          sent={true}
          verified={status?.ownership_verified ?? false}
        />
      )}
    </div>
  )
}
