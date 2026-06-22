import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { UserPlus, Loader2, Building2, ArrowLeft } from 'lucide-react'
import { api } from '@/api/client'

export function RegisterPage() {
  const [fullName, setFullName] = useState('')
  const [domain, setDomain] = useState('')
  const [password, setPassword] = useState('')
  const [passwordRepeat, setPasswordRepeat] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const passwordsMatch = password === passwordRepeat
  const canSubmit = fullName.trim() && domain.trim() && password && passwordRepeat && passwordsMatch && password.length >= 8

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!passwordsMatch) {
      setError('Passwords do not match')
      return
    }
    if (password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }
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
    <div className="mx-auto max-w-md animate-fade-in">
      <Link to="/login" className="mb-6 inline-flex items-center gap-1.5 text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)]">
        <ArrowLeft size={16} /> Back to login
      </Link>

      <div className="mb-8 text-center">
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl gradient-surface">
          <UserPlus className="h-7 w-7 text-[var(--accent)]" />
        </div>
        <h1 className="mb-2 text-3xl font-bold">Register your organization</h1>
        <p className="text-[var(--text-secondary)]">
          Sign up with your name and organization's domain. An admin will validate your account and assign a role.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="glass-card space-y-4 p-6">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-[var(--text-secondary)]">
            Full name
          </label>
          <input
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Jane Doe"
            autoFocus
            className="glass-input w-full px-4 py-3"
          />
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-[var(--text-secondary)]">
            Organization domain
          </label>
          <div className="relative">
            <Building2 className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" size={16} />
            <input
              type="text"
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              placeholder="yourcompany.cm"
              className="glass-input w-full px-4 py-3 pl-10"
            />
          </div>
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
          {password && password.length < 8 && (
            <p className="mt-1 text-xs text-[var(--warning)]">At least 8 characters required</p>
          )}
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-[var(--text-secondary)]">
            Repeat password
          </label>
          <input
            type="password"
            value={passwordRepeat}
            onChange={(e) => setPasswordRepeat(e.target.value)}
            placeholder="••••••••"
            className={`glass-input w-full px-4 py-3 ${passwordRepeat && !passwordsMatch ? 'border-[var(--danger)]' : ''}`}
          />
          {passwordRepeat && !passwordsMatch && (
            <p className="mt-1 text-xs text-[var(--danger)]">Passwords do not match</p>
          )}
        </div>

        {error && (
          <div className="rounded-lg border border-[var(--danger)]/30 bg-[var(--danger)]/10 p-3 text-sm text-[var(--danger)]">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !canSubmit}
          className="flex w-full items-center justify-center gap-2 rounded-xl px-6 py-3 font-semibold text-white transition-opacity disabled:opacity-50"
          style={{ background: 'var(--gradient-accent)' }}
        >
          {loading ? <Loader2 className="animate-spin" size={18} /> : <UserPlus size={18} />}
          Submit registration
        </button>
      </form>

      <div className="mt-6 text-center text-sm text-[var(--text-muted)]">
        Already have an account?{' '}
        <Link to="/login" className="text-[var(--accent)] hover:underline">
          Log in
        </Link>
      </div>
    </div>
  )
}