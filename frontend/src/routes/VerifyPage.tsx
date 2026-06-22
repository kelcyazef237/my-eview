import { useEffect, useState } from 'react'
import { Loader2 } from 'lucide-react'
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
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold">Verify Domain Ownership</h1>

      {status?.ownership_verified && (
        <div className="rounded-lg border border-[var(--success)]/30 bg-[var(--success)]/10 p-4 text-[var(--success)]">
          Ownership verified. {status.just_verified && 'Just verified now.'}
        </div>
      )}

      <div className="glass-card p-5">
        <div className="mb-4">
          <label className="mb-2 block text-sm font-medium">Verification Method</label>
          <select
            value={method}
            onChange={(e) => setMethod(e.target.value as 'dns_txt' | 'email')}
            className="glass-input w-full px-3 py-2"
          >
            <option value="dns_txt">DNS TXT Record</option>
            <option value="email">Email to admin@ / security@</option>
          </select>
        </div>
        <div className="flex gap-2">
          <button
            onClick={start}
            disabled={loading}
            className="flex-1 rounded-lg px-4 py-2 font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
            style={{ background: 'var(--gradient-accent)' }}
          >
            {loading ? <Loader2 className="mx-auto animate-spin" size={18} /> : 'Start Verification'}
          </button>
          <button
            onClick={check}
            disabled={checking}
            className="rounded-lg border border-[var(--glass-border)] px-4 py-2 font-medium transition-colors hover:bg-[var(--glass-bg)] disabled:opacity-50"
          >
            {checking ? <Loader2 className="animate-spin" size={18} /> : 'Check Status'}
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-lg border border-[var(--danger)]/30 bg-[var(--danger)]/10 p-4 text-sm text-[var(--danger)]">
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
