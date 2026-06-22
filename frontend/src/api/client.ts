import type {
  OwnerDashboardData,
  PublicScore,
  ScoreHistoryPoint,
  TechnicalDashboardData,
  User,
  VerificationStatus,
} from '@/types'

const API_BASE = '/api'

async function fetchJson<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('myeview_token')
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((options.headers as Record<string, string>) || {}),
  }
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  })

  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail || `Request failed: ${response.status}`)
  }

  return response.json() as Promise<T>
}

export const api = {
  // Public
  lookupDomain: (domain: string) =>
    fetchJson<PublicScore>(`/public/lookup/${encodeURIComponent(domain)}`),

  triggerLookup: (domain: string) =>
    fetchJson<PublicScore>(`/public/lookup/${encodeURIComponent(domain)}`, {
      method: 'POST',
    }),

  // Auth
  me: () => fetchJson<User>('/auth/me'),
  devLogin: (email: string, role: string, domain?: string) =>
    fetchJson<{ access_token: string }>('/auth/dev-login', {
      method: 'POST',
      body: JSON.stringify({ email, role, domain }),
    }),

  // Owner
  dashboard: () => fetchJson<OwnerDashboardData>('/owner/dashboard'),
  rescan: () =>
    fetchJson<{ scan_run_id: string; status: string }>('/owner/rescan', {
      method: 'POST',
    }),

  // Technical
  technical: () => fetchJson<TechnicalDashboardData>('/owner/technical'),

  // Verification
  startVerification: (method: 'dns_txt' | 'email') =>
    fetchJson<Record<string, string>>('/owner/verify/start', {
      method: 'POST',
      body: JSON.stringify({ method }),
    }),
  verificationStatus: () => fetchJson<VerificationStatus>('/owner/verify/status'),

  // Verified portscan (owner/technical)
  triggerPortscan: () =>
    fetchJson<{ status: string; scan_run_id: string; task_id: string | null }>(
      '/verified/portscan',
      { method: 'POST' },
    ),

  // History
  history: () => fetchJson<ScoreHistoryPoint[]>('/owner/history'),

  // Reports
  reportHtml: (scanRunId: string) => `${API_BASE}/reports/${scanRunId}`,
  reportPdf: (scanRunId: string) => `${API_BASE}/reports/${scanRunId}/pdf`,
}
