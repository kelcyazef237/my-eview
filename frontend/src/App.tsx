import { Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { Layout } from '@/components/Layout'
import { PublicLookup } from '@/routes/PublicLookup'
import { LoginPage } from '@/routes/LoginPage'
import { RegisterPage } from '@/routes/RegisterPage'
import { WaitingPage } from '@/routes/WaitingPage'
import { AdminDashboard } from '@/routes/AdminDashboard'
import { OwnerDashboard } from '@/routes/OwnerDashboard'
import { TechnicalDashboard } from '@/routes/TechnicalDashboard'
import { ReportPage } from '@/routes/ReportPage'
import { SettingsPage } from '@/routes/SettingsPage'
import { api } from '@/api/client'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('myeview_token')
  return token ? children : <Navigate to="/login" replace />
}

function RoleRoute({ requiredRole, children }: { requiredRole: string; children: React.ReactNode }) {
  const [state, setState] = useState<'loading' | 'ok' | 'denied'>('loading')
  const navigate = useNavigate()
  const token = localStorage.getItem('myeview_token')

  useEffect(() => {
    if (!token) {
      navigate('/login', { replace: true })
      return
    }
    api.me()
      .then((user) => {
        if (user.role === requiredRole) {
          setState('ok')
        } else {
          navigate(user.role === 'global_admin' ? '/admin' : '/dashboard', { replace: true })
        }
      })
      .catch(() => {
        localStorage.removeItem('myeview_token')
        navigate('/login', { replace: true })
      })
  }, [token, requiredRole, navigate])

  if (state === 'loading') {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-[var(--border-color)] border-t-[var(--accent)]" />
      </div>
    )
  }
  return <>{children}</>
}

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<PublicLookup />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/waiting" element={<WaitingPage />} />
        <Route
          path="/admin"
          element={
            <RoleRoute requiredRole="global_admin">
              <AdminDashboard />
            </RoleRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <OwnerDashboard />
            </PrivateRoute>
          }
        />
        <Route
          path="/technical"
          element={
            <PrivateRoute>
              <TechnicalDashboard />
            </PrivateRoute>
          }
        />
        <Route
          path="/report"
          element={
            <PrivateRoute>
              <ReportPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <PrivateRoute>
              <SettingsPage />
            </PrivateRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  )
}