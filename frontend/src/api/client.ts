import type {
  AdminMetrics,
  AdminOrg,
  AdminScanRun,
  AdminUser,
  OwnerDashboardData,
  PendingRegistration,
  PublicScore,
  RegistrationResponse,
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
  login: (identifier: string, password: string) =>
    fetchJson<{ access_token: string; role: string; org_id: string | null }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ identifier, password }),
    }),
  register: (full_name: string, organization_domain: string, password: string, password_repeat: string) =>
    fetchJson<RegistrationResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ full_name, organization_domain, password, password_repeat }),
    }),
  devLogin: (email: string, role: string, domain?: string) =>
    fetchJson<{ access_token: string }>('/auth/dev-login', {
      method: 'POST',
      body: JSON.stringify({ email, role, domain }),
    }),
  logout: () => {
    localStorage.removeItem('myeview_token')
    window.location.href = '/'
  },

  // Owner
  dashboard: (orgId?: string) =>
    fetchJson<OwnerDashboardData>(`/owner/dashboard${orgId ? `?org_id=${orgId}` : ''}`),
  rescan: (orgId?: string) =>
    fetchJson<{ scan_run_id: string; status: string }>(`/owner/rescan${orgId ? `?org_id=${orgId}` : ''}`, {
      method: 'POST',
    }),

  // Technical
  technical: (orgId?: string) =>
    fetchJson<TechnicalDashboardData>(`/owner/technical${orgId ? `?org_id=${orgId}` : ''}`),

  // Verification
  startVerification: (method: 'dns_txt' | 'email') =>
    fetchJson<Record<string, string>>('/owner/verify/start', {
      method: 'POST',
      body: JSON.stringify({ method }),
    }),
  verificationStatus: () => fetchJson<VerificationStatus>('/owner/verify/status'),

  // Verified portscan (owner/owner_technical/ops/global_admin)
  triggerPortscan: (orgId?: string) =>
    fetchJson<{ status: string; scan_run_id: string; task_id: string | null }>(
      `/verified/portscan${orgId ? `?org_id=${orgId}` : ''}`,
      { method: 'POST' },
    ),

  // History
  history: (orgId?: string) =>
    fetchJson<ScoreHistoryPoint[]>(`/owner/history${orgId ? `?org_id=${orgId}` : ''}`),

  // Reports — token appended as query param so browser <a>/iframe links work
  reportHtml: (scanRunId: string) => {
    const token = localStorage.getItem('myeview_token')
    return `${API_BASE}/reports/${scanRunId}${token ? `?token=${encodeURIComponent(token)}` : ''}`
  },
  reportPdf: (scanRunId: string) => {
    const token = localStorage.getItem('myeview_token')
    return `${API_BASE}/reports/${scanRunId}/pdf${token ? `?token=${encodeURIComponent(token)}` : ''}`
  },

  // Admin (global_admin only)
  admin: {
    metrics: () => fetchJson<AdminMetrics>('/admin/metrics'),
    registrations: () => fetchJson<PendingRegistration[]>('/admin/registrations'),
    approve: (userId: string, role: string) =>
      fetchJson<{ id: string; username: string; role: string; registration_status: string }>(
        `/admin/registrations/${userId}/approve`,
        { method: 'POST', body: JSON.stringify({ role }) },
      ),
    reject: (userId: string) =>
      fetchJson<{ id: string; registration_status: string }>(`/admin/registrations/${userId}/reject`, {
        method: 'POST',
      }),
    users: (params?: { status?: string; role?: string }) => {
      const qs = new URLSearchParams()
      if (params?.status) qs.set('status_filter', params.status)
      if (params?.role) qs.set('role_filter', params.role)
      const q = qs.toString()
      return fetchJson<AdminUser[]>(`/admin/users${q ? `?${q}` : ''}`)
    },
    updateUser: (userId: string, patch: { is_active?: boolean; role?: string; full_name?: string; username?: string; email?: string }) =>
      fetchJson<{ id: string; role: string; is_active: boolean }>(`/admin/users/${userId}`, {
        method: 'PATCH',
        body: JSON.stringify(patch),
      }),
    deleteUser: (userId: string) =>
      fetchJson<{ id: string; deleted: boolean }>(`/admin/users/${userId}`, {
        method: 'DELETE',
      }),
    orgs: () => fetchJson<AdminOrg[]>('/admin/orgs'),
    scanRuns: () => fetchJson<AdminScanRun[]>('/admin/scan-runs'),
    rescan: (orgId: string) =>
      fetchJson<{ scan_run_id: string; status: string; domain: string }>(`/admin/rescan/${orgId}`, {
        method: 'POST',
      }),
    authorizePortscan: (orgId: string, authorized: boolean) =>
      fetchJson<{ id: string; domain: string; verified_portscan_authorized: boolean }>(
        `/admin/orgs/${orgId}/portscan-auth`,
        { method: 'PATCH', body: JSON.stringify({ authorized }) },
      ),
  },
}
