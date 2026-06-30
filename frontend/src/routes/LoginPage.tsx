import { useState } from 'react'
import { Link } from 'react-router-dom'
import { LogIn, Loader2, UserCircle, KeyRound, User, ChevronRight, ArrowLeft } from 'lucide-react'
import { api } from '@/api/client'
import { AuthLayout } from '@/components/AuthLayout'

export function LoginPage() {
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const data = await api.login(identifier, password)
      localStorage.setItem('myeview_token', data.access_token)
      const dest =
        data.role === 'global_admin' ? '/admin'
        : data.role === 'owner_technical' ? '/technical'
        : '/dashboard'
      window.location.href = dest
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout
      title="OPERATOR_LOGIN"
      subtitle="Authenticate to access your trust dashboard, deep technical drill-down, and exports."
      icon={<UserCircle className="h-6 w-6" />}
      footer={
        <>
          <span className="num text-[var(--text-muted)]">no.account?</span>{' '}
          <Link to="/register" className="text-[var(--neon-cyan)] hover:underline">
            register.org
          </Link>
        </>
      }
    >
      <div className="panel-terminal glass-card">
        <div className="panel-header">
          <div className="flex items-center gap-2">
            <span className="dot dot-cyan" />
            <span>login.session</span>
          </div>
          <div className="flex items-center gap-2">
            <span>handshake.tls</span>
            <span className="dot dot-green" />
          </div>
        </div>
        <form onSubmit={handleSubmit} className="panel-body space-y-5">
          <div>
            <label className="eyebrow mb-2 block">
              <span className="line" />
              <span>identifier</span>
            </label>
            <div className="relative">
              <User
                size={14}
                className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[var(--neon-cyan)]"
              />
              <input
                type="text"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                placeholder="username / email"
                autoFocus
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
              <KeyRound
                size={14}
                className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[var(--neon-violet)]"
              />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="glass-input num w-full py-3 pl-9 pr-3"
              />
            </div>
          </div>

          {error && (
            <div
              className="rounded-sm border p-3 num text-[12px] uppercase tracking-[0.08em]"
              style={{
                borderColor: 'var(--neon-red)',
                background: 'rgba(255,48,96,0.1)',
                color: 'var(--neon-red)',
              }}
            >
              <span className="prompt-prefix">!</span>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !identifier || !password}
            className="btn-gradient w-full py-3"
          >
            {loading ? (
              <>
                <Loader2 className="animate-spin" size={16} /> Authenticating
              </>
            ) : (
              <>
                <LogIn size={16} /> Execute Login <ChevronRight size={14} />
              </>
            )}
          </button>

          <div className="num text-center text-[10px] uppercase tracking-[0.18em] text-[var(--text-muted)]">
            ▸ token stored locally · session timeout 24h
          </div>
        </form>
      </div>

      <Link
        to="/"
        className="mt-4 inline-flex items-center gap-1.5 text-[12px] text-[var(--text-muted)] hover:text-[var(--neon-cyan)]"
        style={{ fontFamily: 'var(--font-mono)' }}
      >
        <ArrowLeft size={12} /> cd ..
      </Link>
    </AuthLayout>
  )
}
