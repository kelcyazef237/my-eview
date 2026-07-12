import { Link, useLocation } from 'react-router-dom'
import { Clock, ArrowRight, ShieldCheck, Activity, Loader2 } from 'lucide-react'

export function WaitingPage() {
  const location = useLocation()
  const username = (location.state as { username?: string; fullName?: string } | null)?.username
  const fullName = (location.state as { username?: string; fullName?: string } | null)?.fullName

  return (
    <div className="mx-auto flex min-h-[70vh] max-w-lg flex-col items-center justify-center animate-fade-in">
      <div className="panel-terminal glass-card-hero w-full">
        <div className="panel-header">
          <div className="flex items-center gap-2">
            <span className="dot dot-amber animate-pulse-soft" />
            <span>queue.awaiting</span>
          </div>
          <div className="num text-[var(--neon-amber)]">queue.id :: #01</div>
        </div>

        <div className="panel-body p-8 text-center">
          <div
            className="relative mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-sm"
            style={{
              background: 'var(--gradient-neon-soft)',
              border: '1px solid var(--neon-amber)',
              color: 'var(--neon-amber)',
              boxShadow: '0 0 24px rgba(var(--neon-amber-rgb),0.35)',
            }}
          >
            <Clock className="h-7 w-7 animate-pulse-soft" />
            <span className="absolute -left-1 -top-1 h-3 w-3 border-t border-l border-[var(--neon-amber)]" />
            <span className="absolute -right-1 -bottom-1 h-3 w-3 border-b border-r border-[var(--neon-magenta)]" />
            <Loader2
              size={64}
              className="absolute inset-0 m-auto animate-spin opacity-25"
              style={{ color: 'var(--neon-cyan)' }}
            />
          </div>

          <div className="eyebrow mb-2 justify-center">
            <span className="line" style={{ background: 'linear-gradient(90deg, transparent, var(--neon-amber))' }} />
            <span>status :: pending</span>
            <span className="line" style={{ background: 'linear-gradient(90deg, var(--neon-amber), transparent)' }} />
          </div>
          <h1 className="display-title mb-3 text-2xl gradient-text">
            Awaiting Admin Validation
          </h1>
          <p className="mb-6 text-sm text-[var(--text-secondary)]">
            {fullName ? `Acknowledged, ${fullName.split(' ')[0]}.` : 'Acknowledged.'} Your
            registration is queued. A global admin will assign a role (owner,
            owner_technical, or ops). Login unlocks once approved.
          </p>

          {username && (
            <div className="panel mb-6 p-4">
              <div className="eyebrow mb-2 justify-center">
                <span className="line" />
                <span>your.login.username</span>
              </div>
              <div
                className="num inline-block rounded-sm border px-3 py-1 text-lg font-semibold"
                style={{
                  color: 'var(--neon-cyan)',
                  borderColor: 'var(--neon-cyan)',
                  background: 'rgba(var(--neon-cyan-rgb),0.08)',
                  textShadow: '0 0 8px rgba(var(--neon-cyan-rgb),0.5)',
                }}
              >
                {username}
              </div>
              <div className="mt-3 num text-[10px] uppercase tracking-[0.16em] text-[var(--text-muted)]">
                ▸ save.this — use to log in once approved
              </div>
            </div>
          )}

          <div
            className="mb-6 flex items-center justify-center gap-2 rounded-sm border p-3 num text-[12px] uppercase tracking-[0.12em]"
            style={{
              borderColor: 'var(--neon-green)',
              background: 'rgba(var(--neon-green-rgb),0.08)',
              color: 'var(--neon-green)',
            }}
          >
            <ShieldCheck size={14} /> no domain verification required yet
          </div>

          <Link to="/login" className="btn-gradient">
            <Activity size={14} /> Go To Login <ArrowRight size={14} />
          </Link>
        </div>
      </div>

      <p className="mt-6 text-center text-[12px] text-[var(--text-muted)]" style={{ fontFamily: 'var(--font-mono)' }}>
        ▸ wrong.form?{' '}
        <Link to="/" className="text-[var(--neon-cyan)] hover:underline">
          cd /public.lookup
        </Link>
      </p>
    </div>
  )
}
