import { Check, Copy } from 'lucide-react'
import { useState } from 'react'

interface VerificationDNSProps {
  domain: string
  token: string
  verified: boolean
}

export function VerificationDNS({ domain, token, verified }: VerificationDNSProps) {
  const [copied, setCopied] = useState(false)
  const record = `myeview-verify=${token}`

  const copy = async () => {
    await navigator.clipboard.writeText(record)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="glass-card p-5">
      <h3 className="mb-2 text-base font-semibold">DNS TXT Verification</h3>
      <p className="mb-4 text-sm text-[var(--text-secondary)]">
        Add the following TXT record to <strong>{domain}</strong>, then click Check Status.
      </p>

      <div className="mb-4 flex items-center justify-between rounded-lg bg-[var(--glass-bg)] p-3 font-mono text-sm">
        <code>{record}</code>
        <button
          onClick={copy}
          className="ml-3 rounded p-1 transition-colors hover:bg-[var(--glass-bg-strong)]"
          aria-label="Copy TXT record"
        >
          {copied ? <Check size={16} /> : <Copy size={16} />}
        </button>
      </div>

      {verified && (
        <div className="flex items-center gap-2 text-sm font-semibold text-[var(--success)]">
          <Check size={16} /> Verified
        </div>
      )}
    </div>
  )
}
