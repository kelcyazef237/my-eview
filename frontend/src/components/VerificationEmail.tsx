import { Mail, Check } from 'lucide-react'

interface VerificationEmailProps {
  email: string
  sent: boolean
  verified: boolean
}

export function VerificationEmail({ email, sent, verified }: VerificationEmailProps) {
  return (
    <div className="glass-card p-5">
      <h3 className="mb-2 text-base font-semibold">Email Verification</h3>
      <p className="mb-4 text-sm text-[var(--text-secondary)]">
        A verification link has been sent to{' '}
        <strong>{email}</strong>. Click the link in that email to confirm ownership.
      </p>

      {sent && !verified && (
        <div className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
          <Mail size={16} /> Verification email sent.
        </div>
      )}

      {verified && (
        <div className="flex items-center gap-2 text-sm font-semibold text-[var(--success)]">
          <Check size={16} /> Verified
        </div>
      )}
    </div>
  )
}
