import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { UserPlus, Loader2, Building2, ArrowLeft, KeyRound, User, ChevronRight, CheckCircle2 } from 'lucide-react'
import { api } from '@/api/client'
import { AuthLayout } from '@/components/AuthLayout'

export function RegisterPage() {
  const [fullName, setFullName] = useState('')
  const [domain, setDomain] = useState('')
  const [password, setPassword] = useState('')
  const [passwordRepeat, setPasswordRepeat] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const passwordsMatch = password === passwordRepeat
  const canSubmit =
    fullName.trim() &&
    domain.trim() &&
    password &&
    passwordRepeat &&
    passwordsMatch &&
    password.length >= 8

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!passwordsMatch) { setError('Passwords do not match'); return }
    if (password.length < 8) { setError('Password must be at least 8 characters'); return }
    setLoading(true)
    setError('')
    try {
      const res = await api.register(fullName.trim(), domain.trim().toLowerCase(), password, passwordRepeat)
      navigate('/waiting', { state: { username: res.username, fullName: fullName.trim() } })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout
      title="ORG_REGISTRATION"
      subtitle="Provision trust access for your organization. An admin will validate and assign a role."
      icon={<UserPlus className="h-6 w-6" />}
      footer={
        <>
          <span className="num text-[var(--text-muted)]">already.verified?</span>{' '}
          <Link to="/login" className="text-[var(--neon-cyan)] hover:underline">
            operator_login
          </Link>
        </>
      }
    >
      <Link
        to="/login"
        className="mb-4 inline-flex items-center gap-1.5 text-[12px] text-[var(--text-muted)] hover:text-[var(--neon-cyan)]"
        style={{ fontFamily: 'var(--font-mono)' }}
      >
        <ArrowLeft size={12} /> cd .. /login
      </Link>

      <div className="panel-terminal glass-card">
        <div className="panel-header">
          <div className="flex items-center gap-2">
            <span className="dot dot-violet" />
            <span>register.form</span>
          </div>
          <div className="flex items-center gap-2">
            <span>step 1 / 2</span>
          </div>
        </div>
        <form onSubmit={handleSubmit} className="panel-body space-y-5">
          <div>
            <label className="eyebrow mb-2 block">
              <span className="line" />
              <span>full_name</span>
            </label>
            <div className="relative">
              <User size={14} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[var(--neon-cyan)]" />
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Jane Doe"
                autoFocus
                className="glass-input num w-full py-3 pl-9 pr-3"
              />
            </div>
          </div>

          <div>
            <label className="eyebrow mb-2 block">
              <span className="line" />
              <span>organization.domain</span>
            </label>
            <div className="relative">
              <Building2 size={14} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[var(--neon-violet)]" />
              <input
                type="text"
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                placeholder="yourcompany.cm"
                className="glass-input num w-full py-3 pl-9 pr-3"
              />
            </div>
          </div>

          <div>
            <label className="eyebrow mb-2 block">
              <span className="line" />
              <span>passphrase</span>
            </label>
            <div className="relative">
              <KeyRound size={14} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[var(--neon-magenta)]" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="≥ 8 chars"
                className="glass-input num w-full py-3 pl-9 pr-3"
              />
            </div>
            {password && password.length < 8 ? (
              <p className="mt-1 num text-[10px] uppercase tracking-[0.12em]" style={{ color: 'var(--neon-amber)' }}>
                ▸ min.length = 8
              </p>
            ) : password ? (
              <p className="mt-1 num text-[10px] uppercase tracking-[0.12em] text-[var(--neon-green)]">
                <CheckCircle2 size={10} className="mr-1 inline" /> strength.OK
              </p>
            ) : null}
          </div>

          <div>
            <label className="eyebrow mb-2 block">
              <span className="line" />
              <span>passphrase.confirm</span>
            </label>
            <div className="relative">
              <KeyRound size={14} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[var(--neon-magenta)]" />
              <input
                type="password"
                value={passwordRepeat}
                onChange={(e) => setPasswordRepeat(e.target.value)}
                placeholder="••••••••"
                className="glass-input num w-full py-3 pl-9 pr-3"
              />
            </div>
            {passwordRepeat && !passwordsMatch && (
              <p className="mt-1 num text-[10px] uppercase tracking-[0.12em]" style={{ color: 'var(--neon-red)' }}>
                ▸ mismatch
              </p>
            )}
          </div>

          {error && (
            <div
              className="rounded-sm border p-3 num text-[12px] uppercase tracking-[0.08em]"
              style={{
                borderColor: 'var(--neon-red)',
                background: 'rgba(var(--neon-red-rgb),0.1)',
                color: 'var(--neon-red)',
              }}
            >
              <span className="prompt-prefix">!</span>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !canSubmit}
            className="btn-gradient w-full py-3"
          >
            {loading ? (
              <>
                <Loader2 className="animate-spin" size={16} /> Submitting
              </>
            ) : (
              <>
                <UserPlus size={16} /> Submit Registration <ChevronRight size={14} />
              </>
            )}
          </button>

          <div className="num text-center text-[10px] uppercase tracking-[0.18em] text-[var(--text-muted)]">
            ▸ awaiting admin.validation
          </div>
        </form>
      </div>
    </AuthLayout>
  )
}
