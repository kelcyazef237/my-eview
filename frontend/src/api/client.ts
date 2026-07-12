import type {
  AdminMetrics,
  AdminOrgPage,
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

  publicStats: () =>
    fetchJson<{ organizations: number; scans: number }>('/public/stats'),

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

  // Reports — short shareable capability links (no JWT in the URL).
  // orgId is appended so a global admin can open any org's report; without it
  // the backend assumes the caller's own org and cross-org reports 404.
  reportHtml: (scanRunId: string, orgId?: string) => {
    const token = localStorage.getItem('myeview_token')
    const qs = new URLSearchParams()
    if (token) qs.set('token', token)
    if (orgId) qs.set('org_id', orgId)
    const q = qs.toString()
    return `${API_BASE}/reports/${scanRunId}${q ? `?${q}` : ''}`
  },
  reportPdf: (scanRunId: string, orgId?: string) => {
    const token = localStorage.getItem('myeview_token')
    const qs = new URLSearchParams()
    if (token) qs.set('token', token)
    if (orgId) qs.set('org_id', orgId)
    const q = qs.toString()
    return `${API_BASE}/reports/${scanRunId}/pdf${q ? `?${q}` : ''}`
  },
  // AI-assisted report views — same template but with AI tier/outlook/narratives/PoCs.
  reportHtmlAI: (scanRunId: string, orgId?: string) => {
    const token = localStorage.getItem('myeview_token')
    const qs = new URLSearchParams()
    if (token) qs.set('token', token)
    if (orgId) qs.set('org_id', orgId)
    const q = qs.toString()
    return `${API_BASE}/reports/${scanRunId}/ai${q ? `?${q}` : ''}`
  },
  reportPdfAI: (scanRunId: string, orgId?: string) => {
    const token = localStorage.getItem('myeview_token')
    const qs = new URLSearchParams()
    if (token) qs.set('token', token)
    if (orgId) qs.set('org_id', orgId)
    const q = qs.toString()
    return `${API_BASE}/reports/${scanRunId}/ai/pdf${q ? `?${q}` : ''}`
  },
  // Mint (or reuse) a short capability share link for a report.
  // Returns a relative path like "/r/<code>" — the frontend builds the full URL.
  shareReport: (scanRunId: string, orgId?: string) => {
    const qs = new URLSearchParams()
    if (orgId) qs.set('org_id', orgId)
    const q = qs.toString()
    return fetchJson<{ code: string; path: string }>(`/reports/${scanRunId}/share${q ? `?${q}` : ''}`, {
      method: 'POST',
    })
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
    orgs: (params?: { q?: string; limit?: number; offset?: number }) => {
      const qs = new URLSearchParams()
      if (params?.q) qs.set('q', params.q)
      if (params?.limit != null) qs.set('limit', String(params.limit))
      if (params?.offset != null) qs.set('offset', String(params.offset))
      const q = qs.toString()
      return fetchJson<AdminOrgPage>(`/admin/orgs${q ? `?${q}` : ''}`)
    },
    scanRuns: () => fetchJson<AdminScanRun[]>('/admin/scan-runs'),
    cleanScanData: (confirm: string) =>
      fetchJson<{ status: string; deleted_organizations: number }>(`/admin/clean-scan-data`, {
        method: 'POST',
        body: JSON.stringify({ confirm }),
      }),
    rescan: (orgId: string) =>
      fetchJson<{ scan_run_id: string; status: string; domain: string }>(`/admin/rescan/${orgId}`, {
        method: 'POST',
      }),
    scan: (name: string, domain: string, sector?: string) =>
      fetchJson<{ scan_run_id: string; status: string; org_id: string; name: string; domain: string; sector: string }>(
        `/admin/scan`,
        { method: 'POST', body: JSON.stringify({ name, domain, sector }) },
      ),
    sectors: () =>
      fetchJson<{ code: string; label: string }[]>('/admin/sectors'),
    getAISettings: () =>
      fetchJson<{ has_key: boolean; api_key_masked: string | null; provider: string; endpoint: string; model: string; providers: string[] }>(
        `/admin/ai-settings`,
      ),
    setAISettings: (api_key: string, provider?: string, endpoint?: string, model?: string) =>
      fetchJson<{ status: string; provider: string; endpoint: string; model: string }>(`/admin/ai-settings`, {
        method: 'POST',
        body: JSON.stringify({ api_key, provider, endpoint, model }),
      }),
    generateAIReport: (scanRunId: string) =>
      fetchJson<{ ai: Record<string, unknown>; provider: { endpoint: string; model: string }; scan_run_id: string }>(
        `/admin/scan-runs/${scanRunId}/ai-report`,
        { method: 'POST' },
      ),
    authorizePortscan: (orgId: string, authorized: boolean) =>
      fetchJson<{ id: string; domain: string; verified_portscan_authorized: boolean }>(
        `/admin/orgs/${orgId}/portscan-auth`,
        { method: 'PATCH', body: JSON.stringify({ authorized }) },
      ),
  },
}
