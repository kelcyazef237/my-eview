# Build Prompt: MYEVIEW — Myescore External Trust Intelligence Platform

You are building **MYEVIEW**, a Cameroon-focused external attack-surface and digital-trust scoring platform — think "FICO score, but for an organization's external cybersecurity posture." It passively assesses a domain's email security, infrastructure, threat exposure, and attack surface, converts findings into a single 0–1000 score ("Myescore"), maps it to a 5-tier "Shield" rating, and produces both a public-facing summary and a detailed owner-facing report with plain-language business impact write-ups.

Treat this prompt as the full spec. Where a decision isn't specified, make a sensible default, document the assumption in a `DECISIONS.md` file at the project root, and keep moving — don't stall on ambiguity.

---

## 0. Non-Negotiable Principles

1. **Determinism.** Re-scanning unchanged infrastructure must produce the identical score. Every check returns a discrete state (`PASS / WARN / FAIL / NOT_APPLICABLE / NOT_OBSERVED`) before it touches the scoring engine — never raw continuous values. The scoring engine itself is a pure function: `score = f(findings, ruleset_version)`, no hidden state, no live calls, no randomness.
2. **Non-intrusive only.** Every collector either reads already-public data (DNS, WHOIS, CT logs, threat-intel feeds) or performs a standard protocol handshake any browser/client would perform (TLS handshake, HTTP GET, DNS query). No exploitation, no login attempts, no payload injection. A separate, explicitly gated "light port-touch" collector (TCP-connect only, curated port list, banner read only) is permitted **only** for organizations that have completed an authorization flag — never run by default.
3. **No heavy paid-API dependency.** Default to direct, self-collected checks (DNS, TLS, HTTP, WHOIS) over third-party indexed data (Shodan/Censys) wherever a direct check is feasible — it's faster, free, and more current. Threat-intelligence vectors (malware/phishing/spam/botnet) are the one place external feeds are unavoidable; use free-tier feeds and cache them locally on a schedule rather than hitting them per-scan.
4. **Customer never sees a "vector."** They see a category-level finding with a plain-English write-up. The 24 underlying risk vectors are visible only behind an explicit "Technical View" toggle for users flagged as technical.

---

## 1. Tech Stack

- **Backend:** Python, FastAPI, PostgreSQL, Celery + Redis (scheduled scans), SQLAlchemy + Alembic migrations, Pydantic for config/schema validation
- **Frontend:** Vite + React + TypeScript + Tailwind CSS
- **Report rendering:** Jinja2 templates → HTML (shared between web view and PDF) → WeasyPrint for PDF export
- **Key Python libraries:** `dnspython`, `httpx`, `cryptography`/`ssl`, `python-whois`, `ipwhois`, `beautifulsoup4`, `python-nmap` (for the gated light-scan collector only)

---

## 2. Score Architecture (build exactly as specified)

### 2.1 Categories, Points, Vectors

8 categories, 7 scored (sum to exactly 1000), 1 unscored. Seed these as fixed reference data via migration — never user-editable at runtime.

| # | Category | Points | Vectors (24 total) |
|---|---|---|---|
| 1 | Email Trust & Authentication | 140 | SPF Presence · DKIM Presence · DMARC Presence+Enforcement (combined, graduated) |
| 2 | Digital Identity & Domain Governance | 90 | Domain Age · Domain Expiration Health · DNSSEC Adoption |
| 3 | Infrastructure Security | 180 | TLS Version Strength · Certificate Health · Security Headers · HTTPS Enforcement · Exposed Admin Interfaces |
| 4 | Technology Currency | 90 | Technology Obsolescence · Software Version Currency · Legacy Service Exposure |
| 5 | Threat Intelligence Exposure | 270 | Malware · Phishing · Spam/Blacklist · Botnet · Blacklist Aggregate Count |
| 6 | Asset Visibility & Attack Surface | 140 | Internet-Facing Asset Count · Shadow Asset Discovery · Unmanaged Asset Indicators |
| 7 | Ecosystem Trust (Third-Party Dependency) | 90 | Subresource Integrity (SRI) Adoption |
| 8 | Entity Intelligence (not scored, displayed separately) | 0 | Related Domains · Shared Infrastructure · Parent/Subsidiary · Brand-Related Assets |

Categories 1–2 together = "Digital Identity" (230 pts). Categories 3–4 together = "Infrastructure Security" (270 pts). This sub-grouping matters for the customer-facing summary view (show the parent grouping + the child finding).

### 2.2 Worked Scoring Examples (use as the template for the rest)

**Email Trust & Authentication (140 pts):**
- SPF Presence: 30 pts — present → 0 / absent → −30
- DKIM Presence: 30 pts — present → 0 / absent → −30
- DMARC Presence + Enforcement (combined, graduated): 80 pts
  - `p=reject` → 0
  - `p=quarantine` → −30
  - `p=none` → −60
  - absent entirely → −80

**Threat Intelligence Exposure (270 pts):**
- Malware: 60 pts — none → 0 / historical(>6mo) → −20 / active → −60
- Phishing: 60 pts — none → 0 / historical → −20 / active → −60
- Spam/DNSBL listing: 55 pts — none → 0 / 1 list → −20 / 2+ lists → −55
- Botnet C2: 65 pts — none → 0 / historical → −25 / active → −65 (weighted highest — most severe finding type)
- Blacklist aggregate count: 30 pts — 0–1 listing → 0 / 2–3 → −15 / 4+ → −30

**Your task:** design the remaining graduated tiers for all other vectors following this exact pattern (PASS=0, WARN=partial deduction, FAIL=full vector-budget deduction; sub-vector points within a category must sum exactly to that category's total). Output the complete ruleset as `backend/config/scoring_rules_v1.yaml`. Validate programmatically on startup that all category point sums equal their declared totals and that all 7 scored categories sum to exactly 1000.

### 2.3 Formula

```
category_score = max(0, category_points_total − Σ(vector deductions in that category))
overall_score  = Σ(category_score) across the 7 scored categories
```

- `NOT_OBSERVED` (check failed to run — timeout, feed down) is never silently scored as pass or fail. If more than ~15% of a run's vectors come back `NOT_OBSERVED`, mark the whole run `INCOMPLETE` — do not publish a new score from it, retry instead.
- A category's deduction cannot exceed its own points_total (floor at 0); categories cannot borrow from each other.

### 2.4 Shield Tiers

| Shield | Score Range | Band Label |
|---|---|---|
| I | 0–399 | Foundational Digital Trust |
| II | 400–599 | Developing Digital Trust |
| III | 600–749 | Above Average Digital Trust |
| IV | 750–899 | Strong Digital Trust |
| V | 900–1000 | Exemplary Digital Trust |

Shield visual = N shield marks rendered for tier N (Shield III shows 3 marks, etc.) — implement this as a reusable component, not hardcoded per tier.

### 2.5 Trust Outlook (momentum signal)

- Default outlook per tier: V→"Positive · Stable", IV→"Positive", III→"Stable · Improving", II→"Stable · Watch", I→"Negative · Action Required".
- **Override rule:** compare current score only against the previous **Full Report** snapshot (a formal monthly snapshot), not every background monitoring scan. If delta ≥ +20 → outlook = "Positive" regardless of tier. If delta ≤ −30 → outlook = "Watch" or "Negative" depending on resulting tier.
- First-ever Full Report for an org → outlook = "Baseline · Insufficient History".
- Run lightweight monitoring scans on a separate, more frequent schedule (e.g. weekly) for internal alerting/freshness, but only formal Full Report snapshots (e.g. monthly) feed the outlook comparison and get rendered as the customer-facing report.

---

## 3. Data Collection — Implementation per Vector

Implement each as an independent, async-callable collector module under `backend/collectors/`. All collectors for a single domain should run concurrently (`asyncio.gather`), except the gated light-scan collector, which runs in its own Celery queue so it never blocks the fast passive checks.

| Vector(s) | Method | Library |
|---|---|---|
| SPF / DKIM / DMARC | DNS TXT query | `dnspython` |
| Domain Age / Expiration | WHOIS/RDAP query | `python-whois` |
| DNSSEC Adoption | DNS RRSIG/DS query | `dnspython` |
| TLS Version / Certificate Health | Direct TLS handshake | `ssl`, `cryptography` |
| Security Headers / HTTPS Enforcement | Direct HTTPS GET, read headers + check for HTTP fallback | `httpx` |
| Exposed Admin Interfaces | HEAD-only request against a small curated path list (`/admin`, `/wp-admin`, `/phpmyadmin`, `/.env`, etc.) | `httpx` |
| Technology Obsolescence / Software Version Currency | Parse `Server` header + HTML generator meta tag from the same GET above | `httpx` + `beautifulsoup4` |
| Legacy Service Exposure | Only in the gated "Verified" tier — light TCP-connect + banner read on a fixed legacy-port subset (21 FTP, 23 Telnet, old SSH) | `python-nmap`, `-sT -T2`, curated ports only |
| Malware | AlienVault OTX API (free key) | `httpx` against OTX REST API |
| Phishing | PhishTank free feed + OpenPhish free feed | `httpx` |
| Spam/Blacklist | DNSBL lookup (reverse-IP query against Spamhaus, SURBL) | `dnspython` |
| Botnet | Abuse.ch Feodo Tracker — download CSV/API on a schedule, cache in `threat_feed_cache` table, check against the **local cache** per scan (no live call per scan) | `httpx` for the periodic refresh task only |
| Asset Visibility (subdomain discovery) | Certificate Transparency logs via crt.sh public JSON endpoint | `httpx` |
| Shadow/Unmanaged Asset Indicators | Re-run the TLS + HTTP collectors against every discovered subdomain; flag cert-issuer mismatch vs primary domain and stale server banners | reuse existing collectors |
| SRI Adoption | Parse the HTML already fetched for the headers check; look for `integrity=` attributes on `<script>`/`<link>` tags | `beautifulsoup4` |
| Entity Intelligence (unscored) | WHOIS registrant correlation + shared ASN/IP lookup for related domains | `ipwhois` |

**Collection-layer reliability rules:**
- Retry up to 3x with backoff on transient network failures before recording a definitive result.
- For flaky checks (script-origin detection, banner reads), require 2-of-3 agreement across repeated fetches within the scan window before finalizing; disagreement → `NOT_OBSERVED`, surfaced for review.
- Run all checks from one fixed outbound IP/region so CDN/WAF geo-routing can't change results between runs.
- Bucket continuous values into the fixed states before scoring (e.g. cert expiry: >90d=PASS, 30–90d=WARN, <30d=FAIL) — never feed raw day-counts into the scorer.

---

## 4. Trust Impact Analysis (TIA) — Deterministic Template Engine

Build `backend/tia/` as a template engine, not free-text generation per report. Each category has versioned templates (`backend/config/tia_templates_v1.yaml`) with 5 fixed slots, populated from the vector states that triggered the finding:

1. **Technical Observation** — one precise sentence, zero jargon, never mentions score impact
2. **Business Impact** — 1–3 paragraphs in plain executive language, templated with variable slots for the specific sub-vector states
3. **Stakeholders Affected** — tags drawn only from the fixed set: Customers, Employees, Business Partners, Regulators
4. **Regulatory Relevance** — soft citation referencing the relevant COBAC/ANTIC/Data Protection Law article, always closing with "regulatory determinations require qualified legal and compliance advisors"
5. **Recommended Action** — one plain, directly executable instruction

**Positive-path requirement:** when a category has no material findings, render a "clean" template variant that explicitly names the controls that are correctly configured and the specific risk that reduces — for at least one representative vector per scored category. Don't just omit the section.

---

## 5. RBAC / View Layers

| Tier | Sees | Unlocked by |
|---|---|---|
| Public / Anonymous | Overall score, Shield tier, trend direction, sector benchmark only | Default, via public lookup page |
| Owner | All 7 category findings + TIA + unscored Entity Intelligence section | Domain ownership verified |
| Owner — Technical View | Everything above + the 24-vector drill-down with raw evidence | Same org, user flagged "technical" role, explicit UI toggle |
| Internal Ops | Everything + raw evidence store, ruleset management, manual re-scan trigger, org administration | Internal staff auth |

**Ownership verification:** implement both DNS TXT challenge (`myeview-verify=<token>` record) and email confirmation (to `admin@`/`security@` at the domain) as verification methods.

**Public lookup abuse protection:** rate-limit scan-triggering on the public page — max one free scan per domain per 30 days, IP-based rate limiting on top of that.

---

## 6. Data Model

```
organizations          id, name, sector, country, primary_domain, ownership_verified, created_at
assets                 id, org_id, type(domain|subdomain|ip), value, discovered_via, first_seen, active
categories             id, name, points_total, scored(bool), parent_group   -- fixed seed data
vectors                id, category_id, name, data_source, collection_method  -- fixed seed data, 24 rows
scan_runs              id, org_id, started_at, finished_at, status, is_full_report(bool), ruleset_version
raw_evidence           id, scan_run_id, asset_id, collector_name, raw_payload(jsonb), fetched_at, attempt_count
vector_findings        id, scan_run_id, asset_id, vector_id, state, evidence_ref
category_scores        id, scan_run_id, category_id, points_lost, points_remaining
tia_entries            id, scan_run_id, category_id, template_id, rendered_text(jsonb)
scores                 id, scan_run_id, org_id, overall_score, shield_tier, outlook, ruleset_version, computed_at
score_history          org_id, scan_run_id, overall_score, is_full_report, computed_at
users                  id, org_id, email, role(public|owner|owner_technical|ops)
ownership_verifications org_id, method(dns_txt|email), token, verified_at
threat_feed_cache      method, source, payload(jsonb), refreshed_at
```

Raw evidence and findings are append-only and immutable per run — never overwritten. This is what makes retroactive ruleset recalculation safe (re-run the pure scoring function over old findings if weights change later).

---

## 7. Frontend — Design Requirements

This product's whole value proposition is "a number a CEO trusts and a regulator can audit." The UI must read as a serious financial/compliance instrument, not a generic SaaS dashboard template. Build with strong intent:

**Light mode is the default and primary design target; dark mode is a full equal-quality second theme**, not an inverted afterthought — design both palettes deliberately, toggle persisted in app state.

**Visual language:**
- Generous whitespace, a clear type hierarchy, restrained color — color is reserved for semantic status only (Shield tier color-coding, PASS/WARN/FAIL states), never decorative.
- One considered sans-serif type family used consistently (e.g. Inter or IBM Plex Sans), with deliberate weight/size scale — avoid default browser/Tailwind defaults applied without a system.
- Shield tier color mapping: I = red/clay, II = amber, III = blue/slate, IV = teal, V = deep green or gold — desaturated, not neon, consistent with a financial-instrument feel.
- The Shield visual (N marks for tier N) and the score itself should be the clear visual anchor of every report view — treat it like a credit-score gauge, not a buried stat.
- Avoid generic shadcn-default look-and-feel applied unmodified; treat any component library as a base to skin, not a finished UI.

**Required views:**
1. **Public Lookup page** — domain search bar, result card showing org name (if known), Shield visual, overall score, trend arrow, sector benchmark category. CTA to request a full assessment if unassessed.
2. **Owner Dashboard** — score history chart, current Shield/Outlook, the 7 category cards (each showing points retained/lost as a progress indicator, customer-facing finding label, expandable TIA panel), separate Entity Intelligence section (visually distinct, "not scored" labeled), "Technical View" toggle (role-gated) that reveals the 24-vector breakdown per category with evidence.
3. **Report / PDF export view** — same content as the Owner Dashboard, rendered for print/PDF via the shared Jinja2 templates, matching the visual system.
4. **Ownership verification flow** — DNS TXT instructions screen with copy-able token + status check, and email-verification alternative.
5. **Org settings / scan history** — list of past Full Report snapshots, manual re-scan trigger (rate-limited), ruleset version shown per historical score.

**Responsiveness:** dashboard must be usable on tablet/mobile — category cards stack, charts resize, Technical View table becomes horizontally scrollable rather than broken.

---

## 8. Backend Structure

```
backend/
  api/                routers: public.py, owner.py, ops.py, auth.py
  collectors/         one module per vector group (dns_collector.py, tls_collector.py, http_collector.py, whois_collector.py, threat_intel_collector.py, asset_discovery.py, portscan_collector.py [gated])
  normalization/       canonicalize_*.py — raw evidence → discrete states
  scoring/             engine.py (pure function), rules_loader.py
  tia/                 template_engine.py
  config/              scoring_rules_v1.yaml, tia_templates_v1.yaml
  models/              SQLAlchemy models matching §6
  tasks/               Celery tasks: run_passive_scan, run_full_report_cycle, refresh_threat_feeds, run_verified_portscan
  reports/             Jinja2 templates + WeasyPrint render pipeline
  tests/               unit tests asserting scoring determinism (same findings in → same score out, every time)
```

---

## 9. Build Order

1. Data model + migrations, seed 8 categories / 24 vectors as fixed reference rows
2. Passive collectors (DNS, WHOIS, TLS, HTTP, CT logs) — covers the majority of vectors
3. Scoring engine + `scoring_rules_v1.yaml`, with a determinism unit test before moving on
4. Shield/Outlook mapper, including the Full-Report-vs-monitoring-scan distinction
5. Threat-feed collectors + local cache refresh task
6. TIA template engine, including positive-path "clean" templates
7. RBAC + ownership verification flow
8. Frontend: public lookup → owner dashboard → technical drill-down → PDF export
9. Gated Verified-tier light port-scan collector (off by default, per-org authorization flag)

---

## 10. Acceptance Checklist

- [ ] Running the same scan twice on unchanged infrastructure produces an identical score
- [ ] All 7 scored category point totals sum to exactly 1000, validated on startup
- [ ] No vector ever appears in the default Owner view without the Technical toggle enabled
- [ ] Public view never exposes findings, only score/tier/trend/benchmark
- [ ] `NOT_OBSERVED` findings never silently count as pass or fail
- [ ] Outlook only changes between Full Report snapshots, never on every background scan
- [ ] No score is published from an `INCOMPLETE` run
- [ ] Light/dark mode both fully styled, not one inverted from the other
- [ ] PDF export visually matches the web report
- [ ] No default collector requires a paid third-party API key to produce a complete score
