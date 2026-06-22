export interface PublicScore {
  domain: string
  org_name: string
  overall_score: number
  shield_tier: number
  shield_label: string
  band: string
  outlook: string
  sector_benchmark: number | null
  ruleset_version: string
  computed_at: string
}

export interface CategoryScore {
  category_id: string
  category_key: string
  category_name: string
  points_total: number
  points_lost: number
  points_remaining: number
  parent_group: string | null
}

export interface TiaEntry {
  category_id: string
  category_key: string
  template_id: string
  rendered_text: Record<string, string | string[]>
}

export interface ScoreHistoryPoint {
  scan_run_id: string
  overall_score: number
  is_full_report: boolean
  computed_at: string
}

export interface EntityIntelligence {
  scored: boolean
  label: string
  related_domains: {
    count: number
    items: string[]
  }
  shared_infrastructure: {
    registrar: string | null
    name_servers: string[]
  }
  parent_subsidiary: {
    registrant: string | null
  }
  brand_assets: {
    discovered_via: string
    count: number
  }
}

export interface OwnerDashboardData {
  org: {
    id: string
    name: string
    domain: string
    ownership_verified: boolean
  }
  score: {
    scan_run_id: string
    overall: number
    shield_tier: number
    outlook: string
    computed_at: string
    is_full_report: boolean
  }
  categories: CategoryScore[]
  tia: TiaEntry[]
  history: ScoreHistoryPoint[]
  entity_intelligence: EntityIntelligence
  user_role: string
}

export interface VectorFinding {
  vector_key: string
  vector_name: string
  category_key: string
  state: string
  evidence_ref: string | null
}

export interface TechnicalDashboardData {
  scan_run_id: string
  overall_score: number
  shield_tier: number
  vectors: VectorFinding[]
}

export interface VerificationStatus {
  ownership_verified: boolean
  just_verified: boolean
}

export interface User {
  id: string
  email: string
  role: string
  org_id: string | null
}
