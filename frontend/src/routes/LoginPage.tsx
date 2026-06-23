import { useState } from 'react'
import { Link } from 'react-router-dom'
import { LogIn, Loader2, UserCircle } from 'lucide-react'
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
      // Hard navigation: sets the URL AND reloads in one atomic browser action,
      // so there's no race between navigate() and reload() that could bounce
      // back to /login. The RoleRoute on the target page re-checks the token.
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
      title="MYEVIEW Login"
      subtitle="Sign in to access your dashboard, reports, and settings."
      icon={<UserCircle className="h-7 w-7 text-[var(--accent)]" />}
      footer={
        <>
          Want to access your organization's details?{' '}
          <Link to="/register" className="text-[var(--accent)] hover:underline">
            Register here
          </Link>
        </>
      }
    >
      <form onSubmit={handleSubmit} className="glass-card space-y-4 p-6">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-[var(--text-secondary)]">
            Username or Email
          </label>
          <input
            type="text"
            value={identifier}
            onChange={(e) => setIdentifier(e.target.value)}
            placeholder="Kelcy or you@example.com"
            autoFocus
            className="glass-input w-full px-4 py-3"
          />
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-[var(--text-secondary)]">
            Password
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            className="glass-input w-full px-4 py-3"
          />
        </div>

        {error && (
          <div className="rounded-lg border border-[var(--danger)]/30 bg-[var(--danger)]/10 p-3 text-sm text-[var(--danger)]">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !identifier || !password}
          className="flex w-full items-center justify-center gap-2 rounded-xl px-6 py-3 font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
          style={{ background: 'var(--gradient-accent)' }}
        >
          {loading ? <Loader2 className="animate-spin" size={18} /> : <LogIn size={18} />}
          Sign In
        </button>
      </form>
    </AuthLayout>
  )
}