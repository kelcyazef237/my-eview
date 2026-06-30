import { Check, Copy, Terminal, Server } from 'lucide-react'
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
    <div className="panel-terminal glass-card">
      <div className="panel-header">
        <div className="flex items-center gap-2">
          <span className="dot dot-violet" />
          <span>dns.txt.verification</span>
        </div>
        <div className="flex items-center gap-2">
          <Server size={11} className="text-[var(--neon-cyan)]" />
          <span>{domain}</span>
        </div>
      </div>
      <div className="panel-body">
        <h3 className="display-title mb-2 text-[14px] tracking-[0.08em] text-white">
          DNS TXT Verification
        </h3>
        <p className="mb-4 num text-[12px] text-[var(--text-secondary)]">
          ▸ Add the following TXT record to <span className="text-[var(--neon-cyan)]">{domain}</span>, then click <span className="text-[var(--neon-magenta)]">Check Status</span>.
        </p>

        <div className="mb-4 flex items-center justify-between rounded-sm border border-[var(--glass-border-subtle)] bg-black/40 p-3 num text-[12px] text-[var(--neon-green)]">
          <code className="flex-1 break-all">
            <span className="prompt-prefix">$</span> dig +short TXT {domain}{' '}
            <span style={{ color: 'var(--neon-cyan)' }}>| grep</span> "myeview-verify="
          </code>
          <button
            onClick={copy}
            className="ml-3 flex items-center gap-1 rounded-sm border px-2 py-1 text-[10px] uppercase tracking-[0.12em]"
            style={{
              borderColor: copied ? 'var(--neon-green)' : 'var(--neon-cyan)',
              color: copied ? 'var(--neon-green)' : 'var(--neon-cyan)',
            }}
            aria-label="Copy TXT record"
          >
            {copied ? <Check size={11} /> : <Copy size={11} />}
            {copied ? 'copied' : 'copy'}
          </button>
        </div>

        <div className="rounded-sm border border-[var(--glass-border-subtle)] bg-black/40 p-3 num text-[12px]">
          <div className="text-[var(--text-muted)]">record ::</div>
          <div className="mt-1 break-all text-[var(--neon-cyan)]">
            <Terminal size={11} className="mr-1 inline" />
            {record}
          </div>
        </div>

        {verified && (
          <div className="mt-3 flex items-center gap-2 num text-[12px] uppercase tracking-[0.12em] text-[var(--neon-green)]">
            <Check size={14} /> verified.ok
          </div>
        )}
      </div>
    </div>
  )
}
