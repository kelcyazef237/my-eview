import { Mail, Check, Terminal } from 'lucide-react'

interface VerificationEmailProps {
  email: string
  sent: boolean
  verified: boolean
}

export function VerificationEmail({ email, sent, verified }: VerificationEmailProps) {
  return (
    <div className="panel-terminal glass-card">
      <div className="panel-header">
        <div className="flex items-center gap-2">
          <span className="dot dot-magenta" />
          <span>email.verification</span>
        </div>
        <span>{email}</span>
      </div>
      <div className="panel-body">
        <h3 className="display-title mb-2 text-[14px] tracking-[0.08em] text-[var(--text-primary)]">
          Email Verification
        </h3>
        <p className="mb-4 num text-[12px] text-[var(--text-secondary)]">
          ▸ A verification link has been sent to{' '}
          <span className="text-[var(--neon-cyan)]">{email}</span>. Click the link in that email to confirm ownership.
        </p>

        <div className="rounded-sm border border-[var(--glass-border-subtle)] terminal-surface p-3 num text-[12px]">
          <div className="text-[var(--neon-magenta)]">
            <Terminal size={11} className="mr-1 inline" />
            mail.queue.status :: {sent ? 'sent' : 'pending'}
          </div>
        </div>

        {sent && !verified && (
          <div className="mt-3 flex items-center gap-2 num text-[12px] uppercase tracking-[0.12em] text-[var(--text-secondary)]">
            <Mail size={13} /> verification email sent
          </div>
        )}

        {verified && (
          <div className="mt-3 flex items-center gap-2 num text-[12px] uppercase tracking-[0.12em] text-[var(--neon-green)]">
            <Check size={14} /> verified.ok
          </div>
        )}
      </div>
    </div>
  )
}
