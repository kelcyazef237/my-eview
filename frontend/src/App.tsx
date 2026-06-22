import { Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from '@/components/Layout'
import { PublicLookup } from '@/routes/PublicLookup'
import { LoginPage } from '@/routes/LoginPage'
import { OwnerDashboard } from '@/routes/OwnerDashboard'
import { TechnicalDashboard } from '@/routes/TechnicalDashboard'
import { VerifyPage } from '@/routes/VerifyPage'
import { ReportPage } from '@/routes/ReportPage'
import { SettingsPage } from '@/routes/SettingsPage'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('myeview_token')
  return token ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<PublicLookup />} />
        <Route path="/login" element={<LoginPage />} />
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
          path="/verify"
          element={
            <PrivateRoute>
              <VerifyPage />
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
