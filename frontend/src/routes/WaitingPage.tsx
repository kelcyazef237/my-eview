import { Link, useLocation } from 'react-router-dom'
import { Clock, ArrowRight, ShieldCheck } from 'lucide-react'

export function WaitingPage() {
  const location = useLocation()
  const username = (location.state as { username?: string; fullName?: string } | null)?.username
  const fullName = (location.state as { username?: string; fullName?: string } | null)?.fullName

  return (
    <div className="mx-auto flex min-h-[70vh] max-w-lg flex-col items-center justify-center animate-fade-in">
      <div className="glass-card-strong w-full p-8 text-center">
        <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl gradient-surface">
          <Clock className="h-8 w-8 text-[var(--accent)] animate-pulse-soft" />
        </div>

        <h1 className="mb-3 text-2xl font-bold">Awaiting admin validation</h1>
        <p className="mb-6 text-[var(--text-secondary)]">
          {fullName ? `Thank you, ${fullName.split(' ')[0]}.` : 'Thank you.'} Your registration has been received.
          The administrator will review your request and assign you a role
          (owner, owner_technical, or ops). You'll be able to log in once approved.
        </p>

        {username && (
          <div className="mb-6 rounded-xl border border-[var(--glass-border)] bg-[var(--glass-bg)] p-4">
            <p className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">
              Your login username
            </p>
            <p className="mt-1 font-mono text-lg font-semibold text-[var(--accent)]">{username}</p>
            <p className="mt-2 text-xs text-[var(--text-muted)]">
              Save this — you'll use it to log in once your account is approved.
            </p>
          </div>
        )}

        <div className="flex items-center justify-center gap-2 rounded-lg bg-[var(--glass-bg)] p-3 text-sm text-[var(--text-secondary)]">
          <ShieldCheck className="text-[var(--success)]" size={16} />
          No domain verification is required at this stage.
        </div>

        <Link
          to="/login"
          className="mt-6 inline-flex items-center gap-2 rounded-xl px-6 py-3 font-semibold text-white transition-opacity hover:opacity-90"
          style={{ background: 'var(--gradient-accent)' }}
        >
          Go to login <ArrowRight size={16} />
        </Link>
      </div>

      <p className="mt-6 text-center text-sm text-[var(--text-muted)]">
        Didn't mean to register?{' '}
        <Link to="/" className="text-[var(--accent)] hover:underline">
          Back to public lookup
        </Link>
      </p>
    </div>
  )
}