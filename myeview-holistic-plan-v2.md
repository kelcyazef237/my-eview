# MYEVIEW — Holistic Build Plan v2
## Reconciling the Original Architecture with the Myescore Build Specification v1.0

---

## 0. ⚠️ Spec Inconsistency Found — Resolve Before Coding

The Build Specification's category table doesn't sum correctly. Walking through Section I:

| Category | Points | Claimed Weight |
|---|---|---|
| Digital Identity | 250 | 25% |
| Infrastructure Security | 300 | 30% |
| Threat Exposure | 300 | 30% |
| Asset Visibility | 150 | 15% |
| Ecosystem Trust | 100 | 10% |
| **Sum** | **1100** | **110%** |

The document states the total is 1000/100%, but the five line items sum to 1100/110%. This is a drafting error in the source spec, not something in our earlier plan. The relative ranking in the rationale text is internally consistent (Infra Security and Threat Exposure tied for largest, Digital Identity second, Asset Visibility third, Ecosystem Trust smallest) — only the absolute total is off by 100.

**Recommended fix (proportional normalization, preserves the documented ranking):**

| Category | Spec Points | Normalized (v1 default) |
|---|---|---|
| Digital Identity | 250 | **230** |
| Infrastructure Security | 300 | **270** |
| Threat Exposure | 300 | **270** |
| Asset Visibility | 150 | **140** |
| Ecosystem Trust | 100 | **90** |
| **Total** | 1100 | **1000** |

This is a config value (`scoring_rules_v1.yaml`), not a hardcoded constant — easy to revisit once you have real breach-correlation data, exactly as the spec itself says weighting will be recalibrated in future versions. Flag this to whoever owns the spec document; the numbers above are my best-faith reconciliation, not a guess at their "real" intent.

---

## 1. Final Category → Vector Map (with normalized points)

8 categories, 7 scored, 24 vectors total — matching the spec's vector count exactly.

| # | Category | Points | Sub-allocation | Vectors |
|---|---|---|---|---|
| 1 | Email Trust & Authentication | 140 | of Digital Identity (230) | SPF Presence · DKIM Presence · DMARC Presence+Enforcement (combined, graduated) |
| 2 | Digital Identity & Domain Governance | 90 | of Digital Identity (230) | Domain Age · Domain Expiration Health · DNSSEC Adoption |
| 3 | Infrastructure Security | 180 | of Infra Security (270) | TLS Version Strength · Certificate Health · Security Headers · HTTPS Enforcement · Exposed Admin Interfaces |
| 4 | Technology Currency | 90 | of Infra Security (270) | Technology Obsolescence · Software Version Currency · Legacy Service Exposure |
| 5 | Threat Intelligence Exposure | 270 | standalone | Malware · Phishing · Spam/Blacklist · Botnet · Blacklist Aggregate Count |
| 6 | Asset Visibility & Attack Surface | 140 | standalone | Internet-Facing Asset Count · Shadow Asset Discovery · Unmanaged Asset Indicators |
| 7 | Ecosystem Trust (Third-Party Dependency) | 90 | standalone | Subresource Integrity (SRI) Adoption |
| 8 | Entity Intelligence | **0 — not scored** | displayed separately | Related Domains · Shared Infrastructure · Parent/Subsidiary · Brand-Related Assets |

**Worked sub-allocation, Email Trust (140 pts):**
- SPF Presence: 30 (binary — present 0 / absent −30)
- DKIM Presence: 30 (binary — present 0 / absent −30)
- DMARC Presence + Enforcement (combined, graduated): 80
  - `p=reject` → 0
  - `p=quarantine` → −30
  - `p=none` → −60
  - absent entirely → −80

**Worked sub-allocation, Threat Intelligence Exposure (270 pts):**
- Malware: 60 (none 0 / historical(>6mo) −20 / active −60)
- Phishing: 60 (none 0 / historical −20 / active −60)
- Spam/DNSBL listing: 55 (none 0 / 1 list −20 / 2+ lists −55)
- Botnet C2: 65 (none 0 / historical −25 / active −65 — weighted highest per spec's own framing: "most severe finding")
- Blacklist aggregate count: 30 (cross-check signal, 0–1 listing 0 / 2–3 −15 / 4+ −30)

The remaining categories follow the same pattern (PASS / WARN / FAIL tiers, each vector's max deduction proportional to its severity within the category budget). Spell these out fully in `scoring_rules_v1.yaml` during implementation — the Claude Code prompt below instructs the build to do this following the two worked examples as the template.

---

## 2. Data Source Decisions — Realistic, Fast, Not Shodan/Censys-Dependent

The spec lists Censys/Shodan as the canonical source for several vectors (TLS, tech obsolescence, legacy services, admin interfaces). For an MVP that needs to be **fast, reproducible, and not paid-API-dependent**, most of these are better served by direct, self-collected checks — which are also more current than a third party's last crawl. Threat intelligence vectors are the one category where you genuinely can't self-generate the data; those need real feeds, but most have free tiers or are plain DNS lookups.

| Vector | Spec's listed source | Recommended implementation | Why |
|---|---|---|---|
| SPF / DKIM / DMARC | DNS TXT | Direct DNS query (`dnspython`) | Free, ~50ms, no third party needed |
| Domain Age / Expiry | WHOIS/RDAP | Direct WHOIS/RDAP query (`python-whois`) | Free, ~300ms–1s |
| DNSSEC | DNS RRSIG/DS | Direct DNS query (`dnspython`) | Free, instant |
| TLS Version / Cert Health | Censys/Shodan passive banner | **Direct TLS handshake** (`ssl`/`cryptography`) | More current than a cached snapshot; same non-intrusive standing as a browser connecting |
| Security Headers / HTTPS Enforcement | CommonCrawl/Wayback | **Direct HTTPS GET** (`httpx`) | Wayback/CommonCrawl coverage is sparse for smaller Cameroonian institutions and can be months stale — undermines your "same result every scan" goal |
| Exposed Admin Interfaces | CommonCrawl/Shodan indexed paths | Small curated HEAD-only path check (5–8 well-known paths) + Wayback as secondary cross-check | Stays non-intrusive (HEAD only, no auth attempt), but doesn't depend on whether the site happens to be crawled |
| Tech Obsolescence / Legacy Services | Shodan/Censys banner | HTTP `Server` header + generator meta tag from the same fetch above; legacy port confirmation (FTP/Telnet) only in the **authorized "Verified" tier** light port-touch | Avoids per-scan reliance on a paid API; legacy-port detection genuinely needs a light active check, gated to consented clients |
| Malware | AlienVault OTX / VirusTotal | AlienVault OTX (free API key, generous limits) | Free tier sufficient at MVP scale |
| Phishing | PhishTank / OpenPhish | PhishTank (free, no key) + OpenPhish free feed | Free |
| Spam / Blacklist | Spamhaus / SURBL / MXToolbox | **DNSBL lookup** (reverse-IP DNS query against Spamhaus/SURBL) | This is literally a DNS query — free, ~50ms, no API key, the fastest item in the whole pipeline |
| Botnet | Abuse.ch Feodo Tracker | Download Feodo's free CSV/API list on a schedule (e.g. hourly), cache locally, check each scan against the **local cache** | Per-scan check becomes a local lookup, not a live external call — major speed win |
| Asset Visibility (subdomains) | CT logs / Censys | crt.sh (free, public CT log query) | Already planned, no change |
| Shadow/Unmanaged Asset Indicators | Censys/Shodan + Wayback | Re-run your **own** TLS+HTTP collectors against every discovered subdomain; compare cert issuer & server banner against the primary domain's | Fully self-sufficient, no third party |
| SRI Adoption | CommonCrawl/Wayback HTML | Parse the HTML you already fetched for the headers check (`beautifulsoup4`) | Free, reuses an existing fetch, more current |

**Net effect:** Shodan/Censys become optional enrichment/cross-validation, not a dependency. The only paid-API surface area left is AlienVault OTX (free tier works fine at this scale) and the legacy-port check (gated to consenting "Verified" clients, using your own light scanner, not a third party).

---

## 3. Scoring Formula

```
category_score = max(0, category_points_total − Σ(vector deductions in that category))
overall_score  = Σ(category_score) across the 7 scored categories   # 0–1000
```

- Each vector returns a discrete state (PASS / WARN / FAIL / NOT_APPLICABLE / NOT_OBSERVED) — never raw continuous data straight into scoring.
- `NOT_OBSERVED` (check couldn't run — timeout, feed unavailable) never silently scores as pass or fail. If too many vectors in a run are `NOT_OBSERVED`, the run is marked `INCOMPLETE` and not published as a new score.
- Deductions are capped per category (a category can't go below 0, and can't "borrow" against another category).
- Entity Intelligence (category 8) never contributes a number — displayed qualitatively only, exactly as the spec requires.

---

## 4. Shield Tier & Trust Outlook

Direct from spec, deterministic range lookup:

| Shield | Score Range | Band |
|---|---|---|
| I | 0–399 | Foundational Digital Trust |
| II | 400–599 | Developing Digital Trust |
| III | 600–749 | Above Average Digital Trust |
| IV | 750–899 | Strong Digital Trust |
| V | 900–1000 | Exemplary Digital Trust |

**Trust Outlook (momentum signal):**
- Each Shield tier has a *default* outlook label (V→Positive-Stable, IV→Positive, III→Stable-Improving, II→Stable-Watch, I→Negative-Action Required).
- This default is **overridden** by momentum: if score has risen ≥20 pts since the previous **full report cycle** → outlook = Positive, regardless of tier. If it has dropped ≥30 pts → outlook = Watch/Negative.
- **Important distinction to build in:** "previous full report" ≠ every background re-scan. Run lightweight monitoring scans frequently (e.g. weekly, for internal freshness/alerting) but only compare momentum across formal **Full Report snapshots** (e.g. monthly). Comparing against every minor scan would make the outlook flap noisily — exactly the inconsistency problem you were trying to avoid.
- First-ever scan for an org has no prior cycle to compare against — outlook shows as "Baseline — Insufficient History" rather than guessing.

---

## 5. Trust Impact Analysis (TIA) Subsystem

Build this as a **deterministic template engine**, not free-form generation per report — this is what keeps "same finding → same wording" true on every re-scan, and matches the spec's requirement that score impact is never disclosed in the TIA text.

Each TIA template has 5 fixed slots, filled from the vector states that triggered it:
1. **Technical Observation** — one precise sentence, no jargon, no score reference
2. **Business Impact** — 1–3 paragraphs, template per finding type with variable slots for the specific sub-vector states
3. **Stakeholders Affected** — always drawn from the fixed set {Customers, Employees, Business Partners, Regulators}
4. **Regulatory Relevance** — soft citation referencing COBAC/ANTIC/Data Protection Law articles relevant to that category, always with the "consult qualified advisors" caveat
5. **Recommended Action** — one plain, executable instruction

**Positive-path requirement (from spec Section V, NB):** when a category has no material findings, generate a TIA-style entry that explicitly calls out which controls are correctly configured and what risk that reduces — for a curated subset of vectors, not all 24. This needs its own template variant per category (a "clean" template), not just silence.

Store TIA templates versioned alongside the scoring ruleset (`tia_templates_v1.yaml`), keyed by category + finding-state combination, so output is reproducible and auditable.

---

## 6. View Layers / RBAC

Three tiers, matching the spec's explicit visibility split:

| Tier | Sees | Trigger |
|---|---|---|
| **Public / Anonymous** | Overall score, Shield tier, trend direction, sector benchmark — nothing else | Anyone, via public domain-lookup page |
| **Owner / Customer** | All 7 scored category findings + TIA + unscored Entity Intelligence section. Vectors hidden by default. | Domain ownership verified (DNS TXT token or admin-email confirmation) |
| **Owner / Technical** | Everything above + raw 24-vector drill-down with evidence | Same org, user explicitly flagged "technical" role, toggles "Technical View" |
| **Internal Ops (Myeview staff)** | Everything + raw evidence store, scoring ruleset management, re-scan triggers, org account admin | Internal auth |

**Ownership verification** (needed before unlocking the Owner tier): DNS TXT record challenge (`myeview-verify=<token>`) or confirmation email to a role address at the domain (`admin@`, `security@`). Either is standard, low-friction, and defensible.

**Public lookup page abuse protection:** the public page can trigger a real scan job for an unassessed domain — rate-limit per IP and per domain (e.g., one free scan per domain per 30 days) to prevent it being used as a scanning-as-a-service proxy.

---

## 7. Updated Architecture

```
┌────────────────────────┐
│   Public Lookup Page     │── overall score / tier / trend only
└─────────────┬────────────┘
              │
┌─────────────▼──────────────────────────────────────────┐
│                      API Layer (FastAPI)                  │
│  RBAC-gated routes: public / owner / owner-technical / ops  │
└─────────────┬────────────────────────────────────────────┘
              │
┌─────────────▼───────────────┐
│   Orchestrator (Celery beat)  │  schedules: weekly monitoring scans,
│                                 │  monthly "Full Report" snapshot,
│                                 │  hourly threat-feed cache refresh
└──┬──────┬──────┬──────┬──────┘
   │      │      │      │
┌──▼──┐ ┌─▼───┐ ┌▼────┐ ┌▼──────────┐
│ DNS/ │ │ TLS/│ │HTTP/│ │ Threat-feed│
│WHOIS │ │Cert │ │HTML │ │ local cache│
│      │ │     │ │     │ │ (OTX,      │
│      │ │     │ │     │ │ PhishTank, │
│      │ │     │ │     │ │ DNSBL,     │
│      │ │     │ │     │ │ Feodo)     │
└──┬───┘ └─┬───┘ └┬────┘ └─────┬──────┘
   └───────┴───────┴───────────┘
              │
   ┌──────────▼───────────┐
   │  Raw Evidence Store    │  immutable, per scan_run
   │  (Postgres JSONB)       │
   └──────────┬────────────┘
              │
   ┌──────────▼───────────┐
   │ Normalization Layer    │  → PASS/FAIL/WARN/NA/NOT_OBSERVED
   └──────────┬────────────┘
              │
   ┌──────────▼───────────┐
   │ Vector Engine          │  24 vectors → discrete states
   └──────────┬────────────┘
              │
   ┌──────────▼───────────┐
   │ Category Aggregator    │  7 scored categories, capped deductions
   └──────────┬────────────┘
              │
   ┌──────────▼───────────┐
   │ Shield / Outlook Mapper │  range lookup + momentum vs prior Full Report
   └──────────┬────────────┘
              │
   ┌──────────▼───────────┐
   │ TIA Generator           │  deterministic templates, versioned
   └──────────┬────────────┘
              │
   ┌──────────▼───────────┐
   │ Report Renderer         │  Jinja2 → web view + PDF (WeasyPrint)
   └────────────────────────┘
```

---

## 8. Data Model Additions (on top of the original plan)

```
categories        id, name, points_total, scored (bool)
vectors           id, category_id, name, data_source, collection_method
vector_findings   scan_run_id, asset_id, vector_id, state, evidence_ref
category_scores   scan_run_id, category_id, points_lost, points_remaining
tia_entries       scan_run_id, category_id, template_id, rendered_text(jsonb)
scores            scan_run_id, org_id, overall_score, shield_tier, outlook,
                   is_full_report (bool), ruleset_version
score_history     org_id, scan_run_id, overall_score, is_full_report, computed_at
orgs              id, name, sector, primary_domain, ownership_verified (bool)
users             id, org_id, role (public|owner|owner_technical|ops)
ownership_verifications  org_id, method (dns_txt|email), token, verified_at
threat_feed_cache method, source, payload, refreshed_at
```

---

## 9. Realistic Build Phases

1. **Data model** — seed the fixed 8 categories / 24 vectors as reference data (never user-editable in the app, only via versioned migration)
2. **Passive collectors** — DNS, WHOIS, TLS, HTTP, CT logs → covers ~17 of 24 vectors
3. **Threat-feed integrations + local cache** — OTX, PhishTank, DNSBL, Feodo Tracker → covers Threat Exposure category
4. **Scoring engine** — pure function over normalized findings, `scoring_rules_v1.yaml`, unit-tested for determinism (same input → same output, always)
5. **Shield/Outlook mapper** — including the Full-Report-vs-monitoring-scan distinction
6. **TIA template engine** — including the "clean controls" positive-path templates
7. **RBAC + ownership verification**
8. **Frontend** — public lookup, owner dashboard, technical drill-down, PDF export
9. **Verified tier (later)** — authorized light port-touch for legacy-service confirmation; Entity Intelligence automation (typosquat detection, ASN co-tenancy)
